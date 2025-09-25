import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from backend.products.models import Product


class Command(BaseCommand):
    help = "Обновляет поле 'Интересный факт' для продуктов из JSON файла."

    DATA_FILE = settings.BASE_DIR / "fixtures" / "generated_facts.json"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not self.DATA_FILE.exists():
            self.stdout.write(self.style.ERROR(f"Файл не найден: {self.DATA_FILE}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Начинаю обновление фактов из файла {self.DATA_FILE}..."
            )
        )

        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        facts_map = {item["pk"]: item["fact"] for item in data}
        product_pks = facts_map.keys()

        products_to_update = list(Product.objects.filter(pk__in=product_pks))

        if not products_to_update:
            self.stdout.write(
                self.style.WARNING("Не найдено продуктов для обновления.")
            )
            return

        updated_count = 0

        for product in products_to_update:
            if not product.fact:
                new_fact = facts_map.get(product.pk)
                if new_fact:
                    product.fact = new_fact
                    updated_count += 1
            else:
                self.stdout.write(
                    f"  - Продукт '{product.name}' (ID: {product.pk}) уже имеет факт, пропускаю."
                )

        Product.objects.bulk_update(products_to_update, ["fact"])

        self.stdout.write(
            self.style.SUCCESS(
                f"\nОбновление успешно завершено!\n"
                f"Всего фактов в файле: {len(facts_map)}\n"
                f"Продуктов найдено в БД: {len(products_to_update)}\n"
                f"Фактов обновлено (где поле было пустым): {updated_count}"
            )
        )
