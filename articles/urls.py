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