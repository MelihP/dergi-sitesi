import unicodedata

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

from .richtext import render_content
from .social_preview import social_preview
from .youtube import validate_youtube_url, youtube_video_id


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


class Tag(models.Model):
    name = models.CharField("Etiket", max_length=80)
    key = models.CharField(max_length=160, unique=True, editable=False, blank=True)

    class Meta:
        ordering = ["name", "id"]
        verbose_name = "Etiket"
        verbose_name_plural = "Etiketler"

    @staticmethod
    def tidy_name(value):
        return unicodedata.normalize("NFC", " ".join(value.split()))

    @classmethod
    def key_for(cls, value):
        return cls.tidy_name(value).translate(str.maketrans({"I": "ı", "İ": "i"})).casefold()

    def clean(self):
        super().clean()
        self.name = self.tidy_name(self.name)
        self.key = self.key_for(self.name)
        if not self.name:
            raise ValidationError({"name": "Etiket adı boş bırakılamaz."})
        if Tag.objects.filter(key=self.key).exclude(pk=self.pk).exists():
            raise ValidationError({"name": "Bu etiket zaten var. Mevcut etiketi kullanın."})

    def save(self, *args, **kwargs):
        self.name = self.tidy_name(self.name)
        self.key = self.key_for(self.name)
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"name", "key"}
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Taslak"
        PUBLISHED = "published", "Yayında"

    class Section(models.TextChoices):
        DOSYA = "dosya", "Dosya"
        CEVIRI = "ceviri", "Çeviri"
        TARTISMA = "tartisma", "Tartışma"

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

    tags = models.ManyToManyField(Tag, verbose_name="Etiketler", related_name="articles", blank=True)

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

    @property
    def preview(self):
        if self.image:
            return {"type": "image", "url": self.image.url}
        return social_preview(self.platform, self.url)

    def __str__(self):
        return (
            f"{self.get_platform_display()} — "
            f"{self.title}"
        )

class SitePage(models.Model):
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("Adres kısa adı", unique=True)
    intro = models.TextField("Giriş metni", blank=True)
    content = models.TextField("Sayfa metni", blank=True,
                               help_text="Paragrafları boş satırla ayırın.")
    is_published = models.BooleanField("Yayında", default=True)
    order = models.PositiveIntegerField("Menü sırası", default=0)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Kurumsal sayfa"
        verbose_name_plural = "Kurumsal sayfalar"

    def __str__(self):
        return self.title


class YouTubeVideo(models.Model):
    title = models.CharField("Video başlığı", max_length=200)
    youtube_url = models.URLField(
        "YouTube video bağlantısı", max_length=500,
        validators=[validate_youtube_url],
        help_text="YouTube'daki videonun Paylaş bağlantısını yapıştırın. Normal video, Shorts ve canlı yayın bağlantıları desteklenir.",
    )
    description = models.TextField("Kısa açıklama", blank=True)
    order = models.PositiveIntegerField("Sıralama", default=0, help_text="Küçük sayılar önce gösterilir.")
    is_active = models.BooleanField("Ana sayfada göster", default=True)
    created_at = models.DateTimeField("Eklenme zamanı", auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at", "-id"]
        verbose_name = "YouTube videosu"
        verbose_name_plural = "YouTube videoları"

    @property
    def embed_url(self):
        video_id = youtube_video_id(self.youtube_url)
        return f"https://www.youtube-nocookie.com/embed/{video_id}?playsinline=1" if video_id else ""

    @property
    def watch_url(self):
        video_id = youtube_video_id(self.youtube_url)
        return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""

    def __str__(self):
        return self.title
