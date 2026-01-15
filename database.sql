-- KÜTÜPHANE YÖNETİM SİSTEMİ - 

-- 1. Yazar Tablosu
CREATE TABLE yazar (
    yazarid SERIAL PRIMARY KEY,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL
);

-- 2. Yayınevi Tablosu
CREATE TABLE yayinevi (
    yayinevino SERIAL PRIMARY KEY,
    ad VARCHAR(100) UNIQUE NOT NULL,
    adres VARCHAR(255),
    vergino VARCHAR(20) UNIQUE
);

-- 3. Tür Tablosu
CREATE TABLE tur (
    turno SERIAL PRIMARY KEY,
    turadi VARCHAR(50) UNIQUE NOT NULL
);

-- 4. KİŞİ (Süper Tip)
CREATE TABLE kisi (
    tcno CHAR(11) PRIMARY KEY,
    adi VARCHAR(50) NOT NULL,
    soyadi VARCHAR(50) NOT NULL,
    eposta VARCHAR(100) UNIQUE,
    telno VARCHAR(15)
);

-- 5. PERSONEL (Alt Tip)
CREATE TABLE personel (
    sicilno VARCHAR(20) UNIQUE NOT NULL,
    evadresi VARCHAR(255),
    pozisyon VARCHAR(50),
    PRIMARY KEY (tcno)
) INHERITS (kisi);

-- 6. ÜYE (Alt Tip - Süper Tip)
CREATE TABLE uye (
    VARCHAR(20) UNIQUE NOT NULL,
    PRIMARY KEY (tcno)
) INHERITS (kisi);

-- 7. ÖĞRENCİ (Alt Tip)
CREATE TABLE ogrenci (
    ogrno VARCHAR(20) UNIQUE,
    sinifduzeyi VARCHAR(20),
    okulbilgisi VARCHAR(100),
    PRIMARY KEY (tcno)
) INHERITS (uye);

-- 8. ÖĞRETMEN (Alt Tip)
CREATE TABLE ogretmen (
    brans VARCHAR(50),
    isyeri VARCHAR(100),
    PRIMARY KEY (tcno)
) INHERITS (uye);

-- 9. DİĞER ÜYE (Alt Tip)
CREATE TABLE diger_uye (
    gerekce VARCHAR(255),
    gecerlilikbitistarihi DATE,
    PRIMARY KEY (tcno)
) INHERITS (uye);

-- 10. ÜYELİK Tablosu
CREATE TABLE uyelik (
    uyelikid SERIAL PRIMARY KEY,
    tcno CHAR(11) UNIQUE NOT NULL REFERENCES uye (tcno) ON DELETE CASCADE,
    max_odunc_limit INT DEFAULT 5,
    odunc_gun_suresi INT DEFAULT 15
);

-- 11. MATERYAL (Süper Tip)
CREATE TABLE materyal (
    materyalno SERIAL PRIMARY KEY,
    ad VARCHAR(255) NOT NULL,
    basimtarihi DATE
);

-- 12. KİTAP (Alt Tip)
CREATE TABLE kitap (
    isbnno VARCHAR(20) UNIQUE,
    baskisayisi INT,
    PRIMARY KEY (materyalno)
) INHERITS (materyal);

-- 13. DERGİ (Alt Tip)
CREATE TABLE dergi (
    ciltno VARCHAR(20),
    PRIMARY KEY (materyalno)
) INHERITS (materyal);

-- 14. KİTAP YAZAR (N:M İlişkisi)
CREATE TABLE kitapyazar (
    materyalno INT NOT NULL REFERENCES kitap (materyalno) ON DELETE CASCADE,
    yazarid INT NOT NULL REFERENCES yazar (yazarid) ON DELETE CASCADE,
    PRIMARY KEY (materyalno, yazarid)
);

