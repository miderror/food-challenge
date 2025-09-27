import asyncio
import logging
from datetime import timedelta

from aiogram import Bot
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import User

logger = logging.getLogger(__name__)


@shared_task
def send_challenge_results_task(user_id: int):
    asyncio.run(send_results_async(user_id))


async def send_results_async(user_id: int):
    try:
        user = await User.objects.aget(telegram_id=user_id)
        bot = Bot(token=settings.BOT_TOKEN)

        days_spent = (user.challenge_end_date - user.date_joined).days + 1

        if user.challenge_status == User.ChallengeStatus.COMPLETED:
            text = (
                f"🎉 Поздравляем!\n\n"
                f"Вы успешно завершили челлендж «400 продуктов»!\n\n"
                f"📊 Ваши результаты:\n"
                f"✅ Съедено продуктов: {user.final_eaten_count}\n"
                f"⏱️ Времени затрачено: {days_spent} дней\n\n"
                f"Это потрясающее достижение! Вы значительно расширили свой рацион. Так держать!"
            )
        elif user.challenge_status == User.ChallengeStatus.EXPIRED:
            text = (
                f"🏁 Челлендж «400 продуктов» завершен!\n\n"
                f"Прошел год с момента вашей регистрации. Время подвести итоги.\n\n"
                f"📊 Ваши результаты:\n"
                f"✅ Съедено продуктов: {user.final_eaten_count} из 400\n"
                f"⏱️ Времени затрачено: 365 дней\n\n"
                f"Отличная работа! Даже если цель не достигнута, вы попробовали много нового. Надеемся, это было полезно!"
            )
        else:
            return

        await bot.send_message(user.telegram_id, text)
        await bot.session.close()
        logger.info(f"Результаты челленджа отправлены пользователю {user_id}")

    except User.DoesNotExist:
        logger.error(f"Не найден пользователь с ID {user_id} для отправки результатов.")
    except Exception as e:
        logger.exception(
            f"Ошибка при отправке результатов челленджа пользователю {user_id}: {e}"
        )


@shared_task
def check_expired_challenges():
    CHALLENGE_DURATION_DAYS = 365
    expiration_date = timezone.now() - timedelta(days=CHALLENGE_DURATION_DAYS)

    expired_users = User.objects.filter(
        challenge_status=User.ChallengeStatus.ACTIVE, date_joined__lte=expiration_date
    )

    for user in expired_users:
        eaten_count = user.eaten_products.count()
        user.challenge_status = User.ChallengeStatus.EXPIRED
        user.challenge_end_date = user.date_joined + timedelta(
            days=CHALLENGE_DURATION_DAYS
        )
        user.final_eaten_count = eaten_count
        user.save(
            update_fields=[
                "challenge_status",
                "challenge_end_date",
                "final_eaten_count",
            ]
        )

        logger.info(
            f"Челлендж для пользователя {user.telegram_id} истек. Запуск отправки результатов."
        )
        transaction.on_commit(
            lambda: send_challenge_results_task.delay(user.telegram_id)
        )
