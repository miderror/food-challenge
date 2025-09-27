from asgiref.sync import sync_to_async
from django.utils import timezone
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_valid_number

from backend.content.models import (
    FAQ,
    AboutProject,
    BotTexts,
    MediaType,
    SiteSettings,
)
from backend.products.models import Product, ProductCategory, ProductSuggestion
from backend.users.models import User


@sync_to_async
def get_user_by_id(telegram_id: int):
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None


@sync_to_async
def register_user(
    telegram_id: int,
    username: str | None,
    phone_number_str: str,
    full_name: str,
    height: int,
    weight: float,
):
    phone_number = to_python(phone_number_str)
    if not is_valid_number(phone_number):
        return None, "Некорректный формат номера телефона."
    user = User.objects.create(
        telegram_id=telegram_id,
        username=username,
        phone_number=phone_number,
        full_name=full_name,
        height_cm=height,
        weight_kg=weight,
    )
    return user


@sync_to_async
def get_user_profile_info(user_id: int):
    try:
        user = User.objects.prefetch_related("eaten_products").get(telegram_id=user_id)
        days_in_challenge = (timezone.now() - user.date_joined).days + 1
        eaten_count = user.eaten_products.count()
        eaten_products_list = list(user.eaten_products.values_list("name", flat=True))
        return {
            "days": days_in_challenge,
            "eaten_count": eaten_count,
            "eaten_list": eaten_products_list,
            "height": user.height_cm,
            "weight": user.weight_kg,
            "bmi": user.bmi,
        }
    except User.DoesNotExist:
        return None


@sync_to_async
def get_available_product_categories(user_id: int):
    try:
        user = User.objects.get(telegram_id=user_id)
        eaten_product_ids = user.eaten_products.values_list("id", flat=True)

        uneaten_products = Product.objects.exclude(id__in=eaten_product_ids)

        available_categories = (
            ProductCategory.objects.filter(products__in=uneaten_products)
            .distinct()
            .order_by("name")
        )

        return list(available_categories.values_list("id", "name"))

    except User.DoesNotExist:
        return list(ProductCategory.objects.order_by("name").values_list("id", "name"))


@sync_to_async
def get_uneaten_products_by_category(user_id: int, category_id: int):
    user = User.objects.get(telegram_id=user_id)
    eaten_product_ids = user.eaten_products.values_list("id", flat=True)
    products = (
        Product.objects.filter(categories__id=category_id)
        .exclude(id__in=eaten_product_ids)
        .distinct()
    )
    return list(products.values_list("id", "name"))


@sync_to_async
def get_product_by_id(product_id: int):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None


@sync_to_async
def add_eaten_product(user_id: int, product_id: int):
    try:
        user = User.objects.get(telegram_id=user_id)
        if user.challenge_status != User.ChallengeStatus.ACTIVE:
            return False, "Челлендж уже завершен."
        product = Product.objects.get(id=product_id)
        user.eaten_products.add(product)
        return True, product.name
    except (User.DoesNotExist, Product.DoesNotExist):
        return False, ""


@sync_to_async
def create_product_suggestion(user_id: int, product_name: str):
    ProductSuggestion.objects.create(user_id=user_id, product_name=product_name)


@sync_to_async
def get_community_link():
    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    return settings.community_link


@sync_to_async
def get_about_project_content():
    content, _ = AboutProject.objects.prefetch_related("media_items").get_or_create(
        pk=1
    )

    media_items = []
    if content.media_type == MediaType.MEDIA_GROUP:
        media_items = list(content.media_items.all())

    return {"content": content, "media_items": media_items}


@sync_to_async
def get_faq_list():
    return list(FAQ.objects.values_list("id", "question"))


@sync_to_async
def get_faq_item(faq_id: int):
    try:
        return FAQ.objects.get(id=faq_id)
    except FAQ.DoesNotExist:
        return None


@sync_to_async
def get_bot_texts():
    texts, _ = BotTexts.objects.get_or_create(pk=1)
    return texts


@sync_to_async
def search_uneaten_products(user_id: int, query: str, limit: int = 10):
    try:
        user = User.objects.get(telegram_id=user_id)
        eaten_product_ids = user.eaten_products.values_list("id", flat=True)

        products = (
            Product.objects.filter(name__icontains=query)
            .exclude(id__in=eaten_product_ids)
            .order_by("name")[:limit]
        )
        return list(products)
    except User.DoesNotExist:
        return []
