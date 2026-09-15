from django import forms
from .models import Article


class ArchiveFilterForm(forms.Form):
    q = forms.CharField(
        label="Arama",
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Başlık, yazar veya metinde ara…",
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

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("baslangic")
        end = cleaned_data.get("bitis")

        if start and end and start > end:
            raise forms.ValidationError(
                "Başlangıç tarihi bitiş tarihinden sonra olamaz."
            )

        return cleaned_data