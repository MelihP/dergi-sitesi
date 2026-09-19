from django.contrib import admin

from .forms import ArticleAdminForm
from .models import Article, Concept, Dossier, SocialPost


class DossierArticleInline(admin.TabularInline):
    model = Article

    fields = (
        "title",
        "author_name",
        "status",
        "dossier_order",
    )

    readonly_fields = (
        "title",
        "author_name",
        "status",
    )

    ordering = (
        "dossier_order",
        "-published_at",
    )

    extra = 0
    can_delete = False
    show_change_link = True

    verbose_name = "Bu dosyadaki yazı"
    verbose_name_plural = "Bu dosyadaki yazılar"


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "is_featured",
        "order",
        "published_at",
    )

    list_display_links = (
        "title",
    )

    list_editable = (
        "status",
        "is_featured",
        "order",
    )

    list_filter = (
        "status",
        "is_featured",
        "published_at",
    )

    search_fields = (
        "title",
        "summary",
        "description",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        ),
    }

    readonly_fields = (
        "created_at",
    )

    date_hierarchy = "published_at"

    save_on_top = True

    fieldsets = (
        (
            "Dosya bilgileri",
            {
                "fields": (
                    "title",
                    "slug",
                    "summary",
                    "description",
                    "cover",
                ),
            },
        ),
        (
            "Yayın ayarları",
            {
                "fields": (
                    "status",
                    "published_at",
                    "is_featured",
                    "order",
                ),
            },
        ),
        (
            "Sistem bilgileri",
            {
                "fields": (
                    "created_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    inlines = (
        DossierArticleInline,
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm

    list_display = (
        "title",
        "author_name",
        "section",
        "dossier",
        "dossier_order",
        "status",
        "published_at",
        "is_featured",
        "is_archive_pick",
    )

    list_display_links = (
        "title",
    )

    list_editable = (
        "dossier_order",
        "status",
        "is_featured",
        "is_archive_pick",
    )

    list_filter = (
        "status",
        "section",
        "dossier",
        "is_featured",
        "is_archive_pick",
        "published_at",
    )

    search_fields = (
        "title",
        "author_name",
        "content",
        "summary",
        "dossier__title",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        ),
    }

    autocomplete_fields = (
        "dossier",
    )

    list_select_related = (
        "dossier",
    )

    date_hierarchy = "published_at"

    save_on_top = True


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "is_active",
    )

    list_display_links = (
        "name",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "order",
        "name",
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

    list_display_links = (
        "title",
    )

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

    readonly_fields = (
        "created_at",
    )

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