# arayüz/kitap_sekmesi.py

import tkinter as tk
from tkinter import ttk, messagebox
import db_connect

class KitapSekmesi:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.kur_arayuz()

    def kur_arayuz(self):
        # Başlık
        ttk.Label(self.parent, text="📚 KİTAP YÖNETİMİ", font=("Arial", 16, "bold")).pack(pady=10)

        # Üst butonlar
        buton_frame = ttk.Frame(self.parent)
        buton_frame.pack(pady=5)

        ttk.Button(buton_frame, text="➕ Yeni Kitap Ekle", command=self.kitap_ekle_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="🔍 Kitap Ara", command=self.kitap_ara_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="🔄 Listeyi Yenile", command=self.listeyi_doldur).pack(side=tk.LEFT, padx=5)

        # Kitap Listesi (Treeview)
        liste_frame = ttk.Frame(self.parent)
        liste_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(liste_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.kitap_listesi = ttk.Treeview(
            liste_frame,
            columns=("ID", "Kitap Adı", "ISBN", "Yayınevi", "Yazarlar", "Tür", "Stok"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(command=self.kitap_listesi.yview)

        # Sütun başlıkları
        self.kitap_listesi.heading("ID", text="ID")
        self.kitap_listesi.heading("Kitap Adı", text="Kitap Adı")
        self.kitap_listesi.heading("ISBN", text="ISBN")
        self.kitap_listesi.heading("Yayınevi", text="Yayınevi")
        self.kitap_listesi.heading("Yazarlar", text="Yazarlar")
        self.kitap_listesi.heading("Tür", text="Tür")
        self.kitap_listesi.heading("Stok", text="Stok")

        # Sütun genişlikleri
        self.kitap_listesi.column("ID", width=50)
        self.kitap_listesi.column("Kitap Adı", width=250)
        self.kitap_listesi.column("ISBN", width=120)
        self.kitap_listesi.column("Yayınevi", width=150)
        self.kitap_listesi.column("Yazarlar", width=200)
        self.kitap_listesi.column("Tür", width=100)
        self.kitap_listesi.column("Stok", width=60)

        self.kitap_listesi.pack(fill="both", expand=True)

        # Çift tıklama ile detay göster
        self.kitap_listesi.bind('<Double-1>', lambda e: self.kitap_detay_goster())

        # Alt butonlar
        alt_buton_frame = ttk.Frame(self.parent)
        alt_buton_frame.pack(pady=5)

        ttk.Button(alt_buton_frame, text="📋 Detay Göster", command=self.kitap_detay_goster).pack(side=tk.LEFT, padx=5)
        ttk.Button(alt_buton_frame, text="✏️ Düzenle", command=self.kitap_duzenle_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(alt_buton_frame, text="🗑️ Sil", command=self.kitap_sil_action).pack(side=tk.LEFT, padx=5)

        # İlk yüklemede listeyi doldur
        self.listeyi_doldur()

    def listeyi_doldur(self):
        """Kitap listesini veritabanından yükler - Sadece müsait kopyaları gösterir"""
        for i in self.kitap_listesi.get_children():
            self.kitap_listesi.delete(i)

        kitaplar = db_connect.kitaplari_getir()

        if kitaplar:
            for kitap in kitaplar:
                # Müsait kopya sayısını al
                stok_durumu = db_connect.kitap_stok_durumu(kitap[0])
                musait = stok_durumu['musait_kopya'] if stok_durumu else 0
                
                self.kitap_listesi.insert("", tk.END, values=(
                    kitap[0],                      # ID
                    kitap[1],                      # Kitap Adı
                    kitap[2] or "-",               # ISBN
                    kitap[6] or "-",               # Yayınevi
                    kitap[5] or "Belirtilmemiş",   # Yazarlar
                    kitap[7] or "-",               # TÜRLER
                    musait                         # MÜSAİT KOPYA (Ödünç verilebilir)
                ))
            self.controller.guncelle_durum(f"✅ {len(kitaplar)} kitap listelendi.", "green")
        else:
            self.controller.guncelle_durum("⚠️ Henüz kitap bulunmamaktadır.", "orange")

    def kitap_ekle_dialog(self):
        """Yeni kitap ekleme penceresi"""
        ekle_pencere = tk.Toplevel(self.controller.ana_pencere)
        ekle_pencere.title("➕ Yeni Kitap Ekle")
        ekle_pencere.geometry("500x700")
        ekle_pencere.resizable(False, False)

        # Yazarları, yayınevlerini ve türleri al
        yazarlar = db_connect.yazarlari_getir()
        yayinevleri = db_connect.yayinevlerini_getir()
        turler = db_connect.turleri_getir()
        
        if not yazarlar or not yayinevleri or not turler:
            messagebox.showerror("Hata", "Yazar, yayınevi veya tür bilgisi yüklenemedi!")
            ekle_pencere.destroy()
            return

        # Form alanları
        row = 0
        
        # Kitap Adı
        ttk.Label(ekle_pencere, text="Kitap Adı *:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        kitap_adi_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=kitap_adi_var, width=40).grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # ISBN
        ttk.Label(ekle_pencere, text="ISBN:", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        isbn_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=isbn_var, width=40).grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Yazar
        ttk.Label(ekle_pencere, text="Yazar *:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        yazar_var = tk.StringVar()
        yazar_combo = ttk.Combobox(ekle_pencere, textvariable=yazar_var, width=37, state="readonly")
        yazar_combo['values'] = [y[1] for y in yazarlar]
        yazar_combo.grid(row=row, column=1, padx=10, pady=10)
        if yazarlar:
            yazar_combo.current(0)
        row += 1

        # Yayınevi
        ttk.Label(ekle_pencere, text="Yayınevi *:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        yayinevi_var = tk.StringVar()
        yayinevi_combo = ttk.Combobox(ekle_pencere, textvariable=yayinevi_var, width=37, state="readonly")
        yayinevi_combo['values'] = [y[1] for y in yayinevleri]
        yayinevi_combo.grid(row=row, column=1, padx=10, pady=10)
        if yayinevleri:
            yayinevi_combo.current(0)
        row += 1

        # Tür
        ttk.Label(ekle_pencere, text="Tür *:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        tur_var = tk.StringVar()
        tur_combo = ttk.Combobox(ekle_pencere, textvariable=tur_var, width=37, state="readonly")
        tur_combo['values'] = [t[1] for t in turler]
        tur_combo.grid(row=row, column=1, padx=10, pady=10)
        if turler:
            tur_combo.current(0)
        row += 1

        # Yayın Yılı
        ttk.Label(ekle_pencere, text="Yayın Yılı:", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        yayin_yili_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=yayin_yili_var, width=40).grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Kopya Sayısı
        ttk.Label(ekle_pencere, text="Kopya Sayısı *:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
        kopya_var = tk.StringVar(value="1")
        ttk.Entry(ekle_pencere, textvariable=kopya_var, width=40).grid(row=row, column=1, padx=10, pady=10)
        row += 1

        def kaydet():
            kitap_adi = kitap_adi_var.get().strip()
            isbn = isbn_var.get().strip() or None
            yazar_secili = yazar_var.get().strip()
            yayinevi_secili = yayinevi_var.get().strip()
            tur_secili = tur_var.get().strip()
            yayin_yili = yayin_yili_var.get().strip()
            kopya_sayisi = kopya_var.get().strip()

            if not kitap_adi:
                messagebox.showerror("Hata", "Kitap adı boş bırakılamaz!")
                return

            if not yazar_secili or not yayinevi_secili or not tur_secili:
                messagebox.showerror("Hata", "Yazar, yayınevi ve tür seçilmelidir!")
                return

            try:
                kopya_sayisi = int(kopya_sayisi)
                if kopya_sayisi < 1:
                    messagebox.showerror("Hata", "Kopya sayısı en az 1 olmalıdır!")
                    return
            except ValueError:
                messagebox.showerror("Hata", "Kopya sayısı sayısal olmalıdır!")
                return

            # ID'leri bul
            yazar_id = next((y[0] for y in yazarlar if y[1] == yazar_secili), None)
            yayinevi_id = next((y[0] for y in yayinevleri if y[1] == yayinevi_secili), None)
            tur_id = next((t[0] for t in turler if t[1] == tur_secili), None)

            if not yazar_id or not yayinevi_id or not tur_id:
                messagebox.showerror("Hata", "Seçimler bulunamadı!")
                return

            # Basım tarihi
            basim_tarihi = f"{yayin_yili}-01-01" if yayin_yili else None

            sonuc = db_connect.kitap_ekle(
                ad=kitap_adi,
                isbn=isbn,
                basim_tarihi=basim_tarihi,
                baski_sayisi=1,
                yazar_ids=[yazar_id],
                yayinevi_ids=[yayinevi_id],
                tur_id=tur_id,
                kopya_sayisi=kopya_sayisi
            )

            if sonuc.get("durum") == "Başarılı":
                self.controller.guncelle_durum(f"✅ Kitap eklendi: {kitap_adi}", "green")
                self.listeyi_doldur()
                ekle_pencere.destroy()
            else:
                messagebox.showerror("Hata", f"Kitap eklenemedi: {sonuc.get('mesaj')}")

        ttk.Button(ekle_pencere, text="💾 Kaydet", command=kaydet).grid(row=row, column=0, columnspan=2, pady=20)

    def kitap_ara_dialog(self):
        """Kitap arama penceresi - Yazar ve yayınevine göre de arama yapabilir"""
        arama_pencere = tk.Toplevel(self.controller.ana_pencere)
        arama_pencere.title("🔍 Kitap Ara")
        arama_pencere.geometry("900x600")

        # Arama kriterleri frame
        kriter_frame = ttk.LabelFrame(arama_pencere, text="Arama Kriterleri", padding=10)
        kriter_frame.pack(pady=10, padx=10, fill="x")

        # Kitap Adı / ISBN
        ttk.Label(kriter_frame, text="Kitap Adı veya ISBN:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        kitap_var = tk.StringVar()
        kitap_entry = ttk.Entry(kriter_frame, textvariable=kitap_var, width=40)
        kitap_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Yazar
        ttk.Label(kriter_frame, text="Yazar:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        yazar_var = tk.StringVar()
        yazar_entry = ttk.Entry(kriter_frame, textvariable=yazar_var, width=40)
        yazar_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Yayınevi
        ttk.Label(kriter_frame, text="Yayınevi:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        yayinevi_var = tk.StringVar()
        yayinevi_entry = ttk.Entry(kriter_frame, textvariable=yayinevi_var, width=40)
        yayinevi_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Bilgi etiketi
        ttk.Label(kriter_frame, text="💡 İpucu: En az bir kriter girerek arama yapabilirsiniz", 
                  font=("Arial", 9, "italic"), foreground="gray").grid(row=3, column=0, columnspan=2, pady=5)

        # Sonuç frame
        sonuc_frame = ttk.Frame(arama_pencere)
        sonuc_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(sonuc_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        sonuc_tree = ttk.Treeview(
            sonuc_frame,
            columns=("ID", "Kitap Adı", "Yazar", "Yayınevi", "Stok"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(command=sonuc_tree.yview)

        sonuc_tree.heading("ID", text="ID")
        sonuc_tree.heading("Kitap Adı", text="Kitap Adı")
        sonuc_tree.heading("Yazar", text="Yazar")
        sonuc_tree.heading("Yayınevi", text="Yayınevi")
        sonuc_tree.heading("Stok", text="Stok")

        sonuc_tree.column("ID", width=50)
        sonuc_tree.column("Kitap Adı", width=300)
        sonuc_tree.column("Yazar", width=200)
        sonuc_tree.column("Yayınevi", width=150)
        sonuc_tree.column("Stok", width=60)

        sonuc_tree.pack(fill="both", expand=True)

        def ara():
            for item in sonuc_tree.get_children():
                sonuc_tree.delete(item)

            kitap_terimi = kitap_var.get().strip()
            yazar_terimi = yazar_var.get().strip()
            yayinevi_terimi = yayinevi_var.get().strip()

            # En az bir kriter girilmeli
            if not any([kitap_terimi, yazar_terimi, yayinevi_terimi]):
                messagebox.showwarning("Uyarı", "Lütfen en az bir arama kriteri girin!")
                return

            # Filtreleme için SQL sorgusu hazırla
            sonuclar = db_connect.kitap_ara_detayli(kitap_terimi, yazar_terimi, yayinevi_terimi)

            if sonuclar:
                for sonuc in sonuclar:
                    # [0]=materyalno, [1]=kitap_adi, [2]=yazarlar, [3]=yayinevi, [4]=stok
                    sonuc_tree.insert("", tk.END, values=(
                        sonuc[0],                           # ID
                        sonuc[1],                           # Kitap Adı
                        sonuc[2] or "Belirtilmemiş",       # Yazarlar
                        sonuc[3] or "Belirtilmemiş",       # Yayınevi
                        sonuc[4]                            # Stok
                    ))
                self.controller.guncelle_durum(f"✅ {len(sonuclar)} sonuç bulundu.", "green")
            else:
                self.controller.guncelle_durum("❌ Sonuç bulunamadı!", "red")

        def temizle():
            kitap_var.set("")
            yazar_var.set("")
            yayinevi_var.set("")
            for item in sonuc_tree.get_children():
                sonuc_tree.delete(item)
            kitap_entry.focus()

        def detay_ac():
            secili = sonuc_tree.focus()
            if secili:
                degerler = sonuc_tree.item(secili, 'values')
                kitap_id = degerler[0]
                self.kitap_detay_goster(kitap_id)

        buton_frame = ttk.Frame(arama_pencere)
        buton_frame.pack(pady=10)

        ttk.Button(buton_frame, text="🔍 Ara", command=ara).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="🔄 Temizle", command=temizle).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="📋 Detay", command=detay_ac).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="Kapat", command=arama_pencere.destroy).pack(side=tk.LEFT, padx=5)

        # Enter tuşu ile arama
        kitap_entry.bind('<Return>', lambda e: ara())
        yazar_entry.bind('<Return>', lambda e: ara())
        yayinevi_entry.bind('<Return>', lambda e: ara())
        
        # Çift tıklama ile detay göster
        sonuc_tree.bind('<Double-1>', lambda e: detay_ac())
        
        kitap_entry.focus()

    def kitap_detay_goster(self, kitap_id=None):
        """Seçili kitabın detaylarını gösterir"""
        if kitap_id is None:
            secili = self.kitap_listesi.focus()
            if not secili:
                self.controller.guncelle_durum("⚠️ Lütfen bir kitap seçin!", "orange")
                return
            degerler = self.kitap_listesi.item(secili, 'values')
            kitap_id = degerler[0]

        kitap = db_connect.kitap_detay_getir(kitap_id)

        if not kitap:
            messagebox.showerror("Hata", "Kitap bilgisi bulunamadı!")
            return

        detay_pencere = tk.Toplevel(self.controller.ana_pencere)
        detay_pencere.title(f"📖 {kitap['kitap_adi']}")
        detay_pencere.geometry("500x600")
        detay_pencere.resizable(False, False)

        bilgiler = [
            ("Kitap ID:", kitap['kitap_id']),
            ("Kitap Adı:", kitap['kitap_adi']),
            ("ISBN:", kitap['isbn'] or "Belirtilmemiş"),
            ("Yayınevi:", kitap['yayinevi'] or "Belirtilmemiş"),
            ("Yayın Yılı:", kitap['yayin_yili'] or "Belirtilmemiş"),
            ("Stok Miktarı:", kitap['stok']),
            ("Yazarlar:", kitap['yazarlar'] or "Belirtilmemiş"),
            ("Kategoriler:", kitap['kategoriler'] or "Belirtilmemiş"),
            ("", ""),
            ("Toplam Ödünç Alınma:", kitap['toplam_odunc']),
            ("Şu An Ödünçte:", kitap['oduncte_olan']),
            ("Mevcut:", kitap['stok'] - kitap['oduncte_olan']),
        ]

        for i, (etiket, deger) in enumerate(bilgiler):
            if etiket == "":
                ttk.Separator(detay_pencere, orient='horizontal').grid(row=i, column=0, columnspan=2, sticky='ew', pady=10, padx=20)
                continue

            ttk.Label(detay_pencere, text=etiket, font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=30, pady=8
            )
            ttk.Label(detay_pencere, text=str(deger), font=("Arial", 10)).grid(
                row=i, column=1, sticky=tk.W, padx=10, pady=8
            )

        ttk.Button(detay_pencere, text="Kapat", command=detay_pencere.destroy).pack(pady=20)

    def kitap_duzenle_dialog(self):
        """Düzenleme özelliği"""
        messagebox.showinfo("Bilgi", "Düzenleme özelliği yakında eklenecek.")

    def kitap_sil_action(self):
        """Seçili kitabı siler"""
        secili = self.kitap_listesi.focus()
        if not secili:
            self.controller.guncelle_durum("⚠️ Lütfen silinecek kitabı seçin!", "orange")
            return

        degerler = self.kitap_listesi.item(secili, 'values')
        kitap_id = degerler[0]
        kitap_adi = degerler[1]

        onay = messagebox.askyesno(
            "Silme Onayı",
            f"'{kitap_adi}' kitabını silmek istediğinizden emin misiniz?\n\n"
            "⚠️ Dikkat: Bu kitapla ilgili ödünç kayıtları varsa silme işlemi başarısız olacaktır."
        )

        if not onay:
            return

        sonuc = db_connect.kitap_sil(kitap_id)

        if sonuc.get("durum") == "Başarılı":
            self.controller.guncelle_durum(f"🗑️ Kitap silindi: {kitap_adi}", "red")
            self.listeyi_doldur()
        else:
            messagebox.showerror("Hata", f"Kitap silinemedi:\n{sonuc.get('mesaj')}\n\nBu kitapla ilgili ödünç kayıtları olabilir.")