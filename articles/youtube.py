import re
from urllib.parse import parse_qs, urlsplit

from django.core.exceptions import ValidationError


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
SHORT_HOSTS = {"youtu.be", "www.youtu.be"}
EMBED_HOSTS = {"youtube-nocookie.com", "www.youtube-nocookie.com"}


def youtube_video_id(value):
    """Extract a video ID from supported YouTube URLs without fetching the URL."""
    try:
        url = urlsplit(value or "")
        if url.scheme not in {"https", "http"} or url.username or url.password:
            return ""
        host = (url.hostname or "").lower()
        parts = url.path.strip("/").split("/")
        if host in SHORT_HOSTS and len(parts) == 1:
            candidate = parts[0]
        elif host in YOUTUBE_HOSTS and parts == ["watch"]:
            candidate = parse_qs(url.query).get("v", [""])[0]
        elif (host in YOUTUBE_HOSTS and len(parts) == 2
              and parts[0] in {"embed", "shorts", "live"}):
            candidate = parts[1]
        elif host in EMBED_HOSTS and len(parts) == 2 and parts[0] == "embed":
            candidate = parts[1]
        else:
            return ""
    except (ValueError, TypeError):
        return ""
    return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate) else ""


def validate_youtube_url(value):
    if not youtube_video_id(value):
        raise ValidationError(
            "Geçerli bir YouTube video bağlantısı girin. Kanal veya oynatma listesi yerine videonun Paylaş bağlantısını kullanın.",
            code="invalid_youtube_url",
        )
