from datetime import timedelta
from tempfile import TemporaryDirectory

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .checks import persistent_storage_check
from .forms import ArticleAdminForm
from .models import Article, Concept, Dossier, SitePage


class MagazineTests(TestCase):
    def article(self, slug, **kwargs):
        defaults = dict(title=slug, author_name="Yazar", content="Metin",
                        status=Article.Status.PUBLISHED)
        defaults.update(kwargs)
        return Article.objects.create(slug=slug, **defaults)

    def test_slider_shows_latest_five_without_feature_flag(self):
        for index in range(7):
            self.article(f"yazi-{index}", cover=f"covers/{index}.jpg")
        self.article("taslak", status=Article.Status.DRAFT)
        self.article("gelecek", published_at=timezone.now() + timedelta(days=1))
        response = self.client.get(reverse("articles:home"))
        self.assertEqual([a.slug for a in response.context["featured"]],
                         [f"yazi-{i}" for i in range(6, 1, -1)])
        self.assertContains(response, "data-slide\n", count=5)
        self.assertContains(response, "/media/covers/6.jpg")
        self.assertNotContains(response, "gelecek")
        self.assertNotContains(response, "taslak")

    def test_slider_single_and_empty_states(self):
        response = self.client.get(reverse("articles:home"))
        self.assertContains(response, "Son yazılar")
        self.assertNotContains(response, "Yeni fikirler burada buluşacak.")
        self.article("tek")
        response = self.client.get(reverse("articles:home"))
        self.assertEqual(len(response.context["featured"]), 1)
        self.assertNotContains(response, "data-next")

    def test_section_filter_is_preserved(self):
        self.article("ceviri", section=Article.Section.CEVIRI)
        self.article("yorum", section=Article.Section.TARTISMA)
        response = self.client.get(reverse("articles:home"), {"bolum": "ceviri"})
        self.assertEqual([a.slug for a in response.context["featured"]], ["ceviri"])

    def test_library_lists_dossiers_and_only_their_published_contents(self):
        dossier = Dossier.objects.create(title="Emek", slug="emek", status="published")
        other = Dossier.objects.create(title="Kent", slug="kent", status="published")
        Dossier.objects.create(title="Gizli dosya", slug="gizli")
        self.article("ikinci", dossier=dossier, dossier_order=2)
        self.article("ilk", dossier=dossier, dossier_order=1, section="ceviri")
        self.article("taslak", dossier=dossier, status="draft")
        self.article("gelecek", dossier=dossier, published_at=timezone.now()+timedelta(days=1))
        self.article("baska", dossier=other)
        index = self.client.get(reverse("articles:dossier_list"))
        self.assertContains(index, "Emek")
        self.assertContains(index, "2 yazı")
        self.assertNotContains(index, "Gizli dosya")
        detail = self.client.get(reverse("articles:dossier_detail", args=["emek"]))
        self.assertEqual([a.slug for a in detail.context["page_obj"]], ["ilk", "ikinci"])
        self.assertContains(detail, 'class="dossier-contents"')
        self.assertNotContains(detail, "baska")
        self.assertEqual(self.client.get(reverse("articles:dossier_detail", args=["gizli"])).status_code, 404)

    def test_dossier_article_admin_requires_a_folder(self):
        data = dict(title="Yazı", slug="yazi", author_name="Yazar", content="<p>Metin</p>",
                    section="dosya", status="draft", dossier_order=0)
        form = ArticleAdminForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("dossier", form.errors)
        dossier = Dossier.objects.create(title="Emek", slug="emek")
        data["dossier"] = dossier.pk
        self.assertTrue(ArticleAdminForm(data=data).is_valid())

    def test_institutional_pages_are_editable_and_escaped(self):
        page = SitePage.objects.get(slug="hakkimizda")
        page.content = "Bizim dergimiz.\n\n<script>alert(1)</script>"
        page.save()
        response = self.client.get(reverse("articles:site_page", args=[page.slug]))
        self.assertContains(response, "Bizim dergimiz.")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertNotContains(self.client.get(reverse("articles:home")), "/kurumsal/kunye/")
        page.is_published = False
        page.save()
        self.assertEqual(self.client.get(reverse("articles:site_page", args=[page.slug])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("articles:home")), "/kurumsal/hakkimizda/")

    def test_media_can_be_read_by_a_new_storage_instance(self):
        with TemporaryDirectory() as root:
            with override_settings(MEDIA_ROOT=root):
                article = self.article("kalici")
                article.cover.save("cover.jpg", ContentFile(b"stored-file"))
                article.refresh_from_db()
                storage = FileSystemStorage(location=root)
                with storage.open(article.cover.name) as saved:
                    self.assertEqual(saved.read(), b"stored-file")


