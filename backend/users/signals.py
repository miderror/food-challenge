from django.db import transaction
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from backend.users.models import User
from backend.users.tasks import send_challenge_results_task

CHALLENGE_GOAL = 400


@receiver(m2m_changed, sender=User.eaten_products.through)
def check_challenge_completion(sender, instance, action, **kwargs):
    if action != "post_add":
        return

    user = instance

    if user.challenge_status != User.ChallengeStatus.ACTIVE:
        return

    eaten_count = user.eaten_products.count()

    if eaten_count >= CHALLENGE_GOAL:
        user.challenge_status = User.ChallengeStatus.COMPLETED
        user.challenge_end_date = timezone.now()
        user.final_eaten_count = eaten_count
        user.save(
            update_fields=[
                "challenge_status",
                "challenge_end_date",
                "final_eaten_count",
            ]
        )

        transaction.on_commit(
            lambda: send_challenge_results_task.delay(user.telegram_id)
        )
