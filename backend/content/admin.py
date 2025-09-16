from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import FAQ, AboutProject, BotTexts, SiteSettings


class SingletonModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        obj, _ = self.model.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=(obj.pk,),
            )
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(BotTexts)
class BotTextsAdmin(SingletonModelAdmin):
    pass


@admin.register(AboutProject)
class AboutProjectAdmin(SingletonModelAdmin):
    fieldsets = (("Содержимое", {"fields": ("text", ("media_file", "media_type"))}),)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "media_type")
    list_editable = ("order",)
    search_fields = ("question", "answer")
    list_filter = ("media_type",)

    fieldsets = (
        ("Основная информация", {"fields": ("question", "order")}),
        ("Содержимое ответа", {"fields": ("answer", ("media_file", "media_type"))}),
    )
