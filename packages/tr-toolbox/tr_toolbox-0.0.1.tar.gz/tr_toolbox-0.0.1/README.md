# tr_toolbox

`tr_toolbox`, Türkçe metinler için küçük ve kullanışlı yardımcı araçlar sunan bir Python kütüphanesidir.

İlk özellik olarak Türkçe karakterleri destekleyen bir "slugify" fonksiyonu içerir.

## Kurulum

Paketi PyPI üzerinden `pip` kullanarak kurabilirsiniz (Yayınlandıktan sonra):

pip install tr_toolbox

### Kullanım

Kütüphanenin kullanımı çok basittir. slugify_tr fonksiyonunu import etmeniz yeterlidir.

from tr_toolbox import slugify_tr

metin = "Bu bir İŞ ilanıdır! (Örnek Metin)"
slug = slugify_tr(metin)

print(slug)

Çıktı: bu-bir-is-ilanidir-ornek-metin

### Lisans

Bu proje MIT Lisansı altında dağıtılmaktadır.

MIT License

Copyright (c) 2025