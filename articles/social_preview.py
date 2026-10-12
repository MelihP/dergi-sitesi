"""Build platform previews without fetching arbitrary URLs on the server."""

import re
from urllib.parse import urlsplit

from .youtube import youtube_video_id


def social_preview(platform, value):
    if platform == "youtube":
        video_id = youtube_video_id(value)
        if video_id:
            return {"type": "image", "url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"}
        return {}

    try:
        url = urlsplit(value or "")
        if (url.scheme not in {"http", "https"} or url.username or url.password
                or url.port not in {None, 80, 443}):
            return {}
        host = (url.hostname or "").lower()
    except (ValueError, TypeError):
        return {}

    if platform == "instagram" and host in {"instagram.com", "www.instagram.com", "m.instagram.com"}:
        match = re.fullmatch(r"/(p|reel|reels|tv)/([A-Za-z0-9_-]{1,100})/?", url.path)
        if match:
            kind = "reel" if match[1] == "reels" else match[1]
            return {"type": "instagram", "url": f"https://www.instagram.com/{kind}/{match[2]}/"}

    if platform == "x" and host in {"x.com", "www.x.com", "mobile.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"}:
        match = re.fullmatch(r"/(?:[A-Za-z0-9_]{1,15}/status|i/(?:web/)?status)/(\d{1,20})(?:/(?:photo|video)/[1-4])?/?", url.path)
        if match:
            return {"type": "x", "url": f"https://twitter.com/i/web/status/{match[1]}"}

    # Profile URLs, private shares and unsupported links remain ordinary links.
    return {}
