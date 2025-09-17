from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название категории"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория продукта"
        verbose_name_plural = "Категории продуктов"
        ordering = ["name"]


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название продукта")
    categories = models.ManyToManyField(
        ProductCategory,
        related_name="products",
        verbose_name="Категории",
    )
    fact = models.TextField(
        blank=True, null=True, verbose_name="Интересный факт о продукте"
    )
    icon_photo = models.ImageField(
        upload_to="product_icons/",
        blank=True,
        null=True,
        verbose_name="Фото-иконка (для поиска)",
        help_text="Маленькое фото для инлайн-режима.",
    )
    main_photo = models.ImageField(
        upload_to="product_main_photos/",
        blank=True,
        null=True,
        verbose_name="Основное фото",
        help_text="Фото, которое отправляется после добавления продукта.",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]


class ProductSuggestion(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, verbose_name="Пользователь"
    )
    product_name = models.CharField(max_length=100, verbose_name="Предложенный продукт")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Status(models.TextChoices):
        NEW = "NEW", "Новый"
        APPROVED = "APPROVED", "Одобрен"
        REJECTED = "REJECTED", "Отклонен"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.NEW, verbose_name="Статус"
    )

    def __str__(self):
        return f"{self.product_name} от {self.user}"

    class Meta:
        verbose_name = "Предложенный продукт"
        verbose_name_plural = "Предложенные продукты"
        ordering = ["-created_at"]
