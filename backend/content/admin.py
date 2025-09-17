from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    FAQ,
    AboutProject,
    AboutProjectMedia,
    BotTexts,
    MediaType,
    SiteSettings,
)


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


class AboutProjectMediaInline(admin.TabularInline):
    model = AboutProjectMedia
    extra = 1
    fields = ("image", "order")


@admin.register(AboutProject)
class AboutProjectAdmin(SingletonModelAdmin):
    fieldsets = (("Содержимое", {"fields": ("text", "media_type", "media_file")}),)
    inlines = [AboutProjectMediaInline]

    class Media:
        js = ("admin/js/about_project_admin_fields.js",)


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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        choices_without_media_group = [
            choice for choice in MediaType.choices if choice[0] != MediaType.MEDIA_GROUP
        ]
        form.base_fields["media_type"].choices = choices_without_media_group
        return form
