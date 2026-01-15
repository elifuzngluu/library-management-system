import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def baglanti_kur():
    """PostgreSQL'e yeni bir bağlantı nesnesi döndürür."""
    try:
        conn = psycopg2.connect(
            dbname=DB_ADI,
            user=DB_KULLANICI,
            password=DB_SIFRE,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return None

def sorgu_calistir(sorgu, parametreler=None, fetch_one=False, fetch_all=False):
    """Veritabanında sorgu çalıştırır ve sonuçları döndürür."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}

    try:
        cur = conn.cursor()
        cur.execute(sorgu, parametreler)
        
        if fetch_one or fetch_all:
            sonuclar = cur.fetchone() if fetch_one else cur.fetchall()
            return sonuclar
        else:
            conn.commit()
            return {"durum": "Başarılı", "mesaj": f"{cur.rowcount} satır etkilendi."}

    except psycopg2.Error as e:
        conn.rollback()
        print(f"❌ Sorgu çalıştırma hatası: {e}")
        return {"durum": "Hata", "mesaj": str(e)}
        
    finally:
        if conn:
            cur.close()
            conn.close()


# ========== ÜYE İŞLEMLERİ ==========

def uyeleri_getir():
    """Üye tablosundaki tüm üyeleri getirir."""
    sorgu = """
    SELECT 
        adi, 
        soyadi, 
        uyeno, 
        tcno 
    FROM uye
    ORDER BY adi;
    """
    
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def uye_detay_getir(tcno):
    """Tek bir üyenin tüm detaylı bilgilerini getirir."""
    sorgu = """
    SELECT 
        u.tcno,
        u.adi,
        u.soyadi,
        u.eposta,
        u.telno,
        u.uyeno,
        CASE 
            WHEN og.tcno IS NOT NULL THEN 'Öğrenci'
            WHEN ot.tcno IS NOT NULL THEN 'Öğretmen'
            WHEN du.tcno IS NOT NULL THEN 'Diğer Üye'
            ELSE 'Üye'
        END AS uye_tipi,
        og.ogrno AS ogrenci_no,
        og.sinifduzeyi AS sinif,
        og.okulbilgisi,
        ot.brans AS ogretmen_brans,
        ot.isyeri AS ogretmen_isyeri,
        du.gerekce,
        du.gecerlilikbitistarihi,
        (SELECT COUNT(*) 
         FROM oduncalma o 
         JOIN kopya k ON o.kopyaid = k.kopyaid
         WHERE o.uyetcno = u.tcno AND k.durum = 'Ödünçte') AS aktif_odunc_sayisi,
        (SELECT hesapla_uye_borc(u.tcno)) AS toplam_borc
    FROM uye u
    LEFT JOIN ogrenci og ON u.tcno = og.tcno
    LEFT JOIN ogretmen ot ON u.tcno = ot.tcno
    LEFT JOIN diger_uye du ON u.tcno = du.tcno
    WHERE u.tcno = %s;
    """
    
    sonuc = sorgu_calistir(sorgu, (tcno,), fetch_one=True)
    
    if sonuc:
        return {
            "tcno": sonuc[0],
            "ad": sonuc[1],
            "soyad": sonuc[2],
            "eposta": sonuc[3],
            "telno": sonuc[4],
            "uye_no": sonuc[5],
            "uye_tipi": sonuc[6],
            "ogrenci_no": sonuc[7],
            "sinif": sonuc[8],
            "okul_bilgisi": sonuc[9],
            "ogretmen_brans": sonuc[10],
            "ogretmen_isyeri": sonuc[11],
            "diger_gerekce": sonuc[12],
            "gecerlilik_bitis": sonuc[13],
            "aktif_odunc_sayisi": sonuc[14],
            "toplam_borc": sonuc[15]
        }
    else:
        return None



def ogrenci_ekle(tcno, ad, soyad, eposta, telno, ogrno, sinif_duzeyi, okul_bilgisi=None):
    """Yeni öğrenci üye ekler - Tablo mirası kullanıldığında SADECE alt tabloya eklenir."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # TC kontrolü - uye tablosundan kontrol et (miras sayesinde alt tablolarda da var)
        cur.execute("SELECT COUNT(*) FROM uye WHERE tcno = %s;", (tcno,))
        if cur.fetchone()[0] > 0:
            return {"durum": "Hata", "mesaj": f"Bu TC Kimlik No ({tcno}) zaten sistemde kayıtlı!"}
        
        # SADECE ogrenci tablosuna ekle - uye tablosu miras yoluyla otomatik dolar
        cur.execute("""
            INSERT INTO ogrenci (tcno, adi, soyadi, eposta, telno, ogrno, sinifduzeyi, okulbilgisi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (tcno, ad, soyad, eposta, telno, ogrno, sinif_duzeyi, okul_bilgisi))
        
        # 👇👇👇 YENİ KONTROL: uyelik tablosunda zaten var mı?
        cur.execute("SELECT COUNT(*) FROM uyelik WHERE tcno = %s;", (tcno,))
        if cur.fetchone()[0] == 0:
            # Eğer yoksa ekle
            cur.execute("""
                INSERT INTO uyelik (tcno, max_odunc_limit)
                VALUES (%s, 3);
            """, (tcno,))
        else:
            # Eğer varsa, sadece limiti güncelle (isteğe bağlı)
            cur.execute("""
                UPDATE uyelik SET max_odunc_limit = 3 WHERE tcno = %s;
            """, (tcno,))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Öğrenci üye eklendi: {ad} {soyad}"}
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique" in error_msg.lower():
            return {"durum": "Hata", "mesaj": f"Bu TC Kimlik No ({tcno}) veya Öğrenci No ({ogrno}) zaten kayıtlı!"}
        elif "not-null" in error_msg.lower() or "null value" in error_msg.lower():
            return {"durum": "Hata", "mesaj": f"Gerekli alan eksik: {error_msg}"}
        return {"durum": "Hata", "mesaj": f"Veritabanı hatası: {error_msg}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": f"Veritabanı hatası: {str(e)}"}
        
    finally:
        cur.close()
        conn.close()        


def ogretmen_ekle(tcno, ad, soyad, eposta, telno, brans, isyeri=None):
    """Yeni öğretmen üye ekler - Tablo mirası kullanıldığında SADECE alt tabloya eklenir."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # TC kontrolü
        cur.execute("SELECT COUNT(*) FROM uye WHERE tcno = %s;", (tcno,))
        if cur.fetchone()[0] > 0:
            return {"durum": "Hata", "mesaj": f"Bu TC Kimlik No ({tcno}) zaten sistemde kayıtlı!"}

        # Branş kontrolü
        if not brans or not brans.strip():
            return {"durum": "Hata", "mesaj": "Branş bilgisi boş olamaz!"}
        
        # SADECE ogretmen tablosuna ekle - uye tablosu miras yoluyla otomatik dolar
        cur.execute("""
            INSERT INTO ogretmen (tcno, adi, soyadi, eposta, telno, brans, isyeri)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (tcno, ad, soyad, eposta, telno, brans.strip(), isyeri))
        
        # 👇👇👇 YENİ KONTROL: uyelik tablosunda zaten var mı?
        cur.execute("SELECT COUNT(*) FROM uyelik WHERE tcno = %s;", (tcno,))
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO uyelik (tcno, max_odunc_limit)
                VALUES (%s, 5);
            """, (tcno,))
        else:
            cur.execute("""
                UPDATE uyelik SET max_odunc_limit = 5 WHERE tcno = %s;
            """, (tcno,))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Öğretmen üye eklendi: {ad} {soyad}"}
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique" in error_msg.lower():
            return {"durum": "Hata", "mesaj": f"Bu TC Kimlik No ({tcno}) zaten sistemde kayıtlı!"}
        elif "not-null" in error_msg.lower() or "null value" in error_msg.lower():
            return {"durum": "Hata", "mesaj": f"Gerekli alan eksik: {error_msg}"}
        return {"durum": "Hata", "mesaj": f"Veritabanı hatası: {error_msg}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": f"Veritabanı hatası: {str(e)}"}
        
    finally:
        cur.close()
        conn.close()

def diger_uye_ekle(tcno, ad, soyad, eposta, telno, gerekce, gecerlilik_tarihi):
    """Diğer üye ekler - Tablo mirası kullanıldığında SADECE alt tabloya eklenir."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # TC kontrolü
        cur.execute("SELECT COUNT(*) FROM uye WHERE tcno = %s;", (tcno,))
        if cur.fetchone()[0] > 0:
            return {"durum": "Hata", "mesaj": f"Bu TC Kimlik No ({tcno}) zaten sistemde kayıtlı!"}
        
        # SADECE diger_uye tablosuna ekle - uye tablosu miras yoluyla otomatik dolar
        cur.execute("""
            INSERT INTO diger_uye (tcno, adi, soyadi, eposta, telno, gerekce, gecerlilikbitistarihi)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (tcno, ad, soyad, eposta, telno, gerekce, gecerlilik_tarihi))
        
        # 👇👇👇 YENİ KONTROL: uyelik tablosunda zaten var mı?
        cur.execute("SELECT COUNT(*) FROM uyelik WHERE tcno = %s;", (tcno,))
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO uyelik (tcno, max_odunc_limit)
                VALUES (%s, 2);
            """, (tcno,))
        else:
            cur.execute("""
                UPDATE uyelik SET max_odunc_limit = 2 WHERE tcno = %s;
            """, (tcno,))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Diğer üye eklendi: {ad} {soyad}"}
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique" in error_msg.lower():
            return {"durum": "Hata", "mesaj": f"Bu TC Kimlik No ({tcno}) zaten sistemde kayıtlı!"}
        elif "not-null" in error_msg.lower() or "null value" in error_msg.lower():
            return {"durum": "Hata", "mesaj": f"Gerekli alan eksik: {error_msg}"}
        return {"durum": "Hata", "mesaj": f"Veritabanı hatası: {error_msg}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": f"Veritabanı hatası: {str(e)}"}
        
    finally:
        cur.close()
        conn.close()

def uye_guncelle(tcno, ad, soyad, eposta, telno):
    """Üye bilgilerini günceller (SQL prosedürü kullanır)."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        cur.execute("""
            CALL sp_uye_guncelle(%s, %s, %s, %s, %s);
        """, (tcno, ad, soyad, eposta, telno))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Üye güncellendi: {ad} {soyad}"}
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def uye_sil(tcno):
    """Üye siler (SQL prosedürü kullanır - güvenli, trigger kontrol eder)."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        cur.execute("CALL sp_uye_sil(%s);", (tcno,))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": "Üye silindi."}
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def uye_ara(arama_terimi):
    sorgu = """
    SELECT
        u.adi,
        u.soyadi,
        u.uyeno,
        u.tcno,
        CASE 
            WHEN og.tcno IS NOT NULL THEN 'Öğrenci'
            WHEN ot.tcno IS NOT NULL THEN 'Öğretmen'
            WHEN du.tcno IS NOT NULL THEN 'Diğer'
            ELSE 'Üye'
        END AS tip
    FROM uye u
    LEFT JOIN ogrenci og ON u.tcno = og.tcno
    LEFT JOIN ogretmen ot ON u.tcno = ot.tcno
    LEFT JOIN diger_uye du ON u.tcno = du.tcno
    WHERE 
        u.adi ILIKE %s OR
        u.soyadi ILIKE %s OR
        u.tcno ILIKE %s OR
        CAST(u.uyeno AS TEXT) ILIKE %s
    ORDER BY u.adi, u.soyadi;
    """

    arama = f"%{arama_terimi}%"
    sonuclar = sorgu_calistir(
        sorgu,
        (arama, arama, arama, arama),
        fetch_all=True
    )

    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []

    return sonuclar


