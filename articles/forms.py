from django import forms
from django.template.defaultfilters import linebreaks

from .models import Article
from .richtext import clean_html, plain_text


class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(
        label="Yazı metni",
        widget=forms.Textarea(
            attrs={
                "class": "rich-editor-source",
                "rows": 20,
            }
        ),
        help_text=(
            "Ara başlıklar için H2/H3 kullan. "
            "Değişiklikleri kaydetmeyi unutma."
        ),
    )

    class Meta:
        model = Article
        fields = "__all__"

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css",
                "articles/css/editor.css",
            )
        }

        js = (
            "https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js",
            "articles/js/editor.js",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_bound and self.instance.pk:
            if self.instance.content_html:
                html = self.instance.content_html
            else:
                html = linebreaks(
                    self.instance.content,
                    autoescape=True,
                )

            self.initial["content"] = clean_html(html)

    def clean_content(self):
        html = clean_html(
            self.cleaned_data["content"]
        )

        text = plain_text(html)

        if not text:
            raise forms.ValidationError(
                "Yazı metni boş bırakılamaz."
            )

        self._cleaned_html = html

        return text

    def save(self, commit=True):
        self.instance.content_html = self._cleaned_html

        return super().save(commit=commit)