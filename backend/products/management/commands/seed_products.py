import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from backend.products.models import Product, ProductCategory

DATA_FILE = settings.BASE_DIR / "fixtures" / "products_data.json"


class Command(BaseCommand):
    help = "Загружает категории и продукты из JSON файла (fixtures/products_data.json) в базу данных"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not DATA_FILE.exists():
            self.stdout.write(self.style.ERROR(f"Файл не найден: {DATA_FILE}"))
            return

        self.stdout.write(
            self.style.WARNING("Очистка старых данных о продуктах и категориях...")
        )
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Старые данные успешно удалены."))

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.stdout.write("Начинается загрузка данных...")

        products_to_create = []

        for category_name, product_list in data.items():
            category, created = ProductCategory.objects.get_or_create(
                name=category_name
            )
            if created:
                self.stdout.write(f"  Создана категория: {category_name}")

            for product_name in product_list:
                products_to_create.append(Product(name=product_name, category=category))

        Product.objects.bulk_create(products_to_create, ignore_conflicts=True)

        total_categories = ProductCategory.objects.count()
        total_products = Product.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nЗагрузка успешно завершена!\n"
                f"Всего категорий в БД: {total_categories}\n"
                f"Всего продуктов в БД: {total_products}"
            )
        )
