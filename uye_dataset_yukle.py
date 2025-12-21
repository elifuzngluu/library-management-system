"""
Türkçe Üye Veri Seti Yükleyici
Öğrenci, Öğretmen ve Diğer Üyeler için örnek veriler
"""
import db_connect as db
from datetime import datetime, timedelta

# Öğrenci Üyeleri
ogrenci_uyeleri = [
    {
        'tcno': '12345678901',
        'ad': 'Ahmet',
        'soyad': 'Yılmaz',
        'eposta': 'ahmet.yilmaz@ogrenci.com',
        'telno': '5551234567',
        'ogrno': '2024001',
        'sinif': '9-A',
        'okul': 'Atatürk Anadolu Lisesi'
    },
    {
        'tcno': '12345678902',
        'ad': 'Ayşe',
        'soyad': 'Demir',
        'eposta': 'ayse.demir@ogrenci.com',
        'telno': '5551234568',
        'ogrno': '2024002',
        'sinif': '10-B',
        'okul': 'Atatürk Anadolu Lisesi'
    },
    {
        'tcno': '12345678903',
        'ad': 'Mehmet',
        'soyad': 'Kaya',
        'eposta': 'mehmet.kaya@ogrenci.com',
        'telno': '5551234569',
        'ogrno': '2024003',
        'sinif': '11-C',
        'okul': 'Fatih Anadolu Lisesi'
    },
    {
        'tcno': '12345678904',
        'ad': 'Zeynep',
        'soyad': 'Çelik',
        'eposta': 'zeynep.celik@ogrenci.com',
        'telno': '5551234570',
        'ogrno': '2024004',
        'sinif': '9-B',
        'okul': 'Atatürk Anadolu Lisesi'
    },
    {
        'tcno': '12345678905',
        'ad': 'Can',
        'soyad': 'Özkan',
        'eposta': 'can.ozkan@ogrenci.com',
        'telno': '5551234571',
        'ogrno': '2024005',
        'sinif': '10-A',
        'okul': 'Gazi Lisesi'
    },
    {
        'tcno': '12345678906',
        'ad': 'Elif',
        'soyad': 'Arslan',
        'eposta': 'elif.arslan@ogrenci.com',
        'telno': '5551234572',
        'ogrno': '2024006',
        'sinif': '12-A',
        'okul': 'Fatih Anadolu Lisesi'
    },
    {
        'tcno': '12345678907',
        'ad': 'Burak',
        'soyad': 'Şahin',
        'eposta': 'burak.sahin@ogrenci.com',
        'telno': '5551234573',
        'ogrno': '2024007',
        'sinif': '11-B',
        'okul': 'Gazi Lisesi'
    },
    {
        'tcno': '12345678908',
        'ad': 'Selin',
        'soyad': 'Yıldız',
        'eposta': 'selin.yildiz@ogrenci.com',
        'telno': '5551234574',
        'ogrno': '2024008',
        'sinif': '9-C',
        'okul': 'Atatürk Anadolu Lisesi'
    },
    {
        'tcno': '12345678909',
        'ad': 'Emre',
        'soyad': 'Aydın',
        'eposta': 'emre.aydin@ogrenci.com',
        'telno': '5551234575',
        'ogrno': '2024009',
        'sinif': '10-C',
        'okul': 'Fatih Anadolu Lisesi'
    },
    {
        'tcno': '12345678910',
        'ad': 'Deniz',
        'soyad': 'Koç',
        'eposta': 'deniz.koc@ogrenci.com',
        'telno': '5551234576',
        'ogrno': '2024010',
        'sinif': '12-B',
        'okul': 'Gazi Lisesi'
    }
]

# Öğretmen Üyeleri
ogretmen_uyeleri = [
    {
        'tcno': '98765432101',
        'ad': 'Fatma',
        'soyad': 'Öztürk',
        'eposta': 'fatma.ozturk@ogretmen.com',
        'telno': '5559876543',
        'brans': 'Türk Dili ve Edebiyatı',
        'isyeri': 'Atatürk Anadolu Lisesi'
    },
    {
        'tcno': '98765432102',
        'ad': 'Hasan',
        'soyad': 'Karaca',
        'eposta': 'hasan.karaca@ogretmen.com',
        'telno': '5559876544',
        'brans': 'Matematik',
        'isyeri': 'Fatih Anadolu Lisesi'
    },
    {
        'tcno': '98765432103',
        'ad': 'Sevgi',
        'soyad': 'Polat',
        'eposta': 'sevgi.polat@ogretmen.com',
        'telno': '5559876545',
        'brans': 'Fizik',
        'isyeri': 'Gazi Lisesi'
    },
    {
        'tcno': '98765432104',
        'ad': 'Mustafa',
        'soyad': 'Erdoğan',
        'eposta': 'mustafa.erdogan@ogretmen.com',
        'telno': '5559876546',
        'brans': 'Kimya',
        'isyeri': 'Atatürk Anadolu Lisesi'
    },
    {
        'tcno': '98765432105',
        'ad': 'Aylin',
        'soyad': 'Kurt',
        'eposta': 'aylin.kurt@ogretmen.com',
        'telno': '5559876547',
        'brans': 'İngilizce',
        'isyeri': 'Fatih Anadolu Lisesi'
    },
    {
        'tcno': '98765432106',
        'ad': 'İbrahim',
        'soyad': 'Aksoy',
        'eposta': 'ibrahim.aksoy@ogretmen.com',
        'telno': '5559876548',
        'brans': 'Tarih',
        'isyeri': 'Gazi Lisesi'
    },
    {
        'tcno': '98765432107',
        'ad': 'Merve',
        'soyad': 'Yavuz',
        'eposta': 'merve.yavuz@ogretmen.com',
        'telno': '5559876549',
        'brans': 'Biyoloji',
        'isyeri': 'Atatürk Anadolu Lisesi'
    }
]

