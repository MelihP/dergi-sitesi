from django import forms
from django.utils import timezone

from .models import Article, Tag


class ArchiveFilterForm(forms.Form):
    q = forms.CharField(
        label="Arama",
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Başlık, yazar, metin veya etikette ara…",
            }
        ),
    )

    bolum = forms.ChoiceField(
        label="Kategori",
        required=False,
        choices=[
            ("", "Tüm kategoriler"),
            *Article.Section.choices,
        ],
    )

    etiket = forms.ModelChoiceField(
        label="Etiket", queryset=Tag.objects.none(), required=False, empty_label="Tüm etiketler",
    )

    baslangic = forms.DateField(
        label="Başlangıç tarihi",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"type": "date"},
        ),
    )

    bitis = forms.DateField(
        label="Bitiş tarihi",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"type": "date"},
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["etiket"].queryset = Tag.objects.filter(
            articles__status=Article.Status.PUBLISHED,
            articles__published_at__lte=timezone.now(),
        ).distinct()

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("baslangic")
        end = cleaned_data.get("bitis")

        if start and end and start > end:
            raise forms.ValidationError(
                "Başlangıç tarihi bitiş tarihinden sonra olamaz."
            )

        return cleaned_data
