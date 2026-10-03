from .models import SocialPost


def social_media(request):
    profile_urls = {
        "x": "https://x.com/yeniyasamnews5",
        "instagram": "https://www.instagram.com/yeniyasamgazetesi/",
        "youtube": "https://www.youtube.com/@yeniyasammedia",
    }

    groups = []

    for platform, label in SocialPost.Platform.choices:
        posts = SocialPost.objects.filter(
            platform=platform,
            is_active=True,
        ).order_by("-created_at", "-id")[:5]

        groups.append({
            "key": platform,
            "label": label,
            "posts": posts,
            "profile_url": profile_urls[platform],
        })

    return {"social_groups": groups}

def institutional_pages(request):
    from .models import SitePage
    return {"institutional_pages": SitePage.objects.filter(slug="hakkimizda", is_published=True)}