# Diğer Üyeler (Veliler, Mezunlar, vb.)
diger_uyeler = [
    {
        'tcno': '55555555501',
        'ad': 'Ali',
        'soyad': 'Tekin',
        'eposta': 'ali.tekin@gmail.com',
        'telno': '5553335501',
        'gerekce': 'Veli - Çocuğu okula devam ediyor',
        'gecerlilik': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    },
    {
        'tcno': '55555555502',
        'ad': 'Gül',
        'soyad': 'Acar',
        'eposta': 'gul.acar@gmail.com',
        'telno': '5553335502',
        'gerekce': 'Mezun - 2020 Mezunu',
        'gecerlilik': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    },
    {
        'tcno': '55555555503',
        'ad': 'Kemal',
        'soyad': 'Bulut',
        'eposta': 'kemal.bulut@gmail.com',
        'telno': '5553335503',
        'gerekce': 'Araştırmacı - Tez Çalışması',
        'gecerlilik': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
    },
    {
        'tcno': '55555555504',
        'ad': 'Hacer',
        'soyad': 'Güneş',
        'eposta': 'hacer.gunes@gmail.com',
        'telno': '5553335504',
        'gerekce': 'Veli - İki çocuğu okula devam ediyor',
        'gecerlilik': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    },
    {
        'tcno': '55555555505',
        'ad': 'Osman',
        'soyad': 'Taş',
        'eposta': 'osman.tas@gmail.com',
        'telno': '5553335505',
        'gerekce': 'Yönetici - Okul Müdür Yardımcısı',
        'gecerlilik': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d')
    }
]

