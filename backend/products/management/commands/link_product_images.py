import os
import re

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from backend.products.models import Product

IMAGES_SOURCE_DIR = "/app/tmp/product_images"


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


class Command(BaseCommand):
    help = "Привязывает скачанные изображения из временной папки к продуктам в БД."

    def handle(self, *args, **kwargs):
        if not os.path.isdir(IMAGES_SOURCE_DIR):
            self.stdout.write(
                self.style.ERROR(
                    f"Папка с изображениями не найдена по пути: '{IMAGES_SOURCE_DIR}'\n"
                    f"Убедитесь, что вы загрузили папку на сервер и указали правильный путь в скрипте."
                )
            )
            return

        self.stdout.write("Начинаю процесс привязки изображений к продуктам...")

        products_to_process = Product.objects.all()
        total_products = products_to_process.count()
        updated_products_count = 0
        not_found_folders_count = 0

        with transaction.atomic():
            for product in products_to_process:
                sanitized_name = sanitize_filename(product.name)
                product_folder_path = os.path.join(IMAGES_SOURCE_DIR, sanitized_name)

                if not os.path.isdir(product_folder_path):
                    self.stdout.write(
                        self.style.WARNING(
                            f"  - Продукт '{product.name}': папка не найдена, пропускаю."
                        )
                    )
                    not_found_folders_count += 1
                    continue

                product_was_updated = False

                icon_path_png = os.path.join(product_folder_path, "icon.png")
                icon_path_jpg = os.path.join(product_folder_path, "icon.jpg")
                main_photo_path_png = os.path.join(
                    product_folder_path, "main_photo.png"
                )
                main_photo_path_jpg = os.path.join(
                    product_folder_path, "main_photo.jpg"
                )

                icon_path = (
                    icon_path_png if os.path.exists(icon_path_png) else icon_path_jpg
                )
                main_photo_path = (
                    main_photo_path_png
                    if os.path.exists(main_photo_path_png)
                    else main_photo_path_jpg
                )

                if os.path.exists(icon_path):
                    with open(icon_path, "rb") as f:
                        product.icon_photo.save(
                            os.path.basename(icon_path), File(f), save=False
                        )
                        product_was_updated = True
                        self.stdout.write(
                            f"  - Продукт '{product.name}': найдена иконка."
                        )

                if os.path.exists(main_photo_path):
                    with open(main_photo_path, "rb") as f:
                        product.main_photo.save(
                            os.path.basename(main_photo_path), File(f), save=False
                        )
                        product_was_updated = True
                        self.stdout.write(
                            f"  - Продукт '{product.name}': найдено основное фото."
                        )

                if product_was_updated:
                    product.save(update_fields=["icon_photo", "main_photo"])
                    updated_products_count += 1

        self.stdout.write(self.style.SUCCESS("\nПроцесс привязки завершен!"))

        self.stdout.write("\n" + "=" * 30)
        self.stdout.write(self.style.SUCCESS("СТАТИСТИКА ОБНОВЛЕНИЯ"))
        self.stdout.write(f"Всего продуктов в БД: {total_products}")
        self.stdout.write(
            f"Продуктов обновлено (найдены фото): {updated_products_count}"
        )
        self.stdout.write(
            f"Продуктов пропущено (папка не найдена): {not_found_folders_count}"
        )
        self.stdout.write("=" * 30 + "\n")

        self.stdout.write(self.style.WARNING("ПРОВЕРКА ПРОДУКТОВ БЕЗ ИЗОБРАЖЕНИЙ"))

        products_still_missing_images = Product.objects.filter(
            Q(icon_photo__isnull=True)
            | Q(icon_photo="")
            | Q(main_photo__isnull=True)
            | Q(main_photo="")
        ).order_by("name")

        if not products_still_missing_images:
            self.stdout.write(
                self.style.SUCCESS("Отлично! У всех продуктов есть оба изображения.")
            )
        else:
            self.stdout.write(
                f"Найдено {products_still_missing_images.count()} продуктов, у которых не хватает изображений:\n"
            )
            for product in products_still_missing_images:
                missing = []
                if not product.icon_photo:
                    missing.append("иконка")
                if not product.main_photo:
                    missing.append("основное фото")
                self.stdout.write(
                    f"- {product.name} (отсутствует: {', '.join(missing)})"
                )
