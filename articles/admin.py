from django.contrib import admin

from .forms import ArticleAdminForm, DossierAdminForm
from .models import Article, Concept, Dossier, SocialPost, SitePage


class DossierArticleInline(admin.StackedInline):
    form = ArticleAdminForm
    model = Article

    fields = (
        ("title", "slug"),
        "author_name",
        "summary",
        "content",
        "cover",
        ("section", "status"),
        ("published_at", "dossier_order"),
    )
    prepopulated_fields = {"slug": ("title",)}

    ordering = (
        "dossier_order",
        "-published_at",
    )

    extra = 0
    can_delete = False
    show_change_link = True

    verbose_name = "yazı"
    verbose_name_plural = "Bu dosyadaki yazılar"


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    form = DossierAdminForm
    change_form_template = "admin/articles/dossier/change_form.html"
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
            "Dosya / klasör bilgileri",
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

@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "order")
    list_editable = ("is_published", "order")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content")