def uye_dataset_yukle():
    """Örnek üye veri setini veritabanına yükler"""
    
    print("=" * 80)
    print("ÜYE VERİ SETİ YÜKLENİYOR")
    print("=" * 80)
    
    # 1. Öğrenci Üyeleri Ekle
    print("\n👨‍🎓 Öğrenci Üyeler Ekleniyor...")
    ogrenci_basarili = 0
    ogrenci_hatali = 0
    
    for ogrenci in ogrenci_uyeleri:
        try:
            # Önce üye var mı kontrol et
            mevcut = db.uye_ara(ogrenci['tcno'])
            if len(mevcut) > 0:
                print(f"  ⏭️  Atlandı (zaten var): {ogrenci['ad']} {ogrenci['soyad']}")
                continue
            
            sonuc = db.ogrenci_ekle(
                tcno=ogrenci['tcno'],
                ad=ogrenci['ad'],
                soyad=ogrenci['soyad'],
                eposta=ogrenci['eposta'],
                telno=ogrenci['telno'],
                ogrno=ogrenci['ogrno'],
                sinif_duzeyi=ogrenci['sinif'],
                okul_bilgisi=ogrenci['okul']
            )
            
            if sonuc.get('durum') == 'Başarılı':
                ogrenci_basarili += 1
                print(f"  ✅ [{ogrenci_basarili}/{len(ogrenci_uyeleri)}] {ogrenci['ad']} {ogrenci['soyad']} - {ogrenci['sinif']}")
            else:
                ogrenci_hatali += 1
                print(f"  ❌ Hata: {ogrenci['ad']} {ogrenci['soyad']} - {sonuc.get('mesaj', '')[:50]}")
        
        except Exception as e:
            ogrenci_hatali += 1
            print(f"  ❌ Beklenmeyen hata: {ogrenci['ad']} {ogrenci['soyad']} - {str(e)[:50]}")
    
    print(f"\n✅ Öğrenci Özet: {ogrenci_basarili} başarılı, {ogrenci_hatali} hatalı")
    
    # 2. Öğretmen Üyeleri Ekle
    print("\n👨‍🏫 Öğretmen Üyeler Ekleniyor...")
    ogretmen_basarili = 0
    ogretmen_hatali = 0
    
    for ogretmen in ogretmen_uyeleri:
        try:
            # Önce üye var mı kontrol et
            mevcut = db.uye_ara(ogretmen['tcno'])
            if len(mevcut) > 0:
                print(f"  ⏭️  Atlandı (zaten var): {ogretmen['ad']} {ogretmen['soyad']}")
                continue
            
            sonuc = db.ogretmen_ekle(
                tcno=ogretmen['tcno'],
                ad=ogretmen['ad'],
                soyad=ogretmen['soyad'],
                eposta=ogretmen['eposta'],
                telno=ogretmen['telno'],
                brans=ogretmen['brans'],
                isyeri=ogretmen['isyeri']
            )
            
            if sonuc.get('durum') == 'Başarılı':
                ogretmen_basarili += 1
                print(f"  ✅ [{ogretmen_basarili}/{len(ogretmen_uyeleri)}] {ogretmen['ad']} {ogretmen['soyad']} - {ogretmen['brans']}")
            else:
                ogretmen_hatali += 1
                print(f"  ❌ Hata: {ogretmen['ad']} {ogretmen['soyad']} - {sonuc.get('mesaj', '')[:50]}")
        
        except Exception as e:
            ogretmen_hatali += 1
            print(f"  ❌ Beklenmeyen hata: {ogretmen['ad']} {ogretmen['soyad']} - {str(e)[:50]}")
    
    print(f"\n✅ Öğretmen Özet: {ogretmen_basarili} başarılı, {ogretmen_hatali} hatalı")
    
    # 3. Diğer Üyeler Ekle
    print("\n👥 Diğer Üyeler Ekleniyor...")
    diger_basarili = 0
    diger_hatali = 0
    
    for diger in diger_uyeler:
        try:
            # Önce üye var mı kontrol et
            mevcut = db.uye_ara(diger['tcno'])
            if len(mevcut) > 0:
                print(f"  ⏭️  Atlandı (zaten var): {diger['ad']} {diger['soyad']}")
                continue
            
            sonuc = db.diger_uye_ekle(
                tcno=diger['tcno'],
                ad=diger['ad'],
                soyad=diger['soyad'],
                eposta=diger['eposta'],
                telno=diger['telno'],
                gerekce=diger['gerekce'],
                gecerlilik_tarihi=diger['gecerlilik']
            )
            
            if sonuc.get('durum') == 'Başarılı':
                diger_basarili += 1
                print(f"  ✅ [{diger_basarili}/{len(diger_uyeler)}] {diger['ad']} {diger['soyad']} - {diger['gerekce'][:30]}")
            else:
                diger_hatali += 1
                print(f"  ❌ Hata: {diger['ad']} {diger['soyad']} - {sonuc.get('mesaj', '')[:50]}")
        
        except Exception as e:
            diger_hatali += 1
            print(f"  ❌ Beklenmeyen hata: {diger['ad']} {diger['soyad']} - {str(e)[:50]}")
    
    print(f"\n✅ Diğer Üye Özet: {diger_basarili} başarılı, {diger_hatali} hatalı")
    
    # 4. Genel Özet
    print("\n" + "=" * 80)
    print("İŞLEM TAMAMLANDI")
    print("=" * 80)
    toplam_basarili = ogrenci_basarili + ogretmen_basarili + diger_basarili
    toplam_hatali = ogrenci_hatali + ogretmen_hatali + diger_hatali
    
    print(f"\n📊 Özet:")
    print(f"  • Öğrenci: {ogrenci_basarili} başarılı")
    print(f"  • Öğretmen: {ogretmen_basarili} başarılı")
    print(f"  • Diğer Üye: {diger_basarili} başarılı")
    print(f"  ─────────────────────")
    print(f"  ✅ Toplam Başarılı: {toplam_basarili}")
    print(f"  ❌ Toplam Hatalı: {toplam_hatali}")
    
    # 5. Test - Üye Listesi
    print("\n" + "=" * 80)
    print("VERİTABANI DURUMU")
    print("=" * 80)
    
    uyeler = db.uyeleri_getir()
    print(f"\n📋 Toplam Üye Sayısı: {len(uyeler)}")
    
    if len(uyeler) > 0:
        print(f"\n👥 İlk 5 Üye:")
        for i, uye in enumerate(uyeler[:5]):
            print(f"  {i+1}. {uye[0]} {uye[1]} - Üye No: {uye[2]}")
    
    # 6. Arama Testi
    print(f"\n🔍 Arama Testleri:")
    test_aramalar = ["Ahmet", "Yılmaz", "Fatma", "Öğretmen"]
    for arama in test_aramalar:
        sonuc = db.uye_ara(arama)
        print(f"  • '{arama}': {len(sonuc)} sonuç")
    
    print("\n" + "=" * 80)
    print("🎉 Üye veri seti başarıyla yüklendi!")
    print("=" * 80)

if __name__ == "__main__":
    uye_dataset_yukle()