import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ortam değişkenlerinden yönetici hesabı oluşturur."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                "Yönetici bilgileri bulunamadı; işlem atlandı."
            )
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
        )

        user.email = email
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            message = "Yönetici hesabı oluşturuldu."
        else:
            message = "Mevcut yönetici hesabı güncellendi."

        self.stdout.write(self.style.SUCCESS(message))