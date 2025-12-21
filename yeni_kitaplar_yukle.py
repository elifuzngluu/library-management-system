"""
Türkçe Kitap Veri Seti - Tablo Kolonlarına Uygun
Kolonlar: ID, Kitap Adı, ISBN, Yayınevi, Yazarlar,Tür, Stok
"""
import db_connect as db

# Türkçe kitap veri seti - Yeni kitaplar (çakışma olmaması için farklı ISBN'ler)
turkce_kitaplar_yeni = [
    {
        'baslik': 'Sefiller',
        'yazar': 'Victor Hugo',
        'yayinevi': 'İş Bankası Kültür Yayınları',
        'isbn': '9789754584394',
        'yil': 1862,
        'tur': 'Klasik'
    },
    {
        'baslik': '1984',
        'yazar': 'George Orwell',
        'yayinevi': 'Can Yayınları',
        'isbn': '9789750718533',
        'yil': 1949,
        'tur': 'Distopya'
    },
    {
        'baslik': 'Hayvan Çiftliği',
        'yazar': 'George Orwell',
        'yayinevi': 'Can Yayınları',
        'isbn': '9789750718571',
        'yil': 1945,
        'tur': 'Distopya'
    },
    {
        'baslik': 'Anna Karenina',
        'yazar': 'Lev Tolstoy',
        'yayinevi': 'İş Bankası Kültür Yayınları',
        'isbn': '9786053607427',
        'yil': 1877,
        'tur': 'Klasik'
    },
    {
        'baslik': 'Küçük Prens',
        'yazar': 'Antoine de Saint-Exupéry',
        'yayinevi': 'Can Yayınları',
        'isbn': '9789750718564',
        'yil': 1943,
        'tur': 'Çocuk'
    },
    {
        'baslik': 'Vadideki Zambak',
        'yazar': 'Honoré de Balzac',
        'yayinevi': 'İş Bankası Kültür Yayınları',
        'isbn': '9786053604228',
        'yil': 1835,
        'tur': 'Klasik'
    },
    {
        'baslik': 'İstanbul Hatırası',
        'yazar': 'Ahmet Ümit',
        'yayinevi': 'Everest Yayınları',
        'isbn': '9789752896062',
        'yil': 2010,
        'tur': 'Polisiye'
    },
    {
        'baslik': 'Beyoğlu Rapsodisi',
        'yazar': 'Ahmet Ümit',
        'yayinevi': 'Everest Yayınları',
        'isbn': '9789752896758',
        'yil': 2003,
        'tur': 'Polisiye'
    },
    {
        'baslik': 'Medcezir',
        'yazar': 'Buket Uzuner',
        'yayinevi': 'Everest Yayınları',
        'isbn': '9789752894327',
        'yil': 2000,
        'tur': 'Roman'
    },
    {
        'baslik': 'Aşk',
        'yazar': 'Elif Şafak',
        'yayinevi': 'Doğan Kitap',
        'isbn': '9786050914641',
        'yil': 2009,
        'tur': 'Roman'
    },
    {
        'baslik': 'Baba ve Piç',
        'yazar': 'Elif Şafak',
        'yayinevi': 'Doğan Kitap',
        'isbn': '9786050914634',
        'yil': 2006,
        'tur': 'Roman'
    },
    {
        'baslik': 'Kimse Bilmez Beni',
        'yazar': 'Hakan Günday',
        'yayinevi': 'Doğan Kitap',
        'isbn': '9786050926996',
        'yil': 2015,
        'tur': 'Roman'
    },
    {
        'baslik': 'Zaman Makinesi',
        'yazar': 'H. G. Wells',
        'yayinevi': 'İthaki Yayınları',
        'isbn': '9786053755258',
        'yil': 1895,
        'tur': 'Bilim Kurgu'
    },
    {
        'baslik': 'Frankenstein',
        'yazar': 'Mary Shelley',
        'yayinevi': 'İthaki Yayınları',
        'isbn': '9786053753612',
        'yil': 1818,
        'tur': 'Klasik'
    },
    {
        'baslik': 'Cesur Yeni Dünya',
        'yazar': 'Aldous Huxley',
        'yayinevi': 'İthaki Yayınları',
        'isbn': '9786053751861',
        'yil': 1932,
        'tur': 'Distopya'
    },
    {
        'baslik': 'Dokuzuncu Hariciye Koğuşu',
        'yazar': 'Peyami Safa',
        'yayinevi': 'Ötüken Neşriyat',
        'isbn': '9789754370652',
        'yil': 1930,
        'tur': 'Roman'
    },
    {
        'baslik': 'Rüya',
        'yazar': 'Peyami Safa',
        'yayinevi': 'Ötüken Neşriyat',
        'isbn': '9789754370669',
        'yil': 1924,
        'tur': 'Roman'
    },
    {
        'baslik': 'Kara Kitap',
        'yazar': 'Orhan Pamuk',
        'yayinevi': 'İletişim Yayınları',
        'isbn': '9789750502668',
        'yil': 1990,
        'tur': 'Roman'
    },
    {
        'baslik': 'Benim Adım Kırmızı',
        'yazar': 'Orhan Pamuk',
        'yayinevi': 'İletişim Yayınları',
        'isbn': '9789750503818',
        'yil': 1998,
        'tur': 'Roman'
    },
    {
        'baslik': 'Cevdet Bey ve Oğulları',
        'yazar': 'Orhan Pamuk',
        'yayinevi': 'İletişim Yayınları',
        'isbn': '9789750501852',
        'yil': 1982,
        'tur': 'Roman'
    },
    {
        'baslik': 'Aylak Adam',
        'yazar': 'Yusuf Atılgan',
        'yayinevi': 'Yapı Kredi Yayınları',
        'isbn': '9789750803291',
        'yil': 1959,
        'tur': 'Roman'
    },
    {
        'baslik': 'Anayurt Oteli',
        'yazar': 'Yusuf Atılgan',
        'yayinevi': 'Yapı Kredi Yayınları',
        'isbn': '9789750803307',
        'yil': 1973,
        'tur': 'Roman'
    },
    {
        'baslik': 'Masumiyet Müzesi',
        'yazar': 'Orhan Pamuk',
        'yayinevi': 'İletişim Yayınları',
        'isbn': '9789750509445',
        'yil': 2008,
        'tur': 'Roman'
    },
    {
        'baslik': 'Şu Çılgın Türkler',
        'yazar': 'Turgut Özakman',
        'yayinevi': 'Bilgi Yayınevi',
        'isbn': '9789754705850',
        'yil': 2005,
        'tur': 'Tarih'
    },
    {
        'baslik': 'Nutuk',
        'yazar': 'Mustafa Kemal Atatürk',
        'yayinevi': 'Türk Dil Kurumu',
        'isbn': '9789751617736',
        'yil': 1927,
        'tur': 'Tarih'
    }
]

