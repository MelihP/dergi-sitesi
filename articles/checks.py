from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.database, Tags.files, deploy=True)
def persistent_storage_check(app_configs, **kwargs):
    """Prevent production deployments silently relying on ephemeral disk."""
    if settings.DEBUG:
        return []
    errors = []
    if (settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
            and not settings.SQLITE_STORAGE_PERSISTENT):
        errors.append(Error(
            "Üretimde SQLite geçici diskte tutulamaz.",
            hint="DATABASE_URL ile kalıcı PostgreSQL kullanın veya SQLITE_PATH için kalıcı disk bağlayıp SQLITE_STORAGE_PERSISTENT=True ayarlayın.",
            id="articles.E001",
        ))
    if (settings.STORAGES["default"]["BACKEND"] == "django.core.files.storage.FileSystemStorage"
            and not settings.MEDIA_STORAGE_PERSISTENT):
        errors.append(Error(
            "Üretimde yüklenen görseller için kalıcı depolama gerekli.",
            hint="CLOUDINARY_URL ayarlayın veya MEDIA_ROOT için kalıcı disk bağlayıp MEDIA_STORAGE_PERSISTENT=True ayarlayın.",
            id="articles.E002",
        ))
    return errors