class ProductionStorageTests(TestCase):
    @override_settings(DEBUG=True)
    def test_local_development_does_not_require_external_storage(self):
        self.assertEqual(persistent_storage_check(None), [])

    @override_settings(DEBUG=False, SQLITE_STORAGE_PERSISTENT=False, MEDIA_STORAGE_PERSISTENT=False)
    def test_ephemeral_database_and_media_are_rejected(self):
        self.assertEqual({e.id for e in persistent_storage_check(None)},
                         {"articles.E001", "articles.E002"})

    @override_settings(DEBUG=False, SQLITE_STORAGE_PERSISTENT=True, MEDIA_STORAGE_PERSISTENT=True)
    def test_explicit_persistent_volumes_are_supported(self):
        self.assertEqual(persistent_storage_check(None), [])

    @override_settings(DEBUG=False,
        DATABASES={"default": {"ENGINE": "django.db.backends.postgresql"}},
        STORAGES={"default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}})
    def test_external_database_and_cloudinary_are_supported(self):
        self.assertEqual(persistent_storage_check(None), [])


class SocialPanelTests(TestCase):
    def test_latest_active_posts_are_grouped_by_platform(self):
        from .models import SocialPost
        for i in range(7):
            SocialPost.objects.create(platform="x", title=f"Paylaşım {i}",
                                      url=f"https://x.com/example/status/{i}", order=7-i)
        SocialPost.objects.create(platform="x", title="Gizli paylaşım", url="https://x.com/example/status/8", is_active=False)
        SocialPost.objects.create(platform="instagram", title="Instagram yazısı", url="https://www.instagram.com/p/example/")
        SocialPost.objects.create(platform="youtube", title="Yeni video", url="https://www.youtube.com/watch?v=example")
        response = self.client.get(reverse("articles:home"))
        self.assertContains(response, "Yeni video")
        groups = response.context["social_groups"]
        self.assertEqual([g["key"] for g in groups], ["x", "instagram", "youtube"])
        self.assertEqual([p.title for p in groups[0]["posts"]], [f"Paylaşım {i}" for i in range(6, 1, -1)])
        self.assertContains(response, "Instagram yazısı")
        self.assertNotContains(response, "Gizli paylaşım")
        self.assertContains(response, 'id="social-launcher"')

    def test_empty_feeds_offer_profile_links(self):
        response = self.client.get(reverse("articles:home"))
        self.assertContains(response, "Henüz paylaşım eklenmedi.", count=3)
        self.assertContains(response, "Instagram hesabına git")


class UnifiedAboutTests(TestCase):
    def test_about_includes_existing_content_and_legacy_links_redirect(self):
        SitePage.objects.filter(slug="kunye").update(content="Künye ekibi")
        SitePage.objects.filter(slug="yayin-ilkeleri").update(content="Yayın ilkelerimiz")
        response = self.client.get(reverse("articles:site_page", args=["hakkimizda"]))
        self.assertContains(response, "Künye ekibi")
        self.assertContains(response, "Yayın ilkelerimiz")
        menu = self.client.get(reverse("articles:home"))
        self.assertEqual([p.slug for p in menu.context["institutional_pages"]], ["hakkimizda"])
        for slug in ("kunye", "yayin-ilkeleri"):
            self.assertRedirects(self.client.get(reverse("articles:site_page", args=[slug])),
                reverse("articles:site_page", args=["hakkimizda"]) + "#" + slug)

    def test_hidden_sections_are_not_published_inside_about(self):
        SitePage.objects.filter(slug="kunye").update(content="Gizli ekip", is_published=False)
        response = self.client.get(reverse("articles:site_page", args=["hakkimizda"]))
        self.assertNotContains(response, "Gizli ekip")


class DossierEditorTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create_superuser(username="editor", email="editor@example.com")
        self.client.force_login(self.user)

    def test_create_dossier_with_multiple_articles_in_one_form(self):
        data = {"title": "Kent Dosyası", "slug": "kent-dosyasi", "status": "published", "order": "0",
                "articles-TOTAL_FORMS": "2", "articles-INITIAL_FORMS": "0",
                "articles-MIN_NUM_FORMS": "0", "articles-MAX_NUM_FORMS": "1000"}
        for i in range(2):
            data.update({f"articles-{i}-title": f"Kent yazısı {i}", f"articles-{i}-slug": f"kent-{i}",
                         f"articles-{i}-author_name": "Yazar", f"articles-{i}-content": "<p>Yazı metni</p>",
                         f"articles-{i}-section": "dosya", f"articles-{i}-status": "published",
                         f"articles-{i}-dossier_order": str(i)})
        response = self.client.post(reverse("admin:articles_dossier_add"), data)
        self.assertEqual(response.status_code, 302)
        dossier = Dossier.objects.get(slug="kent-dosyasi")
        self.assertEqual(dossier.articles.count(), 2)
        self.assertEqual(dossier.articles.first().content_html, "<p>Yazı metni</p>")
        home = self.client.get(reverse("articles:home"))
        self.assertEqual(len(home.context["featured"]), 2)
        self.assertContains(home, "data-slider")
        self.assertContains(home, "data-next")
        library = self.client.get(reverse("articles:dossier_list"))
        self.assertContains(library, "dossier-book")
        self.assertContains(library, "2 yazı")

    def test_admin_explains_folder_workflow_and_has_editable_article_fields(self):
        response = self.client.get(reverse("admin:articles_dossier_add"))
        self.assertContains(response, "Dosya / klasör adı")
        self.assertContains(response, 'name="articles-__prefix__-content"')
        self.assertContains(response, 'name="articles-__prefix__-title"')
        self.assertContains(response, "Dosya kütüphanesi")

    def test_empty_home_keeps_slider_layout_without_fake_articles(self):
        response = self.client.get(reverse("articles:home"))
        self.assertContains(response, 'class="featured-slider"')
        self.assertContains(response, 'class="hero slider-empty"')
        self.assertNotContains(response, "data-slide\n")


class SectionLandingTests(TestCase):
    def test_translation_and_discussion_only_show_their_own_articles(self):
        dossier = Dossier.objects.create(title="Dosya başlığı", slug="dosya", status="published")
        Concept.objects.create(name="Özel kavram", description="Kavram metni")
        for section in ("ceviri", "tartisma"):
            for i in range(6):
                Article.objects.create(title=f"{section} yazısı {i}", slug=f"{section}-{i}",
                    author_name="Yazar", content="İçerik", section=section, status="published", dossier=dossier,
                    is_archive_pick=True)
        for section in ("ceviri", "tartisma"):
            with self.subTest(section=section):
                response = self.client.get(reverse("articles:home"), {"bolum": section})
                self.assertEqual(len(response.context["featured"]), 5)
                self.assertTrue(all(a.section == section for a in response.context["featured"]))
                self.assertEqual(len(response.context["articles"]), 6)
                self.assertTrue(all(a.section == section for a in response.context["articles"]))
                self.assertEqual(list(response.context["dossiers"]), [])
                self.assertNotContains(response, 'class="dossier-book"')
                self.assertNotContains(response, "Öne Çıkan Dosyalar")
                self.assertNotContains(response, "Özel kavram")
                self.assertNotContains(response, "Arşivden Seçmeler")
                other = "ceviri" if section == "tartisma" else "tartisma"
                self.assertNotContains(response, f"{other} yazısı")
                self.assertContains(response, f"?bolum={section}")
                self.assertEqual([a.slug for a in response.context["articles"]],
                                 [f"{section}-{i}" for i in range(5, -1, -1)])
        self.assertContains(self.client.get(reverse("articles:home")), 'class="dossier-book"')

    def test_section_pagination_keeps_filter_and_slider(self):
        for i in range(10):
            Article.objects.create(title=f"Çeviri {i}", slug=f"translation-{i}", section="ceviri",
                author_name="Yazar", content="Metin", status="published")
        response = self.client.get(reverse("articles:home"), {"bolum": "ceviri", "sayfa": 2})
        self.assertEqual(response.context["section_page"].number, 2)
        self.assertEqual(len(response.context["articles"]), 1)
        self.assertEqual(len(response.context["featured"]), 5)
        self.assertContains(response, "bolum=ceviri&amp;sayfa=1")


class DictionaryTests(TestCase):
    def test_letter_filter_and_alphabetical_order(self):
        Concept.objects.create(name="Anarşizm", description="Anarşizm açıklaması.", order=0)
        Concept.objects.create(name="Adalet", description="Adalet açıklaması.", order=9)
        Concept.objects.create(name="Bilinç", description="Bilinç açıklaması.")
        Concept.objects.create(name="Aktif olmayan", description="Gizli tanım.", is_active=False)
        response = self.client.get(reverse("articles:concept_dictionary"), {"harf": "a"})
        dictionary = response.context["dictionary"]
        self.assertEqual(dictionary["selected_letter"], "A")
        self.assertEqual([c.name for c in dictionary["concepts"]], ["Adalet", "Anarşizm"])
        self.assertEqual(len(dictionary["letters"]), 29)
        self.assertNotContains(response, "Bilinç açıklaması.")
        self.assertNotContains(response, "Gizli tanım.")
        response = self.client.get(reverse("articles:concept_dictionary"), {"harf": "B"})
        self.assertContains(response, "Bilinç açıklaması.")
        self.assertNotContains(response, "Adalet açıklaması.")

    def test_turkish_dotted_and_dotless_letters_are_distinct(self):
        for name in ("İdeoloji", "İrade", "Işık", "ıslah", "ihtiyaç", "Çelişki", "Şuur"):
            Concept.objects.create(name=name, description=f"{name} tanımı")
        for letter, expected in [("i", ["İdeoloji", "ihtiyaç", "İrade"]), ("ı", ["ıslah", "Işık"]),
                                 ("ç", ["Çelişki"]), ("ş", ["Şuur"])]:
            with self.subTest(letter=letter):
                response = self.client.get(reverse("articles:concept_dictionary"), {"harf": letter})
                self.assertEqual([c.name for c in response.context["dictionary"]["concepts"]], expected)

    def test_empty_letters_and_invalid_selection(self):
        response = self.client.get(reverse("articles:concept_dictionary"), {"harf": "Z"})
        self.assertContains(response, "Z harfiyle başlayan bir kavram henüz eklenmedi.")
        response = self.client.get(reverse("articles:concept_dictionary"), {"harf": "invalid"})
        self.assertEqual(response.context["dictionary"]["selected_letter"], "A")
        self.assertContains(self.client.get(reverse("articles:home")), 'class="dictionary-alphabet"')

    def test_discussion_label_is_shortened_everywhere(self):
        article = Article.objects.create(title="Bir tartışma", slug="bir-tartisma", author_name="Yazar",
                                         content="Metin", section="tartisma", status="published")
        self.assertEqual(article.get_section_display(), "Tartışma")
        response = self.client.get(reverse("articles:home"), {"bolum": "tartisma"})
        self.assertEqual(response.context["section_title"], "Tartışma")
        self.assertNotContains(response, "Tartışma ve Yorum")


class ArticleWrappingTests(TestCase):
    def test_pasted_nonbreaking_spaces_wrap_without_losing_formatting(self):
        article = Article(content_html='<p>Bir&nbsp;<strong>uzun\u00a0yazı</strong>\u202fmetni.</p>')
        self.assertEqual(str(article.formatted_content), '<p>Bir <strong>uzun yazı</strong> metni.</p>')
        self.assertIn('&nbsp;', article.content_html)

    def test_plain_text_nonbreaking_spaces_are_also_normalized(self):
        article = Article(content='Bir\u00a0yazı\u202fmetni.\n\nİkinci paragraf.')
        html = str(article.formatted_content)
        self.assertIn('<p>Bir yazı metni.</p>', html)
        self.assertIn('<p>İkinci paragraf.</p>', html)
