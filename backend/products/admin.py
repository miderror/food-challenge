from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import Product, ProductCategory, ProductSuggestion


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "view_products_link")
    search_fields = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(products_count=Count("products"))
        return queryset

    @admin.display(description="Продукты", ordering="products_count")
    def view_products_link(self, obj):
        count = obj.products_count
        if count > 0:
            url = (
                reverse("admin:products_product_changelist")
                + f"?category__id__exact={obj.pk}"
            )
            return format_html('<a href="{}">Смотреть ({})</a>', url, count)
        return "Нет продуктов"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    search_fields = ("name",)
    list_filter = ("category",)
    autocomplete_fields = ("category",)
    fields = ("category", "name")


@admin.register(ProductSuggestion)
class ProductSuggestionAdmin(admin.ModelAdmin):
    list_display = ("product_name", "user", "created_at", "status")
    list_filter = ("status", "created_at")
    search_fields = ("product_name", "user__username", "user__full_name")
    readonly_fields = ("user", "product_name", "created_at")
    list_editable = ("status",)

    def has_add_permission(self, request):
        return False
