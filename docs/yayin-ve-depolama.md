# Dergiyi yönetme ve kalıcı depolama

## Kurumsal sayfalar

Migration Hakkımızda, Künye ve Yayın İlkeleri sayfalarını oluşturur. Yönetim panelindeki
**Kurumsal sayfalar** bölümünden başlık, giriş, metin ve menü sırası değiştirilebilir.
Menüde yalnızca Hakkımızda görünür; Künye ve Yayın İlkeleri aynı sayfanın alt bölümleridir.
Mevcut metinler korunur; eski sayfa bağlantıları ilgili alt bölüme yönlendirilir.
Üçüncü başlık da değiştirilebilir; başka sayfalar eklenebilir. Taslak metin veya gerçek
olmayan ekip bilgileri yayımlanmaz; boş sayfalarda içerik hazırlanıyor mesajı görünür.

Hakkımızda için önerilen içerik: derginin amacı, okur kitlesi, ele aldığı konular,
editoryal yaklaşımı ve katkı sunma yolu. Künye için gerçek yayıncı/sorumlu kişi,
yayın kurulu ve iletişim bilgileri gerekir. Yayın İlkeleri için kaynak gösterme,
düzeltme/yanıt hakkı, çeviri izinleri ve yazı değerlendirme usulü açıklanabilir.
Sendika.org metni burada kopyalanmadı veya incelenmiş gibi aktarılmadı.

## Dosya kütüphanesi

1. Yönetim panelinde **Dosyalar → Ekle**: örneğin “Emek”, “Kent”, “Ekoloji”.
2. Başlık, açıklama, isteğe bağlı kapak ve yayın durumunu belirleyin.
3. Aynı dosya formunda **Bu dosyadaki yazılar → Yeni bir yazı ekle** ile yazı başlığını, yazarı ve metni girin. Tek dosyaya birden fazla yazı ekleyip birlikte kaydedebilirsiniz.
   Alternatif: **Yazılar → Ekle** ekranındaki “Bağlı olduğu dosya” alanından dosyayı seçin.
4. “Dosya içindeki sıralama” alanıyla içindekiler sırasını belirleyin.
5. Dosya ve yazı ayrı ayrı yayında olmalı; ileri tarihli içerik zamanı gelmeden görünmez.

Çeviri ve tartışma yazıları da dosyalara bağlanabilir. “Dosya” bölümündeki yazılar için
panel dosya seçimini zorunlu tutar. Mevcut bağlantısız yazılar otomatik olarak bir dosyaya
atanmadı: hangi dosyaya ait olduklarına editör karar vermeli. Dosya silmek yazıları silmez.

Ana sayfa slider'ı seçili bölümdeki son eklenen, yayımlanmış en fazla beş yazıyı gösterir.
Manşet işaretine ihtiyaç duymaz. Yazı yokken slider düzeninde bir karşılama alanı görünür;
tek yazıda geçiş yapılmaz, iki yazıdan itibaren otomatik dönüş başlar. Otomatik geçiş altı saniyedir; oklar, noktalar ve durdurma
butonu vardır. Fare üstündeyken, klavye odağı içindeyken veya hareket azaltma tercihi
etkinken geçiş durur. Görseller kırpılmadan gösterilir.

## Kaybolan yazı ve görseller

Yazı metni veritabanındadır; kapak dosyası ayrı medya depolamasındadır. Kodda belirli
bir süreden sonra bunları silen işlem bulunmadı. DATABASE_URL yoksa SQLite dosyası,
CLOUDINARY_URL yoksa media klasörü kullanılıyor. Geçici sunucu diski yeniden oluşturulursa
bu veriler kaybolur. Canlı barındırma ayarları görülmeden kesin neden doğrulanamaz.

### Önerilen üretim yapılandırması

- Kalıcı PostgreSQL oluşturun ve sunucunun güvenli ortam ayarlarında DATABASE_URL tanımlayın.
- Cloudinary hesabının CLOUDINARY_URL değerini sunucunun güvenli ortam ayarlarına girin.
  Mevcut Cloudinary backend'i yeni yüklemeleri burada saklar.
