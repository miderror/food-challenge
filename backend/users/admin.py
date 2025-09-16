from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "full_name",
        "username",
        "phone_number",
        "challenge_status",
        "get_eaten_products_count",
        "get_days_in_challenge",
        "date_joined",
    )
    search_fields = ("telegram_id", "username", "full_name", "phone_number")
    list_filter = ("challenge_status", "last_activity_at", "date_joined")
    readonly_fields = (
        "telegram_id",
        "username",
        "phone_number",
        "date_joined",
        "last_activity_at",
        "full_name",
        "height_cm",
        "weight_kg",
        "bmi",
        "challenge_status",
        "challenge_end_date",
        "final_eaten_count",
    )
    filter_horizontal = ("eaten_products",)
    fieldsets = (
        (
            "Контактная информация",
            {"fields": ("telegram_id", "username", "phone_number")},
        ),
        (
            "Данные профиля",
            {"fields": ("full_name", "height_cm", "weight_kg", "bmi")},
        ),
        ("Статистика челленджа", {"fields": ("date_joined", "eaten_products")}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.challenge_status != User.ChallengeStatus.ACTIVE:
            return self.readonly_fields + ("eaten_products",)
        return self.readonly_fields

    @admin.display(description="Дней в челлендже")
    def get_days_in_challenge(self, obj):
        if obj.date_joined:
            return (timezone.now() - obj.date_joined).days
        return 0

    @admin.display(description="Съедено продуктов")
    def get_eaten_products_count(self, obj):
        return obj.eaten_products.count()

    def has_add_permission(self, request):
        return False


admin.site.unregister(AuthUser)
admin.site.unregister(Group)
