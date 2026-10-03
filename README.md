# Dergi sitesi

Python 3.13 / Django 5.2 tabanlı dergi uygulaması.

## Yerel çalıştırma

Python 3.13 ile bir sanal ortam oluşturun (`python -m venv .venv`), etkinleştirin ve:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py test
python manage.py runserver
```

Yönetici hesabı için `python manage.py createsuperuser` çalıştırın.
SQLite ve yerel medya varsayılan yerel geliştirme depolamasıdır.

Kurumsal sayfalar, dosya kütüphanesi, slider, sosyal panel ve kalıcı üretim depolaması
hakkında [yayın ve depolama rehberini](docs/yayin-ve-depolama.md) okuyun.
Arşiv kaynak dosyaları içerir; sanal ortam, yerel veritabanı, medya ve gizli ortam ayarları dahil değildir.
