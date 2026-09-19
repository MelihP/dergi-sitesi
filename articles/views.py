from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .archive_forms import ArchiveFilterForm
from .models import Article, Concept, Dossier


def published_articles():
    return (
        Article.objects
        .filter(
            status=Article.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )
        .select_related("dossier")
        .order_by(
            "-published_at",
            "-id",
        )
    )


def published_dossiers():
    now = timezone.now()

    return (
        Dossier.objects
        .filter(
            status=Dossier.Status.PUBLISHED,
            published_at__lte=now,
        )
        .annotate(
            published_article_count=Count(
                "articles",
                filter=Q(
                    articles__status=(
                        Article.Status.PUBLISHED
                    ),
                    articles__published_at__lte=now,
                ),
                distinct=True,
            )
        )
        .order_by(
            "order",
            "-published_at",
            "-id",
        )
    )


def home(request):
    published = published_articles()

    section = request.GET.get(
        "bolum",
        "",
    )

    section_title = ""

    if section in Article.Section.values:
        published = published.filter(
            section=section,
        )

        section_title = (
            Article.Section(section).label
        )

    featured = list(
        published.filter(
            is_featured=True,
        )[:5]
    )

    if not featured:
        featured = list(
            published[:1]
        )

    latest = published.exclude(
        pk__in=[
            article.pk
            for article in featured
        ]
    )[:9]

    dossiers = list(
        published_dossiers().filter(
            is_featured=True,
        )[:3]
    )

    if not dossiers:
        dossiers = list(
            published_dossiers()[:3]
        )

    context = {
        "featured": featured,
        "articles": latest,
        "dossiers": dossiers,
        "archive_articles": (
            published.filter(
                is_archive_pick=True,
            )[:6]
        ),
        "concepts": (
            Concept.objects.filter(
                is_active=True,
            )[:8]
        ),
        "section_title": section_title,
    }

    return render(
        request,
        "articles/home.html",
        context,
    )


def dossier_list(request):
    dossiers = published_dossiers()

    paginator = Paginator(
        dossiers,
        9,
    )

    page_obj = paginator.get_page(
        request.GET.get("sayfa")
    )

    return render(
        request,
        "articles/dossier_list.html",
        {
            "page_obj": page_obj,
        },
    )


def dossier_detail(request, slug):
    dossier = get_object_or_404(
        published_dossiers(),
        slug=slug,
    )

    articles = (
        published_articles()
        .filter(
            dossier=dossier,
        )
        .order_by(
            "dossier_order",
            "-published_at",
            "-id",
        )
    )

    paginator = Paginator(
        articles,
        9,
    )

    page_obj = paginator.get_page(
        request.GET.get("sayfa")
    )

    return render(
        request,
        "articles/dossier_detail.html",
        {
            "dossier": dossier,
            "page_obj": page_obj,
        },
    )


def archive(request):
    form = ArchiveFilterForm(
        request.GET,
    )

    articles = published_articles()

    if form.is_valid():
        data = form.cleaned_data

        query = data.get("q")
        section = data.get("bolum")
        start = data.get("baslangic")
        end = data.get("bitis")

        if query:
            articles = articles.filter(
                Q(title__icontains=query)
                | Q(
                    author_name__icontains=query
                )
                | Q(content__icontains=query)
                | Q(
                    dossier__title__icontains=query
                )
            )

        if section:
            articles = articles.filter(
                section=section,
            )

        if start:
            articles = articles.filter(
                published_at__date__gte=start,
            )

        if end:
            articles = articles.filter(
                published_at__date__lte=end,
            )
    else:
        articles = articles.none()

    paginator = Paginator(
        articles,
        9,
    )

    page_obj = paginator.get_page(
        request.GET.get("sayfa")
    )

    params = request.GET.copy()
    params.pop(
        "sayfa",
        None,
    )

    context = {
        "filter_form": form,
        "page_obj": page_obj,
        "querystring": params.urlencode(),
    }

    return render(
        request,
        "articles/archive.html",
        context,
    )


def article_detail(request, slug):
    article = get_object_or_404(
        published_articles(),
        slug=slug,
    )

    related_articles = Article.objects.none()

    if article.dossier:
        related_articles = (
            published_articles()
            .filter(
                dossier=article.dossier,
            )
            .exclude(
                pk=article.pk,
            )
            .order_by(
                "dossier_order",
                "-published_at",
            )[:3]
        )

    return render(
        request,
        "articles/article_detail.html",
        {
            "article": article,
            "related_articles": related_articles,
        },
    )