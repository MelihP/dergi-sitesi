from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

from .richtext import render_content


class Dossier(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Taslak"
        PUBLISHED = "published", "Yayında"

    title = models.CharField(
        "Dosya başlığı",
        max_length=200,
    )

    slug = models.SlugField(
        "Adres kısa adı",
        max_length=220,
        unique=True,
        help_text="Örnek: emek",
    )

    summary = models.TextField(
        "Kısa açıklama",
        blank=True,
        help_text="Dosya kartlarında gösterilecek kısa açıklama.",
    )

    description = models.TextField(
        "Dosya tanıtım metni",
        blank=True,
        help_text="Dosya sayfasının üst bölümünde gösterilir.",
    )

    cover = models.ImageField(
        "Dosya kapak görseli",
        upload_to="dossiers/",
        blank=True,
    )

    status = models.CharField(
        "Yayın durumu",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_featured = models.BooleanField(
        "Ana sayfada göster",
        default=False,
    )

    order = models.PositiveIntegerField(
        "Sıralama",
        default=0,
        help_text="Küçük sayılar önce gösterilir.",
    )

    created_at = models.DateTimeField(
        "Oluşturulma zamanı",
        auto_now_add=True,
    )

    published_at = models.DateTimeField(
        "Yayın tarihi",
        null=True,
        blank=True,
        help_text=(
            "Yayındaki dosyada boş bırakılırsa "
            "kaydedildiği zaman kullanılır."
        ),
    )

    class Meta:
        ordering = [
            "order",
            "-published_at",
            "-id",
        ]
        verbose_name = "Dosya"
        verbose_name_plural = "Dosyalar"

    def save(self, *args, **kwargs):
        if (
            self.status == self.Status.PUBLISHED
            and self.published_at is None
        ):
            self.published_at = timezone.now()

            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = (
                    set(kwargs["update_fields"])
                    | {"published_at"}
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Taslak"
        PUBLISHED = "published", "Yayında"

    class Section(models.TextChoices):
        DOSYA = "dosya", "Dosya"
        CEVIRI = "ceviri", "Çeviri"
        TARTISMA = "tartisma", "Tartışma ve Yorum"

    title = models.CharField(
        "Başlık",
        max_length=250,
    )

    slug = models.SlugField(
        "Adres kısa adı",
        unique=True,
    )

    author_name = models.CharField(
        "Yazar adı",
        max_length=150,
    )

    summary = models.TextField(
        "Kısa açıklama",
        blank=True,
    )

    content = models.TextField(
        "Yazı metni",
    )

    content_html = models.TextField(
        "Biçimlendirilmiş yazı",
        blank=True,
        editable=False,
    )

    cover = models.ImageField(
        "Kapak görseli",
        upload_to="covers/",
        blank=True,
    )

    dossier = models.ForeignKey(
        Dossier,
        verbose_name="Bağlı olduğu dosya",
        related_name="articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=(
            "Yazı bir tematik dosyaya aitse seçin. "
            "Örnek: Emek."
        ),
    )

    dossier_order = models.PositiveIntegerField(
        "Dosya içindeki sıralama",
        default=0,
        help_text=(
            "Dosya sayfasındaki sıralamayı belirler. "
            "Küçük sayılar önce gösterilir."
        ),
    )

    section = models.CharField(
        "Bölüm",
        max_length=20,
        choices=Section.choices,
        default=Section.DOSYA,
    )

    status = models.CharField(
        "Yayın durumu",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_featured = models.BooleanField(
        "Manşette göster",
        default=False,
    )

    created_at = models.DateTimeField(
        "Oluşturulma zamanı",
        auto_now_add=True,
    )

    published_at = models.DateTimeField(
        "Yayın tarihi",
        null=True,
        blank=True,
        help_text=(
            "Yayındaki yazıda boş bırakılırsa "
            "kaydedildiği zaman kullanılır."
        ),
    )

    is_archive_pick = models.BooleanField(
        "Arşivden seçmelerde göster",
        default=False,
    )

    class Meta:
        ordering = [
            "-created_at",
            "-id",
        ]
        verbose_name = "Yazı"
        verbose_name_plural = "Yazılar"

    def save(self, *args, **kwargs):
        if (
            self.status == self.Status.PUBLISHED
            and self.published_at is None
        ):
            self.published_at = timezone.now()

            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = (
                    set(kwargs["update_fields"])
                    | {"published_at"}
                )

        super().save(*args, **kwargs)

    @property
    def formatted_content(self):
        return render_content(self)

    def __str__(self):
        return self.title


class Concept(models.Model):
    name = models.CharField(
        "Kavram",
        max_length=150,
    )

    description = models.TextField(
        "Açıklama",
    )

    order = models.PositiveIntegerField(
        "Sıralama",
        default=0,
    )

    is_active = models.BooleanField(
        "Sitede göster",
        default=True,
    )

    class Meta:
        ordering = [
            "order",
            "name",
        ]
        verbose_name = "Kavram"
        verbose_name_plural = "Kavramlar"

    def __str__(self):
        return self.name


class SocialPost(models.Model):
    class Platform(models.TextChoices):
        X = "x", "X"
        INSTAGRAM = "instagram", "Instagram"
        YOUTUBE = "youtube", "YouTube"

    platform = models.CharField(
        "Platform",
        max_length=20,
        choices=Platform.choices,
    )

    title = models.CharField(
        "Başlık",
        max_length=200,
    )

    description = models.TextField(
        "Kısa açıklama",
        blank=True,
    )

    image = models.ImageField(
        "Görsel",
        upload_to="social/",
        blank=True,
    )

    url = models.URLField(
        "Gönderi bağlantısı",
        max_length=1000,
        validators=[
            URLValidator(
                schemes=["http", "https"],
            ),
        ],
        help_text=(
            "Gönderinin veya videonun "
            "tam bağlantısını gir."
        ),
    )

    order = models.PositiveIntegerField(
        "Sıralama",
        default=0,
        help_text="Küçük sayılar önce gösterilir.",
    )

    is_active = models.BooleanField(
        "Sitede göster",
        default=True,
    )

    created_at = models.DateTimeField(
        "Eklenme zamanı",
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "order",
            "-created_at",
            "-id",
        ]
        verbose_name = "Sosyal medya gönderisi"
        verbose_name_plural = "Sosyal medya gönderileri"

    def __str__(self):
        return (
            f"{self.get_platform_display()} — "
            f"{self.title}"
        )