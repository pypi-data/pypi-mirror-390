import re

def slugify_tr(metin):
    """
    Türkçe metni URL dostu bir "slug" (örn: kutuphane-fikri) haline getirir.
    """
    
    # 1. Adım: 'İ' harfini 'I' harfine dönüştür (lower() yapmadan önce)
    metin = metin.replace('İ', 'I')
    
    # 2. Adım: Tüm metni küçük harfe çevir
    metin = metin.lower()
    
    # 3. Adım: Türkçe karakterleri ASCII karşılıkları ile değiştir
    karakter_map = {
        'ı': 'i',
        'ğ': 'g',
        'ü': 'u',
        'ş': 's',
        'ö': 'o',
        'ç': 'c',
    }
    
    for tr_karakter, ascii_karsilik in karakter_map.items():
        metin = metin.replace(tr_karakter, ascii_karsilik)

    # 4. Adım: Boşlukları ve bilinen ayraçları tire (-) yap
    metin = metin.replace(' ', '-')
    metin = metin.replace('_', '-')
    
    # 5. Adım: Sadece harf (a-z), sayı (0-9) ve tire (-) kalsın.
    metin = re.sub(r'[^a-z0-9-]', '', metin)
    
    # 6. Adım: Birden fazla tireyi tek tireye indir
    metin = re.sub(r'-+', '-', metin)
    
    # 7. Adım: Başta veya sonda kalabilecek tireleri temizle
    metin = metin.strip('-')
    
    return metin