- DEBUG=False ve güçlü, özel SECRET_KEY kullanın.
- `python manage.py check --deploy` çalıştırın. build.sh bu kontrolü migration'dan önce yapar.
- `python manage.py migrate --noinput` ve `python manage.py collectstatic --noinput` çalıştırın.
- Uygulama başlangıcı: `gunicorn config.wsgi:application`.

Yeni kontrol, DEBUG=False iken kalıcılığı beyan edilmemiş SQLite veya yerel medya için
build'i durdurur. Bu kontrol disk sağlayıcısının gerçek kalıcılığını kendi başına doğrulayamaz.

### Kalıcı disk alternatifi

Sağlayıcıda gerçek bir kalıcı volume bağladıktan sonra SQLITE_PATH ve MEDIA_ROOT değerlerini
bu volume altındaki dizinlere ayarlayın. Dizinler uygulama kullanıcısı tarafından yazılabilir
olmalı. İlgili kalıcılığı SQLITE_STORAGE_PERSISTENT=True ve MEDIA_STORAGE_PERSISTENT=True
ile beyan edin. Bu değişkenler disk oluşturmaz; geçici diski kalıcı yapmaz.
PostgreSQL çoklu instance kullanımı için daha uygundur.

DEBUG=False iken Django medya dosyalarını sunmaz. Yerel kalıcı medya kullanılıyorsa
web sunucusunda /media/ için ayrıca sunum yapılandırın; WhiteNoise yalnızca statik
uygulama dosyalarını sunar. Cloudinary medya URL'lerini kendi üzerinden sunar.

### Mevcut verileri koruma ve taşıma

Yeni veritabanı URL'si veya depolama servisi tanımlamak mevcut verileri otomatik taşımaz.
Canlı sistemi değiştirmeden önce veritabanı ve media klasörünün yedeğini alın; yazma işlemlerini
geçici durdurup mevcut verileri hedefe taşıyın ve karşılaştırın. Eski medya dosyalarını yeni
backend'e taşıyıp modeldeki dosya adlarını/URL'lerini doğrulayın. Yedeği doğrulamadan eski
veritabanını veya volume'u silmeyin. Sunucudan daha önce silinmiş veriler için sağlayıcı
veya başka bir yedek gerekir; kod değişikliği silinmiş dosyayı geri getirmez.

Dağıtımdan sonra deneme yazısı ve kapak yükleyin; hem yeniden başlatma hem yeni dağıtım
sonrasında yazı kaydı, metni ve görsel URL'sinin erişilebilir olduğunu doğrulayın.
Bu çalışma canlı PostgreSQL/Cloudinary erişimi veya gerçek sunucuda yeniden dağıtım testi yapmadı.

## Diğer öneriler

- Sosyal bağlantılar şu anda Yeni Yaşam hesaplarına yönleniyor; derginin gerçek hesaplarıyla doğrulayın.
- “Dergi” adı, logo, iletişim adresi ve künye bilgilerini yayın kimliğiyle tamamlayın.
- Düzenli veritabanı/medya yedeği ve geri yükleme denemesi planlayın.
- Özgün Hakkımızda metni, yayın ilkeleri ve yazı gönderim koşulları hazırlayın.

## Yüzen sosyal medya paneli

Sağ alttaki yuvarlak düğme bütün sayfalarda görünür. X ve Instagram sekmeleri,
**Sosyal medya gönderileri** yönetim bölümündeki son eklenen beş aktif gönderiyi gösterir.
Başlık, açıklama, görsel ve gönderinin tam bağlantısını buradan ekleyin. Pasif gönderiler
okurlara gösterilmez. Panel sosyal ağlardan otomatik veri çekmez; bunun için hesap yetkileri
ve resmi API entegrasyonu gerekir. Mevcut profil bağlantıları Yeni Yaşam hesaplarıdır.
