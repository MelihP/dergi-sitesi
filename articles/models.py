from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone
from .richtext import render_content


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Taslak"
        PUBLISHED = "published", "Yayında"

    class Section(models.TextChoices):
        DOSYA = "dosya", "Dosya"
        CEVIRI = "ceviri", "Çeviri"
        TARTISMA = "tartisma", "Tartışma ve Yorum"

    title = models.CharField("Başlık", max_length=250)
    slug = models.SlugField("Adres kısa adı", unique=True)
    author_name = models.CharField("Yazar adı", max_length=150)
    summary = models.TextField("Kısa açıklama", blank=True)
    content = models.TextField("Yazı metni")


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
        help_text="Yayındaki yazıda boş bırakılırsa kaydedildiği zaman kullanılır.",
    )

    is_archive_pick = models.BooleanField(
        "Arşivden seçmelerde göster",
        default=False,
    )
    class Meta:
        ordering = ["-created_at", "-id"]
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
                    set(kwargs["update_fields"]) | {"published_at"}
                )

        super().save(*args, **kwargs)


    @property
    def formatted_content(self):
        return render_content(self)

    def __str__(self):
        return self.title




class Concept(models.Model):
    name = models.CharField("Kavram", max_length=150)
    description = models.TextField("Açıklama")
    order = models.PositiveIntegerField("Sıralama", default=0)
    is_active = models.BooleanField("Sitede göster", default=True)

    class Meta:
        ordering = ["order", "name"]
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
            URLValidator(schemes=["http", "https"]),
        ],
        help_text="Gönderinin veya videonun tam bağlantısını gir.",
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
        ordering = ["order", "-created_at", "-id"]
        verbose_name = "Sosyal medya gönderisi"
        verbose_name_plural = "Sosyal medya gönderileri"

    def __str__(self):
        return f"{self.get_platform_display()} — {self.title}"