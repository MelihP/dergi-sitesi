from django.contrib import admin
from .models import Article, Concept, SocialPost
from .forms import ArticleAdminForm

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = (
        "title",
        "author_name",
        "section",
        "status",
        "published_at",
        "is_featured",
        "is_archive_pick",
    )

    list_display_links = ("title",)

    list_editable = (
        "status",
        "is_featured",
        "is_archive_pick",
    )

    list_filter = (
        "status",
        "section",
    )

    search_fields = (
        "title",
        "author_name",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "platform",
        "order",
        "is_active",
        "created_at",
    )

    list_display_links = ("title",)

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "platform",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    readonly_fields = ("created_at",)

    fields = (
        "platform",
        "title",
        "description",
        "image",
        "url",
        "order",
        "is_active",
        "created_at",
    )


admin.site.site_header = "Dergi Yönetimi"
admin.site.site_title = "Dergi Admin"
admin.site.index_title = "İçerik Yönetimi"