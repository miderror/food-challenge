from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, primary_key=True, verbose_name="Телеграм ID"
    )
    username = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Юзернейм"
    )
    phone_number = PhoneNumberField(
        null=True, blank=True, verbose_name="Номер телефона"
    )
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    height_cm = models.PositiveIntegerField(verbose_name="Рост (см)")
    weight_kg = models.PositiveIntegerField(verbose_name="Вес (кг)")
    bmi = models.FloatField(null=True, blank=True, verbose_name="ИМТ")
    eaten_products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="eaten_by_users",
        verbose_name="Съеденные продукты",
    )
    last_activity_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Последняя активность"
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class ChallengeStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Активен"
        COMPLETED = "COMPLETED", "Завершен (успешно)"
        EXPIRED = "EXPIRED", "Завершен (по времени)"

    challenge_status = models.CharField(
        max_length=10,
        choices=ChallengeStatus.choices,
        default=ChallengeStatus.ACTIVE,
        verbose_name="Статус челленджа",
    )
    challenge_end_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата завершения челленджа"
    )
    final_eaten_count = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Итоговое кол-во продуктов"
    )

    def save(self, *args, **kwargs):
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            self.bmi = round(self.weight_kg / (height_m**2), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"id: {str(self.telegram_id)}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