-- 15. MATERYAL YAYINEVİ (N:M İlişkisi)
CREATE TABLE materyalyayinevi (
    materyalno INT NOT NULL REFERENCES materyal (materyalno) ON DELETE CASCADE,
    yayinevino INT NOT NULL REFERENCES yayinevi (yayinevino) ON DELETE CASCADE,
    PRIMARY KEY (materyalno, yayinevino)
);

-- 16. MATERYAL TÜRÜ (N:M İlişkisi)
CREATE TABLE materyaltur (
    materyalno INT NOT NULL REFERENCES materyal (materyalno) ON DELETE CASCADE,
    turno INT NOT NULL REFERENCES tur (turno) ON DELETE CASCADE,
    PRIMARY KEY (materyalno, turno)
);

-- 17. KOPYA Tablosu
CREATE TABLE kopya (
    kopyaid SERIAL PRIMARY KEY,
    materyalno INT NOT NULL REFERENCES materyal (materyalno) ON DELETE CASCADE,
    rafno VARCHAR(10),
    durum VARCHAR(20) DEFAULT 'Rafta' CHECK (durum IN ('Rafta', 'Ödünçte', 'Kayıp', 'Bakımda')),
    eklenmetarihi DATE DEFAULT CURRENT_DATE
);

-- 18. ÖDÜNÇ ALMA İşlemleri
CREATE TABLE oduncalma (
    oduncid SERIAL PRIMARY KEY,
    kopyaid INT UNIQUE NOT NULL REFERENCES kopya (kopyaid),
    uyetcno CHAR(11) NOT NULL REFERENCES uye (tcno),
    personeltcno CHAR(11) REFERENCES personel (tcno),
    odunc_tarihi DATE DEFAULT CURRENT_DATE,
    iade_tarihi_beklenen DATE NOT NULL
);

-- 19. CEZA Tablosu
CREATE TABLE ceza (
    cezaid SERIAL PRIMARY KEY,
    oduncid INT UNIQUE NOT NULL REFERENCES oduncalma (oduncid) ON DELETE CASCADE,
    iade_tarihi_gercek DATE,
    gecikme_gun INT,
    ceza_miktari DECIMAL(10, 2) DEFAULT 0.00,
    odeme_durumu BOOLEAN DEFAULT FALSE
);

-- ========================================
-- FONKSİYONLAR
-- ========================================

-- Borç miktarını hesaplayan fonksiyon
CREATE OR REPLACE FUNCTION hesapla_uye_borc(p_tcno VARCHAR(11))
RETURNS DECIMAL(10,2)
AS $$
DECLARE
    toplam_borc DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(ceza_miktari), 0)
    INTO toplam_borc
    FROM ceza c
    JOIN oduncalma o ON c.oduncid = o.oduncid
    WHERE o.uyetcno = p_tcno AND c.odeme_durumu = FALSE;
    
    RETURN toplam_borc;
END;
$$ LANGUAGE plpgsql;

