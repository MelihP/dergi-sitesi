from django.urls import path

from . import views


app_name = "articles"


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "dosyalar/",
        views.dossier_list,
        name="dossier_list",
    ),

    path(
        "dosya/<slug:slug>/",
        views.dossier_detail,
        name="dossier_detail",
    ),

    path(
        "yazilar/",
        views.archive,
        name="archive",
    ),

    path(
        "yazi/<slug:slug>/",
        views.article_detail,
        name="detail",
    ),
]