from django.contrib import admin  # type: ignore
from django.db import models  # type: ignore
from markdownx.widgets import AdminMarkdownxWidget  # type: ignore

from .models import Blog, Category, Advertisement, Anchorlink


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_display_links = ("id", "title")


class BlogAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminMarkdownxWidget},
    }

class AnchorlinkInline(admin.TabularInline):
    model = Anchorlink
    extra = 1

class AdvertisementAdmin(admin.ModelAdmin):
    inlines = [AnchorlinkInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Advertisement, AdvertisementAdmin)