-- Kitabın stok durumu fonksiyonu
CREATE OR REPLACE FUNCTION kitap_stok_durumu(p_materyal_no INT)
RETURNS TABLE(
    toplam_kopya BIGINT,
    musait_kopya BIGINT,
    oduncte_kopya BIGINT,
    kayip_kopya BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as toplam_kopya,
        COUNT(*) FILTER (WHERE durum = 'Rafta') as musait_kopya,
        COUNT(*) FILTER (WHERE durum = 'Ödünçte') as oduncte_kopya,
        COUNT(*) FILTER (WHERE durum = 'Kayıp') as kayip_kopya
    FROM kopya
    WHERE materyalno = p_materyal_no;
END;
$$ LANGUAGE plpgsql;

-- Gecikmiş ödünçleri listeleyen fonksiyon
CREATE OR REPLACE FUNCTION geciken_oduncler()
RETURNS TABLE(
    odunc_id INT,
    uye_ad_soyad VARCHAR,
    materyal_adi VARCHAR,
    gecikme_gun INT,
    potansiyel_ceza DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.oduncid,
        (u.adi || ' ' || u.soyadi)::VARCHAR,
        m.ad::VARCHAR,
        (CURRENT_DATE - o.iade_tarihi_beklenen)::INT,
        ((CURRENT_DATE - o.iade_tarihi_beklenen) * 2.0)::DECIMAL(10,2)
    FROM oduncalma o
    JOIN kopya k ON o.kopyaid = k.kopyaid
    JOIN materyal m ON k.materyalno = m.materyalno
    JOIN uye u ON o.uyetcno = u.tcno
    WHERE k.durum = 'Ödünçte' 
    AND CURRENT_DATE > o.iade_tarihi_beklenen
    ORDER BY gecikme_gun DESC;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- STORED PROCEDURES
-- ========================================

CREATE PROCEDURE sp_odunc_ver(
    p_uye_tcno CHARACTER(11),
    p_kopya_id INTEGER,
    p_personel_tcno CHARACTER(11) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_max_limit INT;
    v_aktif_odunc INT;
    v_toplam_borc DECIMAL(10,2);
    v_odunc_suresi INT;
    v_iade_tarihi_beklenen DATE;
    v_kopya_durum VARCHAR(20);
BEGIN
    -- Kopya kontrolü
    SELECT durum INTO v_kopya_durum
    FROM kopya WHERE kopyaid = p_kopya_id;
    
    IF v_kopya_durum IS NULL THEN
        RAISE EXCEPTION 'Kopya bulunamadı!';
    END IF;
    
    IF v_kopya_durum != 'Rafta' THEN
        RAISE EXCEPTION 'Bu kopya şu anda müsait değil! Durum: %', v_kopya_durum;
    END IF;
    
    -- Üyelik bilgisi
    SELECT max_odunc_limit, odunc_gun_suresi
    INTO v_max_limit, v_odunc_suresi
    FROM uyelik WHERE tcno = p_uye_tcno;
    
    IF v_max_limit IS NULL THEN
        RAISE EXCEPTION 'Üyelik bilgisi bulunamadı!';
    END IF;
    
    -- AKTİF ÖDÜNÇ KONTROLÜ (DÜZELTİLDİ)
    -- iade_tarihi NULL olanlar = henüz iade edilmemiş
    SELECT COUNT(*)
    INTO v_aktif_odunc
    FROM oduncalma
    WHERE uyetcno = p_uye_tcno 
      AND iade_tarihi IS NULL;
    
    IF v_aktif_odunc >= v_max_limit THEN
        RAISE EXCEPTION 'Ödünç limiti dolmuş! (Limit: %, Aktif: %)', v_max_limit, v_aktif_odunc;
    END IF;
    
    -- Borç kontrolü
    v_toplam_borc := hesapla_uye_borc(p_uye_tcno);
    
    IF v_toplam_borc > 0 THEN
        RAISE EXCEPTION 'Ödenmemiş ceza var: % TL', v_toplam_borc;
    END IF;
    
    -- Beklenen iade tarihi hesapla
    v_iade_tarihi_beklenen := CURRENT_DATE + v_odunc_suresi;
    
    -- Ödünç kaydı oluştur
    INSERT INTO oduncalma (kopyaid, uyetcno, personeltcno, odunc_tarihi, iade_tarihi_beklenen)
    VALUES (p_kopya_id, p_uye_tcno, p_personel_tcno, CURRENT_DATE, v_iade_tarihi_beklenen);
    
    -- Kopya durumunu güncelle
    UPDATE kopya SET durum = 'Ödünçte' WHERE kopyaid = p_kopya_id;
    
    RAISE NOTICE 'Ödünç verme başarılı! Beklenen iade tarihi: %', v_iade_tarihi_beklenen;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_iade_al(
    p_odunc_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_kopya_id INTEGER;
    v_iade_tarihi_beklenen DATE;
    v_gecikme_gun INT;
    v_ceza_tutari DECIMAL(10,2) := 0;
    v_gunluk_ceza DECIMAL(10,2) := 2.00; -- Günlük 2 TL ceza
BEGIN
    -- Ödünç kaydını kontrol et
    SELECT kopyaid, iade_tarihi_beklenen
    INTO v_kopya_id, v_iade_tarihi_beklenen
    FROM oduncalma
    WHERE oduncid = p_odunc_id AND iade_tarihi IS NULL;
    
    IF v_kopya_id IS NULL THEN
        RAISE EXCEPTION 'Ödünç kaydı bulunamadı veya zaten iade edilmiş!';
    END IF;
    
    -- Gecikme hesapla
    v_gecikme_gun := CURRENT_DATE - v_iade_tarihi_beklenen;
    
    IF v_gecikme_gun > 0 THEN
        v_ceza_tutari := v_gecikme_gun * v_gunluk_ceza;
        
        -- Ceza kaydı oluştur
        INSERT INTO ceza (oduncid, ceza_tutari, ceza_nedeni, olusturulma_tarihi)
        VALUES (p_odunc_id, v_ceza_tutari, 
                'Gecikme cezası (' || v_gecikme_gun || ' gün)', 
                CURRENT_DATE);
        
        RAISE NOTICE 'Gecikme var! % gün gecikme - Ceza: % TL', v_gecikme_gun, v_ceza_tutari;
    ELSE
        RAISE NOTICE 'Zamanında iade edildi. Gecikme yok.';
    END IF;
    
    -- İade tarihini güncelle
    UPDATE oduncalma 
    SET iade_tarihi = CURRENT_DATE
    WHERE oduncid = p_odunc_id;
    
    -- Kopya durumunu güncelle
    UPDATE kopya 
    SET durum = 'Rafta'
    WHERE kopyaid = v_kopya_id;
    
    RAISE NOTICE 'İade alındı. Kopya ID: %', v_kopya_id;
END;
$$;

-- Toplu ceza ödeme prosedürü
CREATE OR REPLACE PROCEDURE sp_toplu_ceza_ode(p_uye_tcno CHAR(11))
LANGUAGE plpgsql
AS $$
DECLARE
    v_toplam_borc DECIMAL(10,2);
    v_odenen_ceza_sayisi INT;
BEGIN
    v_toplam_borc := hesapla_uye_borc(p_uye_tcno);
    
    IF v_toplam_borc = 0 THEN
        RAISE NOTICE 'Ödenmemiş ceza bulunmamaktadır.';
        RETURN;
    END IF;
    
    UPDATE ceza c
    SET odeme_durumu = TRUE
    FROM oduncalma o
    WHERE c.oduncid = o.oduncid
    AND o.uyetcno = p_uye_tcno
    AND c.odeme_durumu = FALSE;
    
    GET DIAGNOSTICS v_odenen_ceza_sayisi = ROW_COUNT;
    
    RAISE NOTICE '% adet ceza ödendi. Toplam: % TL', v_odenen_ceza_sayisi, v_toplam_borc;
END;
$$;

-- Kopya ekleme prosedürü
CREATE OR REPLACE PROCEDURE sp_kopya_ekle(
    p_materyal_no INT,
    p_kopya_sayisi INT DEFAULT 1,
    p_raf_prefix VARCHAR(10) DEFAULT 'R'
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_materyal_adi VARCHAR(255);
BEGIN
    SELECT ad INTO v_materyal_adi
    FROM materyal WHERE materyalno = p_materyal_no;
    
    IF v_materyal_adi IS NULL THEN
        RAISE EXCEPTION 'Materyal bulunamadı!';
    END IF;
    
    FOR i IN 1..p_kopya_sayisi LOOP
        INSERT INTO kopya (materyalno, rafno, durum, eklenmetarihi)
        VALUES (
            p_materyal_no,
            p_raf_prefix || '-' || p_materyal_no || '-' || (SELECT COUNT(*) + 1 FROM kopya WHERE materyalno = p_materyal_no),
            'Rafta',
            CURRENT_DATE
        );
    END LOOP;
    
    RAISE NOTICE '% adet kopya eklendi: %', p_kopya_sayisi, v_materyal_adi;
END;
$$;

-- ========================================
-- TRIGGER'LAR
-- ========================================

-- Kopya silme koruma
CREATE OR REPLACE FUNCTION trg_kopya_silme_koruma()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.durum = 'Ödünçte' THEN
        RAISE EXCEPTION 'Ödünçte olan kopya silinemez! Kopya ID: %', OLD.kopyaid;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER kopya_silme_trigger
BEFORE DELETE ON kopya
FOR EACH ROW
EXECUTE FUNCTION trg_kopya_silme_koruma();

-- Üyelik otomatik oluşturma
CREATE OR REPLACE FUNCTION trg_uyelik_otomatik_olustur()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO uyelik (tcno, max_odunc_limit, odunc_gun_suresi)
    VALUES (NEW.tcno, 5, 15)
    ON CONFLICT (tcno) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER uyelik_olustur_trigger
AFTER INSERT ON uye
FOR EACH ROW
EXECUTE FUNCTION trg_uyelik_otomatik_olustur();

-- Üye silme koruma
CREATE OR REPLACE FUNCTION trg_uye_silme_koruma()
RETURNS TRIGGER AS $$
DECLARE
    v_aktif_odunc INT;
    v_odenmemis_borc DECIMAL(10,2);
BEGIN
    SELECT COUNT(*) INTO v_aktif_odunc
    FROM oduncalma o
    JOIN kopya k ON o.kopyaid = k.kopyaid
    WHERE o.uyetcno = OLD.tcno AND k.durum = 'Ödünçte';
    
    IF v_aktif_odunc > 0 THEN
        RAISE EXCEPTION 'Üyenin % adet aktif ödüncü var, silinemez!', v_aktif_odunc;
    END IF;
    
    v_odenmemis_borc := hesapla_uye_borc(OLD.tcno);
    
    IF v_odenmemis_borc > 0 THEN
        RAISE EXCEPTION 'Üyenin % TL ödenmemiş borcu var, silinemez!', v_odenmemis_borc;
    END IF;
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER uye_silme_koruma_trigger
BEFORE DELETE ON uye
FOR EACH ROW
EXECUTE FUNCTION trg_uye_silme_koruma();

-- TC Kimlik numarası kontrol
CREATE OR REPLACE FUNCTION trg_tcno_kontrol()
RETURNS TRIGGER AS $$
BEGIN
    IF LENGTH(NEW.tcno) != 11 THEN
        RAISE EXCEPTION 'TC Kimlik No 11 haneli olmalıdır!';
    END IF;
    
    IF NEW.tcno !~ '^[0-9]{11}$' THEN
        RAISE EXCEPTION 'TC Kimlik No sadece rakam içermelidir!';
    END IF;
    
    IF LEFT(NEW.tcno, 1) = '0' THEN
        RAISE EXCEPTION 'TC Kimlik No 0 ile başlayamaz!';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tcno_kontrol_trigger
BEFORE INSERT OR UPDATE ON kisi
FOR EACH ROW
EXECUTE FUNCTION trg_tcno_kontrol();

-- Tür kontrolü fonksiyonu
CREATE OR REPLACE FUNCTION trg_kitap_tur_kontrol()
RETURNS TRIGGER AS $$
DECLARE
    v_tur_sayisi INT;
BEGIN
    -- Kitap için tür sayısını kontrol et
    SELECT COUNT(*) INTO v_tur_sayisi
    FROM materyaltur
    WHERE materyalno = NEW.materyalno;
    
    -- Eğer tür yoksa uyarı ver
    IF v_tur_sayisi = 0 THEN
        RAISE WARNING 'Kitabın türü belirtilmedi: %', NEW.ad;
        -- Not: Bu sadece uyarı, hata vermek isterseniz:
        -- RAISE EXCEPTION 'Kitap en az bir türe sahip olmalıdır!';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger oluştur
CREATE TRIGGER kitap_tur_kontrol_trigger
AFTER INSERT ON kitap
FOR EACH ROW
EXECUTE FUNCTION trg_kitap_tur_kontrol();


-- 1. ÜYE ARAMA FONKSİYONU
CREATE OR REPLACE FUNCTION uye_ara(p_arama_terimi TEXT)
RETURNS TABLE(
    tcno CHAR(11),
    adi VARCHAR(50),
    soyadi VARCHAR(50),
    eposta VARCHAR(100),
    telno VARCHAR(15),
    uyeno VARCHAR(20),
    uye_tipi TEXT
) AS $$
BEGIN
    RETURN QUERY
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
        END::TEXT AS uye_tipi
    FROM uye u
    LEFT JOIN ogrenci og ON u.tcno = og.tcno
    LEFT JOIN ogretmen ot ON u.tcno = ot.tcno
    LEFT JOIN diger_uye du ON u.tcno = du.tcno
    WHERE 
        u.adi ILIKE '%' || p_arama_terimi || '%' OR
        u.soyadi ILIKE '%' || p_arama_terimi || '%' OR
        u.tcno LIKE '%' || p_arama_terimi || '%' OR
        u.eposta ILIKE '%' || p_arama_terimi || '%' OR
        u.uyeno LIKE '%' || p_arama_terimi || '%'
    ORDER BY u.adi, u.soyadi;
END;
$$ LANGUAGE plpgsql;

-- 2. ÜYE DETAY FONKSİYONU
CREATE OR REPLACE FUNCTION uye_detay(p_tcno CHAR(11))
RETURNS TABLE(
    tcno CHAR(11),
    adi VARCHAR(50),
    soyadi VARCHAR(50),
    eposta VARCHAR(100),
    telno VARCHAR(15),
    uyeno VARCHAR(20),
    uye_tipi TEXT,
    aktif_odunc BIGINT,
    toplam_borc DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
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
        END::TEXT AS uye_tipi,
        (SELECT COUNT(*) 
         FROM oduncalma o 
         JOIN kopya k ON o.kopyaid = k.kopyaid
         WHERE o.uyetcno = u.tcno AND k.durum = 'Ödünçte') AS aktif_odunc,
        hesapla_uye_borc(u.tcno) AS toplam_borc
    FROM uye u
    LEFT JOIN ogrenci og ON u.tcno = og.tcno
    LEFT JOIN ogretmen ot ON u.tcno = ot.tcno
    LEFT JOIN diger_uye du ON u.tcno = du.tcno
    WHERE u.tcno = p_tcno;
END;
$$ LANGUAGE plpgsql;

-- 3. AKTİF ÜYELER LİSTESİ
CREATE OR REPLACE FUNCTION aktif_uyeler()
RETURNS TABLE(
    tcno CHAR(11),
    tam_ad VARCHAR(101),
    uye_tipi TEXT,
    aktif_odunc BIGINT,
    toplam_borc DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.tcno,
        (u.adi || ' ' || u.soyadi)::VARCHAR(101) AS tam_ad,
        CASE 
            WHEN og.tcno IS NOT NULL THEN 'Öğrenci'
            WHEN ot.tcno IS NOT NULL THEN 'Öğretmen'
            WHEN du.tcno IS NOT NULL THEN 'Diğer Üye'
            ELSE 'Üye'
        END::TEXT AS uye_tipi,
        (SELECT COUNT(*) 
         FROM oduncalma o 
         JOIN kopya k ON o.kopyaid = k.kopyaid
         WHERE o.uyetcno = u.tcno AND k.durum = 'Ödünçte') AS aktif_odunc,
        hesapla_uye_borc(u.tcno) AS toplam_borc
    FROM uye u
    LEFT JOIN ogrenci og ON u.tcno = og.tcno
    LEFT JOIN ogretmen ot ON u.tcno = ot.tcno
    LEFT JOIN diger_uye du ON u.tcno = du.tcno
    WHERE EXISTS (
        SELECT 1 FROM oduncalma o 
        JOIN kopya k ON o.kopyaid = k.kopyaid
        WHERE o.uyetcno = u.tcno AND k.durum = 'Ödünçte'
    )
    OR hesapla_uye_borc(u.tcno) > 0
    ORDER BY u.adi, u.soyadi;
END;
$$ LANGUAGE plpgsql;

-- 4. BORÇLU ÜYELER LİSTESİ
CREATE OR REPLACE FUNCTION borclu_uyeler()
RETURNS TABLE(
    tcno CHAR(11),
    tam_ad VARCHAR(101),
    uye_tipi TEXT,
    toplam_borc DECIMAL(10,2),
    odenmemis_ceza_sayisi BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.tcno,
        (u.adi || ' ' || u.soyadi)::VARCHAR(101) AS tam_ad,
        CASE 
            WHEN og.tcno IS NOT NULL THEN 'Öğrenci'
            WHEN ot.tcno IS NOT NULL THEN 'Öğretmen'
            WHEN du.tcno IS NOT NULL THEN 'Diğer Üye'
            ELSE 'Üye'
        END::TEXT AS uye_tipi,
        hesapla_uye_borc(u.tcno) AS toplam_borc,
        (SELECT COUNT(*) 
         FROM ceza c 
         JOIN oduncalma o ON c.oduncid = o.oduncid
         WHERE o.uyetcno = u.tcno AND c.odeme_durumu = FALSE) AS odenmemis_ceza_sayisi
    FROM uye u
    LEFT JOIN ogrenci og ON u.tcno = og.tcno
    LEFT JOIN ogretmen ot ON u.tcno = ot.tcno
    LEFT JOIN diger_uye du ON u.tcno = du.tcno
    WHERE hesapla_uye_borc(u.tcno) > 0
    ORDER BY toplam_borc DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE sp_ogrenci_ekle(
    p_tcno VARCHAR,
    p_ad VARCHAR,
    p_soyad VARCHAR,
    p_eposta VARCHAR,
    p_telno VARCHAR,
    p_ogrno VARCHAR,
    p_sinifduzeyi VARCHAR,
    p_okulbilgisi VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- ÖNCE KİŞİ TABLOSUNA EKLE
    INSERT INTO kisi (tcno, adi, soyadi, eposta, telno)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno);
    
    -- SONRA ÜYE TABLOSUNA EKLE
    INSERT INTO uye (tcno, adi, soyadi, eposta, telno)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno);
    
    -- SON OLARAK ÖĞRENCİ TABLOSUNA EKLE
    INSERT INTO ogrenci (tcno, ogrno, sinifduzeyi, okulbilgisi)
    VALUES (p_tcno, p_ogrno, p_sinifduzeyi, p_okulbilgisi);
    
    RAISE NOTICE 'Öğrenci başarıyla eklendi: % % (TC: %)', p_ad, p_soyad, p_tcno;
    
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Bu TC numarası veya öğrenci numarası ile kayıtlı bir kişi zaten var';
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'İlişkili tablo hatası oluştu';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Öğrenci eklenirken hata: %', SQLERRM;
END;
$$;



CREATE PROCEDURE sp_ogretmen_ekle(
    p_tcno VARCHAR(11),
    p_ad VARCHAR(50),
    p_soyad VARCHAR(50),
    p_eposta VARCHAR(100),
    p_telno VARCHAR(15),
    p_brans VARCHAR(100),
    p_isyeri VARCHAR(200)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_uyeno VARCHAR(20);
    v_max_no INT;
BEGIN
    -- Mevcut en büyük üye numarasını bul (güvenli şekilde)
    SELECT COALESCE(MAX(
        CASE 
            WHEN uyeno ~ '^UYE[0-9]+$' 
            THEN SUBSTRING(uyeno FROM 4)::INT 
            ELSE 0 
        END
    ), 0) INTO v_max_no
    FROM ogretmen;
    
    -- Yeni üye numarası oluştur
    v_uyeno := 'UYE' || LPAD((v_max_no + 1)::TEXT, 5, '0');
    
    -- Kisi tablosuna ekle
    INSERT INTO kisi (tcno, adi, soyadi, eposta, telno)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno);
    
    -- Uye tablosuna ekle
    INSERT INTO uye (tcno, adi, soyadi, eposta, telno)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno);
    
    -- Ogretmen tablosuna ekle
    INSERT INTO ogretmen (tcno, adi, soyadi, eposta, telno, uyeno, brans, isyeri)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno, v_uyeno, p_brans, p_isyeri);
    
    RAISE NOTICE 'Öğretmen başarıyla eklendi: % % - Üye No: %', p_ad, p_soyad, v_uyeno;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Bu TC numarası zaten kayıtlı';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Hata: %', SQLERRM;
END;
$$;


CREATE PROCEDURE sp_diger_uye_ekle(
    p_tcno VARCHAR(11),
    p_ad VARCHAR(50),
    p_soyad VARCHAR(50),
    p_eposta VARCHAR(100),
    p_telno VARCHAR(15),
    p_gerekce TEXT,
    p_gecerlilik DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_uyeno VARCHAR(20);
    v_max_no INT;
BEGIN
    -- Mevcut en büyük üye numarasını bul
    SELECT COALESCE(MAX(
        CASE 
            WHEN uyeno ~ '^UYE[0-9]+$' 
            THEN SUBSTRING(uyeno FROM 4)::INT 
            ELSE 0 
        END
    ), 0) INTO v_max_no
    FROM diger_uye;
    
    -- Yeni üye numarası oluştur
    v_uyeno := 'UYE' || LPAD((v_max_no + 1)::TEXT, 5, '0');
    
    -- Kisi tablosuna ekle
    INSERT INTO kisi (tcno, adi, soyadi, eposta, telno)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno);
    
    -- Uye tablosuna ekle
    INSERT INTO uye (tcno, adi, soyadi, eposta, telno)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno);
    
    -- Diger_uye tablosuna ekle
    INSERT INTO diger_uye (tcno, adi, soyadi, eposta, telno, uyeno, gerekce, gecerlilikbitistarihi)
    VALUES (p_tcno, p_ad, p_soyad, p_eposta, p_telno, v_uyeno, p_gerekce, p_gecerlilik);
    
    RAISE NOTICE 'Diğer üye başarıyla eklendi: % %', p_ad, p_soyad;
END;
$$;


-- 8. ÜYE GÜNCELLEME PROSEDÜRÜ
CREATE OR REPLACE PROCEDURE sp_uye_guncelle(
    p_tcno CHAR(11),
    p_ad VARCHAR(50),
    p_soyad VARCHAR(50),
    p_eposta VARCHAR(100),
    p_telno VARCHAR(15)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Üye bilgilerini güncelle
    UPDATE uye
    SET 
        adi = p_ad,
        soyadi = p_soyad,
        eposta = p_eposta,
        telno = p_telno
    WHERE tcno = p_tcno;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Üye bulunamadı: %', p_tcno;
    END IF;
    
    RAISE NOTICE 'Üye güncellendi: % %', p_ad, p_soyad;
END;
$$;

-- 9. ÜYE SİLME PROSEDÜRÜ
CREATE OR REPLACE PROCEDURE sp_uye_sil(p_tcno CHAR(11))
LANGUAGE plpgsql
AS $$
DECLARE
    v_uye_adi VARCHAR(101);
BEGIN
    -- Üye adını al
    SELECT adi || ' ' || soyadi INTO v_uye_adi
    FROM uye WHERE tcno = p_tcno;
    
    IF v_uye_adi IS NULL THEN
        RAISE EXCEPTION 'Üye bulunamadı: %', p_tcno;
    END IF;
    
    -- Trigger otomatik olarak kontrol eder (aktif ödünç ve borç)
    DELETE FROM uye WHERE tcno = p_tcno;
    
    RAISE NOTICE 'Üye silindi: %', v_uye_adi;
END;
$$;