def yeni_kitaplar_yukle():
    """Yeni Türkçe kitap veri setini veritabanına yükler"""
    
    print("=" * 80)
    print("YENİ TÜRKÇE KİTAP VERİ SETİ YÜKLENİYOR")
    print("=" * 80)
    
    # 1. Yazarları ekle
    print("\n📝 Yazarlar ekleniyor...")
    yazar_ekleme = {}
    
    for kitap in turkce_kitaplar_yeni:
        yazar_ad = kitap['yazar'].strip()
        if yazar_ad not in yazar_ekleme:
            parts = yazar_ad.split()
            ad = parts[0]
            soyad = ' '.join(parts[1:]) if len(parts) > 1 else ""
            
            sonuc = db.yazar_ekle(ad, soyad)
            yazar_ekleme[yazar_ad] = sonuc
            
            if sonuc.get('durum') == 'Başarılı':
                print(f"  ✅ {yazar_ad}")
            else:
                print(f"  ℹ️  {yazar_ad} (zaten var)")
    
    # Yazarları veritabanından çek
    yazar_listesi = db.yazarlari_getir()
    yazar_mapping = {}
    for yazar_db in yazar_listesi:
        yazar_mapping[yazar_db[1].strip()] = yazar_db[0]
    
    print(f"\n✅ {len(yazar_mapping)} yazar hazır")
    
    # 2. Yayınevlerini ekle
    print("\n🏢 Yayınevleri ekleniyor...")
    yayinevi_ekleme = {}
    
    for kitap in turkce_kitaplar_yeni:
        yayinevi_ad = kitap['yayinevi'].strip()
        if yayinevi_ad not in yayinevi_ekleme:
            sonuc = db.yayinevi_ekle(yayinevi_ad)
            yayinevi_ekleme[yayinevi_ad] = sonuc
            
            if sonuc.get('durum') == 'Başarılı':
                print(f"  ✅ {yayinevi_ad}")
            else:
                print(f"  ℹ️  {yayinevi_ad} (zaten var)")
    
    # Yayınevlerini veritabanından çek
    yayinevi_listesi = db.yayinevlerini_getir()
    yayinevi_mapping = {}
    for yayinevi_db in yayinevi_listesi:
        yayinevi_mapping[yayinevi_db[1].strip()] = yayinevi_db[0]
    
    print(f"\n✅ {len(yayinevi_mapping)} yayınevi hazır")
    
    # 3. türleri ekle
    print("\n📚 Türler ekleniyor...")
    turler = set([k['tur'] for k in turkce_kitaplar_yeni])
    
    for tur in turler:
        sonuc = db.tur_ekle(tur)
        if sonuc.get('durum') == 'Başarılı':
            print(f"  ✅ {tur}")
        else:
            print(f"  ℹ️  {tur} (zaten var)")
    
    # Türleri veritabanından çek
    tur_listesi = db.turleri_getir()
    tur_mapping = {}
    for tur_db in tur_listesi:
        tur_mapping[tur_db[1].strip()] = tur_db[0]
    
    print(f"\n✅ {len(tur_mapping)} tür hazır")

    # 4. Kitapları ekle
    print("\n" + "=" * 80)
    print("KİTAPLAR EKLENİYOR")
    print("=" * 80)
    
    basarili = 0
    hatali = 0
    atlanan = 0
    
    for kitap in turkce_kitaplar_yeni:
        try:
            # Önce kitap var mı kontrol et
            mevcut = db.kitap_ara(kitap['baslik'])
            if len(mevcut) > 0:
                print(f"⏭️  Atlandı (zaten var): {kitap['baslik']}")
                atlanan += 1
                continue
            
            yazar_tam_ad = kitap['yazar'].strip()
            yayinevi_ad = kitap['yayinevi'].strip()
            tur_ad = kitap['tur'].strip()
            
            if yazar_tam_ad not in yazar_mapping:
                print(f"❌ Yazar bulunamadı: {yazar_tam_ad}")
                hatali += 1
                continue
            
            yazar_ids = [yazar_mapping[yazar_tam_ad]]
            yayinevi_ids = []
            if yayinevi_ad in yayinevi_mapping:
                yayinevi_ids = [yayinevi_mapping[yayinevi_ad]]
            
            tur_id = tur_mapping.get(tur_ad)
            basim_tarihi = f"{kitap['yil']}-01-01"
            
            sonuc = db.kitap_ekle(
                ad=kitap['baslik'],
                isbn=kitap['isbn'],
                basim_tarihi=basim_tarihi,
                baski_sayisi=1,
                yazar_ids=yazar_ids,
                yayinevi_ids=yayinevi_ids,
                tur_id=tur_id,
                kopya_sayisi=5  # Her kitaptan 5 kopya
            )
            
            if sonuc.get('durum') == 'Başarılı':
                basarili += 1
                print(f"✅ [{basarili}/{len(turkce_kitaplar_yeni)}] {kitap['baslik']}")
            else:
                hatali += 1
                print(f"❌ Hata: {kitap['baslik']} - {sonuc.get('mesaj', 'Bilinmeyen')[:50]}")
            
        except Exception as e:
            hatali += 1
            print(f"❌ Beklenmeyen hata ({kitap['baslik']}): {str(e)[:50]}")
    
    # 5. Özet
    print("\n" + "=" * 80)
    print("İŞLEM TAMAMLANDI")
    print("=" * 80)
    print(f"✅ Başarılı: {basarili} kitap")
    print(f"⏭️  Atlandı: {atlanan} kitap (zaten vardı)")
    print(f"❌ Hatalı: {hatali} kitap")
    print(f"📊 Toplam İşlenen: {basarili + hatali + atlanan} kitap")
    
    # 6. Test
    print("\n" + "=" * 80)
    print("VERİTABANI DURUMU")
    print("=" * 80)
    
    kitaplar = db.kitaplari_getir()
    print(f"\n📚 Veritabanında Toplam: {len(kitaplar)} kitap")
    
    print(f"\n📖 Son Eklenen 5 Kitap:")
    for i, kitap in enumerate(kitaplar[-5:]):
        print(f"  {i+1}. {kitap[1]}")
        print(f"     Yazar: {kitap[5]}")
        print(f"     Yayınevi: {kitap[6]}")
        print(f"     Tür: {kitap[7] or 'Belirtilmemiş'}")
        print(f"     Stok: {kitap[8]} kopya")
    
    print("\n" + "=" * 80)
    print("🎉 İşlem tamamlandı!")
    print("=" * 80)

if __name__ == "__main__":
    yeni_kitaplar_yukle()