def uye_detay_fonksiyon(tcno):
    """Üye detayını getirir (SQL fonksiyonu kullanır)."""
    sorgu = "SELECT * FROM uye_detay(%s);"
    sonuc = sorgu_calistir(sorgu, (tcno,), fetch_one=True)
    
    if sonuc:
        return {
            "tcno": sonuc[0],
            "ad": sonuc[1],
            "soyad": sonuc[2],
            "eposta": sonuc[3],
            "telno": sonuc[4],
            "uye_no": sonuc[5],
            "uye_tipi": sonuc[6],
            "aktif_odunc": sonuc[7],
            "toplam_borc": float(sonuc[8])
        }
    return None


def aktif_uyeler_listesi():
    """Aktif üyeleri (ödüncü veya borcu olan) getirir (SQL fonksiyonu kullanır)."""
    sorgu = "SELECT * FROM aktif_uyeler();"
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
    
    return sonuclar


def borclu_uyeler_listesi():
    """Borçlu üyeleri getirir (SQL fonksiyonu kullanır)."""
    sorgu = "SELECT * FROM borclu_uyeler();"
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
    
    return sonuclar



# ========== KİTAP/MATERYAL İŞLEMLERİ ==========

def kitaplari_getir():
    """Tüm kitapları yazarları, yayınevleri ve TÜRLERİ ile birlikte getirir"""
    conn = baglanti_kur()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                k.materyalno,
                k.ad AS kitap_adi,
                k.isbnno,
                k.basimtarihi,
                k.baskisayisi,
                STRING_AGG(DISTINCT y.ad, ', ') AS yazarlar,
                STRING_AGG(DISTINCT yay.ad, ', ') AS yayinevleri,
                STRING_AGG(DISTINCT t.turadi, ', ') AS turler,
                COUNT(DISTINCT kop.kopyaid) AS stok
            FROM kitap k
            LEFT JOIN kitapyazar ky ON k.materyalno = ky.materyalno
            LEFT JOIN yazar y ON ky.yazarid = y.yazarid
            LEFT JOIN materyalyayinevi my ON k.materyalno = my.materyalno
            LEFT JOIN yayinevi yay ON my.yayinevino = yay.yayinevino
            LEFT JOIN materyaltur mt ON k.materyalno = mt.materyalno
            LEFT JOIN tur t ON mt.turno = t.turno
            LEFT JOIN kopya kop ON k.materyalno = kop.materyalno
            GROUP BY k.materyalno, k.ad, k.isbnno, k.basimtarihi, k.baskisayisi
            ORDER BY k.materyalno;
        """)
        return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Kitaplar getirilemedi: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def kitap_detay_getir(kitap_id):
    """Kitap detaylarını getirir (SQL fonksiyonu ile stok bilgisi)"""
    sorgu = """
    SELECT 
        k.materyalno,
        k.ad AS kitap_adi,
        k.isbnno,
        STRING_AGG(DISTINCT ya.ad, ', ') AS yayinevi,
        k.basimtarihi AS yayin_yili,
        NULL AS sayfa_sayisi,
        NULL AS dil,
        NULL AS raf,
        (SELECT toplam_kopya FROM kitap_stok_durumu(k.materyalno)) AS stok,
        STRING_AGG(DISTINCT y.ad || ' ' || y.soyad, ', ') AS yazarlar,
        STRING_AGG(DISTINCT t.turadi, ', ') AS kategoriler,
        (SELECT COUNT(*) FROM oduncalma o 
         JOIN kopya ko ON o.kopyaid = ko.kopyaid 
         WHERE ko.materyalno = k.materyalno) AS toplam_odunc,
        (SELECT oduncte_kopya FROM kitap_stok_durumu(k.materyalno)) AS oduncte_olan
    FROM kitap k
    LEFT JOIN kitapyazar ky ON k.materyalno = ky.materyalno
    LEFT JOIN yazar y ON ky.yazarid = y.yazarid
    LEFT JOIN materyalyayinevi my ON k.materyalno = my.materyalno
    LEFT JOIN yayinevi ya ON my.yayinevino = ya.yayinevino
    LEFT JOIN materyaltur mt ON k.materyalno = mt.materyalno
    LEFT JOIN tur t ON mt.turno = t.turno
    WHERE k.materyalno = %s
    GROUP BY k.materyalno, k.ad, k.isbnno, k.basimtarihi;
    """
    
    sonuc = sorgu_calistir(sorgu, (kitap_id,), fetch_one=True)
    
    if sonuc:
        return {
            'kitap_id': sonuc[0],
            'kitap_adi': sonuc[1],
            'isbn': sonuc[2],
            'yayinevi': sonuc[3],
            'yayin_yili': sonuc[4],
            'sayfa_sayisi': sonuc[5],
            'dil': sonuc[6],
            'raf': sonuc[7],
            'stok': sonuc[8],
            'yazarlar': sonuc[9],
            'kategoriler': sonuc[10],
            'toplam_odunc': sonuc[11],
            'oduncte_olan': sonuc[12]
        }
    
    return None

def kitap_ekle(ad, isbn, basim_tarihi, baski_sayisi, yazar_ids, yayinevi_ids, tur_id, kopya_sayisi=1):
    """Yeni kitap ekler ve sp_kopya_ekle prosedürü ile kopyalarını oluşturur."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO materyal (ad, basimtarihi)
            VALUES (%s, %s)
            RETURNING materyalno;
        """, (ad, basim_tarihi))
        materyal_no = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO kitap (materyalno, ad, basimtarihi, isbnno, baskisayisi)
            VALUES (%s, %s, %s, %s, %s);
        """, (materyal_no, ad, basim_tarihi, isbn, baski_sayisi))
        
        for yazar_id in yazar_ids:
            cur.execute("""
                INSERT INTO kitapyazar (materyalno, yazarid)
                VALUES (%s, %s);
            """, (materyal_no, yazar_id))
        
        for yayinevi_id in yayinevi_ids:
            cur.execute("""
                INSERT INTO materyalyayinevi (materyalno, yayinevino)
                VALUES (%s, %s);
            """, (materyal_no, yayinevi_id))
        
        # TÜR İLİŞKİSİ EKLE (yazar ve yayınevi gibi)
        if tur_id:
            cur.execute("""
                INSERT INTO materyaltur (materyalno, turno)
                VALUES (%s, %s);
            """, (materyal_no, tur_id))
        
        # SQL Prosedürü ile kopya ekle
        cur.execute("CALL sp_kopya_ekle(%s, %s, %s);", (materyal_no, kopya_sayisi, 'R'))
        
        conn.commit()
        return {"durum": "Başarılı", "kitap_id": materyal_no, "mesaj": f"Kitap eklendi: {ad}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def kitap_ara_detayli(kitap_terimi="", yazar_terimi="", yayinevi_terimi=""):
    """
    Kitap adı, ISBN, yazar ve yayınevine göre detaylı arama yapar.
    
    Args:
        kitap_terimi (str): Kitap adı veya ISBN
        yazar_terimi (str): Yazar adı
        yayinevi_terimi (str): Yayınevi adı
        
    Returns:
        list: [(materyalno, kitap_adi, yazarlar, yayinevi, stok), ...]
    """
    # Dinamik SQL sorgusu oluştur
    sorgu = """
    SELECT DISTINCT
        k.materyalno,
        k.ad AS kitap_adi,
        STRING_AGG(DISTINCT y.ad || ' ' || y.soyad, ', ') AS yazarlar,
        STRING_AGG(DISTINCT ya.ad, ', ') AS yayinevi,
        (SELECT COUNT(*) FROM kopya ko WHERE ko.materyalno = k.materyalno AND ko.durum = 'Rafta') AS stok
    FROM kitap k
    LEFT JOIN kitapyazar ky ON k.materyalno = ky.materyalno
    LEFT JOIN yazar y ON ky.yazarid = y.yazarid
    LEFT JOIN materyalyayinevi my ON k.materyalno = my.materyalno
    LEFT JOIN yayinevi ya ON my.yayinevino = ya.yayinevino
    WHERE 1=1
    """
    
    params = []
    
    # Kitap adı veya ISBN araması
    if kitap_terimi:
        sorgu += " AND (k.ad ILIKE %s OR k.isbnno ILIKE %s)"
        search_term = f"%{kitap_terimi}%"
        params.extend([search_term, search_term])
    
    # Yazar araması
    if yazar_terimi:
        sorgu += " AND (y.ad ILIKE %s OR y.soyad ILIKE %s OR (y.ad || ' ' || y.soyad) ILIKE %s)"
        yazar_search = f"%{yazar_terimi}%"
        params.extend([yazar_search, yazar_search, yazar_search])
    
    # Yayınevi araması
    if yayinevi_terimi:
        sorgu += " AND ya.ad ILIKE %s"
        params.append(f"%{yayinevi_terimi}%")
    
    sorgu += """
    GROUP BY k.materyalno, k.ad
    ORDER BY k.ad
    LIMIT 100;
    """
    
    sonuclar = sorgu_calistir(sorgu, tuple(params) if params else None, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
    
    return sonuclar

def kitap_guncelle(kitap_id, kitap_adi, isbn, yayinevi, yayin_yili, sayfa, dil, stok, raf):
    """Kitap bilgilerini günceller"""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE kitap
            SET ad = %s, isbnno = %s, basimtarihi = %s
            WHERE materyalno = %s;
        """, (kitap_adi, isbn, yayin_yili, kitap_id))
        
        cur.execute("""
            UPDATE materyal
            SET ad = %s, basimtarihi = %s
            WHERE materyalno = %s;
        """, (kitap_adi, yayin_yili, kitap_id))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Kitap güncellendi: {kitap_adi}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def turleri_getir():
    """Tüm türleri getirir"""
    conn = baglanti_kur()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT turno, turadi FROM tur ORDER BY turadi;")
        return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Tür listesi getirilemedi: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def kitap_sil(kitap_id):
    """Kitap ve ilgili kayıtları siler (trigger ödünçte olanları korur)"""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # Trigger otomatik olarak ödünçte olan kopyaları kontrol eder
        cur.execute("DELETE FROM kitap WHERE materyalno = %s;", (kitap_id,))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": "Kitap silindi."}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


# ========== YAZAR VE YAYINEVİ YÖNETİMİ ==========

def yazar_ekle(ad, soyad):
    """Yazar ekler (Basit INSERT ile)."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        # Prosedür yerine direkt INSERT
        cur.execute("""
            INSERT INTO yazar (ad, soyad)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING yazarid;
        """, (ad, soyad))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Yazar eklendi: {ad} {soyad}"}
    except Exception as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def yayinevi_ekle(ad, adres=None, vergino=None):
    """Yayınevi ekler (Basit INSERT ile)."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO yayinevi (ad, adres, vergino)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING yayinevino;
        """, (ad, adres, vergino))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Yayınevi eklendi: {ad}"}
    except Exception as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def tur_ekle(tur_adi):
    """Tür ekler"""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # Önce var mı kontrol et
        cur.execute("SELECT turno FROM tur WHERE LOWER(turadi) = LOWER(%s);", (tur_adi,))
        if cur.fetchone():
            return {"durum": "Mevcut", "mesaj": f"'{tur_adi}' türü zaten mevcut."}
        
        # Yoksa ekle
        cur.execute("""
            INSERT INTO tur (turadi)
            VALUES (%s)
            RETURNING turno;
        """, (tur_adi,))
        
        tur_no = cur.fetchone()[0]
        conn.commit()
        return {"durum": "Başarılı", "tur_id": tur_no, "mesaj": f"Tür eklendi: {tur_adi}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()
        
# ========== YARDIMCI FONKSİYONLAR ==========

def yazarlari_getir():
    """Tüm yazarları getirir."""
    sorgu = "SELECT yazarid, ad || ' ' || soyad AS tam_ad FROM yazar ORDER BY ad;"
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def yayinevlerini_getir():
    """Tüm yayınevlerini getirir."""
    sorgu = "SELECT yayinevino, ad FROM yayinevi ORDER BY ad;"
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def personelleri_getir():
    """Tüm personelleri getirir"""
    sorgu = """
    SELECT tcno, adi, soyadi, sicilno, pozisyon
    FROM personel
    ORDER BY adi, soyadi;
    """
    
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def personel_ekle(tcno, ad, soyad, eposta, telno, sicilno, pozisyon, ev_adresi=None):
    """Yeni personel ekler"""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # Personel tablosuna direkt INSERT
        cur.execute("""
            INSERT INTO personel (tcno, adi, soyadi, eposta, telno, sicilno, pozisyon, evadresi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (tcno, ad, soyad, eposta, telno, sicilno, pozisyon, ev_adresi))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"Personel eklendi: {ad} {soyad}"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()

# ========== SQL FONKSİYONLARINI KULLANAN YENİ FONKSİYONLAR ==========

def kitap_stok_durumu(materyal_no):
    """SQL fonksiyonu ile kitabın stok durumunu getirir."""
    sorgu = "SELECT * FROM kitap_stok_durumu(%s);"
    sonuc = sorgu_calistir(sorgu, (materyal_no,), fetch_one=True)
    
    if sonuc:
        return {
            "toplam_kopya": sonuc[0],
            "musait_kopya": sonuc[1],
            "oduncte_kopya": sonuc[2],
            "kayip_kopya": sonuc[3]
        }
    return None


def geciken_oduncler():
    """SQL fonksiyonu ile gecikmiş ödünçleri getirir."""
    sorgu = "SELECT * FROM geciken_oduncler();"
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
    
    return sonuclar


def hesapla_uye_borc(tcno):
    """SQL fonksiyonu ile üyenin toplam borcunu hesaplar."""
    sorgu = "SELECT hesapla_uye_borc(%s);"
    sonuc = sorgu_calistir(sorgu, (tcno,), fetch_one=True)
    
    if sonuc:
        return float(sonuc[0])
    return 0.0


# ========== SAKLI YORDAM KULLANAN FONKSİYONLAR ==========

def toplu_ceza_ode(uye_tcno):
    """SQL prosedürü ile üyenin tüm cezalarını öder."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        cur.execute("CALL sp_toplu_ceza_ode(%s);", (uye_tcno,))
        conn.commit()
        return {"durum": "Başarılı", "mesaj": "Tüm cezalar ödendi."}
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def kopya_ekle(materyal_no, kopya_sayisi=1, raf_prefix='R'):
    """SQL prosedürü ile materyal için kopya ekler."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        cur.execute("CALL sp_kopya_ekle(%s, %s, %s);", (materyal_no, kopya_sayisi, raf_prefix))
        conn.commit()
        return {"durum": "Başarılı", "mesaj": f"{kopya_sayisi} adet kopya eklendi."}
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


# ========== ÖDÜNÇ İŞLEMLERİ ==========


def aktif_oduncler():
    """Aktif ödünç kayıtlarını getirir - DÜZELTME: DISTINCT eklendi"""
    sorgu = """
    SELECT DISTINCT
        o.oduncid,
        u.adi || ' ' || u.soyadi AS uye_adi,
        m.ad AS materyal_adi,
        o.odunc_tarihi,
        o.iade_tarihi_beklenen,
        k.durum,
        CASE 
            WHEN CURRENT_DATE > o.iade_tarihi_beklenen THEN 'GECİKMİŞ'
            ELSE 'AKTİF'
        END AS durum_bilgisi
    FROM oduncalma o
    JOIN kopya k ON o.kopyaid = k.kopyaid
    JOIN materyal m ON k.materyalno = m.materyalno
    JOIN uye u ON o.uyetcno = u.tcno
    WHERE k.durum = 'Ödünçte'
    ORDER BY o.odunc_tarihi DESC;
    """
    
    sonuclar = sorgu_calistir(sorgu, fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def odunc_verebilir_mi(tcno):
    """Üyenin ödünç alma hakkı olup olmadığını kontrol eder (SQL fonksiyonu ile)."""
    sorgu = """
    SELECT 
        u.max_odunc_limit,
        (SELECT COUNT(*) 
         FROM oduncalma o 
         JOIN kopya k ON o.kopyaid = k.kopyaid
         WHERE o.uyetcno = %s AND k.durum = 'Ödünçte') AS aktif_odunc,
        hesapla_uye_borc(%s) AS toplam_borc
    FROM uyelik u
    WHERE u.tcno = %s;
    """
    
    sonuc = sorgu_calistir(sorgu, (tcno, tcno, tcno), fetch_one=True)
    
    if not sonuc:
        return {"durum": False, "mesaj": "Üyelik bilgisi bulunamadı."}
    
    max_limit, aktif_odunc, toplam_borc = sonuc
    
    if aktif_odunc >= max_limit:
        return {"durum": False, "mesaj": f"Ödünç limiti dolmuş! (Limit: {max_limit})"}
    
    if toplam_borc > 0:
        return {"durum": False, "mesaj": f"Ödenmemiş ceza var: {toplam_borc:.2f} TL"}
    
    return {"durum": True, "mesaj": "Ödünç verilebilir.", "kalan_hak": max_limit - aktif_odunc}


def musait_kopyalar(materyal_no):
    """Belirli bir materyalin müsait kopyalarını getirir."""
    sorgu = """
    SELECT kopyaid, rafno
    FROM kopya
    WHERE materyalno = %s AND durum = 'Rafta'
    ORDER BY kopyaid;
    """
    
    sonuclar = sorgu_calistir(sorgu, (materyal_no,), fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def odunc_ver(uye_tcno, kopya_id, personel_tcno=None):
    """Ödünç verme işlemini SQL prosedürü ile yapar."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # SQL Prosedürünü çağır
        cur.execute("CALL sp_odunc_ver(%s, %s, %s);", (uye_tcno, kopya_id, personel_tcno))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": "Ödünç verme başarılı!"}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def iade_al(odunc_id):
    """İade alma işlemini SQL prosedürü ile yapar."""
    conn = baglanti_kur()
    if conn is None:
        return {"durum": "Hata", "mesaj": "Bağlantı kurulamadı."}
    
    try:
        cur = conn.cursor()
        
        # SQL Prosedürünü çağır
        cur.execute("CALL sp_iade_al(%s);", (odunc_id,))
        
        conn.commit()
        return {"durum": "Başarılı", "mesaj": "İade alındı."}
        
    except psycopg2.Error as e:
        conn.rollback()
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        cur.close()
        conn.close()


def uye_odunc_durumu(tcno):
    """Üyenin aktif ödünç listesini getirir."""
    sorgu = """
    SELECT 
        o.oduncid,
        m.ad AS kitap_adi,
        STRING_AGG(DISTINCT y.ad || ' ' || y.soyad, ', ') AS yazarlar,
        o.odunc_tarihi,
        o.iade_tarihi_beklenen,
        CASE 
            WHEN CURRENT_DATE > o.iade_tarihi_beklenen 
            THEN (CURRENT_DATE - o.iade_tarihi_beklenen)
            ELSE 0
        END AS gecikme_gun,
        CASE 
            WHEN CURRENT_DATE > o.iade_tarihi_beklenen 
            THEN (CURRENT_DATE - o.iade_tarihi_beklenen) * 2.0
            ELSE 0
        END AS potansiyel_ceza
    FROM oduncalma o
    JOIN kopya k ON o.kopyaid = k.kopyaid
    JOIN materyal m ON k.materyalno = m.materyalno
    LEFT JOIN kitap kt ON m.materyalno = kt.materyalno
    LEFT JOIN kitapyazar ky ON kt.materyalno = ky.materyalno
    LEFT JOIN yazar y ON ky.yazarid = y.yazarid
    WHERE o.uyetcno = %s AND k.durum = 'Ödünçte'
    GROUP BY o.oduncid, m.ad, o.odunc_tarihi, o.iade_tarihi_beklenen
    ORDER BY o.odunc_tarihi DESC;
    """
    
    sonuclar = sorgu_calistir(sorgu, (tcno,), fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def uye_ceza_durumu(tcno):
    """Üyenin ödenmemiş cezalarını getirir."""
    sorgu = """
    SELECT 
        c.cezaid,
        c.ceza_miktari,
        c.iade_tarihi_gercek,
        m.ad AS kitap_adi,
        o.odunc_tarihi,
        o.iade_tarihi_beklenen
    FROM ceza c
    JOIN oduncalma o ON c.oduncid = o.oduncid
    JOIN kopya k ON o.kopyaid = k.kopyaid
    JOIN materyal m ON k.materyalno = m.materyalno
    WHERE o.uyetcno = %s AND c.odeme_durumu = FALSE
    ORDER BY c.iade_tarihi_gercek DESC;
    """
    
    sonuclar = sorgu_calistir(sorgu, (tcno,), fetch_all=True)
    
    if isinstance(sonuclar, dict) and sonuclar.get("durum") == "Hata":
        return []
        
    return sonuclar


def ceza_ode(ceza_id):
    """Ceza ödeme işlemi yapar."""
    sorgu = """
    UPDATE ceza
    SET odeme_durumu = TRUE
    WHERE cezaid = %s;
    """
    
    return sorgu_calistir(sorgu, (ceza_id,))
