# arayuz/personel_sekmesi.py

import tkinter as tk
from tkinter import ttk, messagebox
import db_connect

class PersonelSekmesi:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.kur_arayuz()

    def kur_arayuz(self):
        ttk.Label(self.parent, text="👔 PERSONEL YÖNETİMİ", 
                  font=("Arial", 16, "bold")).pack(pady=10)

        # Üst butonlar
        buton_frame = ttk.Frame(self.parent)
        buton_frame.pack(pady=5)

        ttk.Button(buton_frame, text="➕ Yeni Personel Ekle", 
                   command=self.personel_ekle_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="🔄 Listeyi Yenile", 
                   command=self.listeyi_doldur).pack(side=tk.LEFT, padx=5)

        # Personel Listesi
        liste_frame = ttk.Frame(self.parent)
        liste_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(liste_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.personel_listesi = ttk.Treeview(
            liste_frame,
            columns=("TC No", "Ad", "Soyad", "Sicil No", "Pozisyon"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(command=self.personel_listesi.yview)

        # Sütun başlıkları
        self.personel_listesi.heading("TC No", text="TC No")
        self.personel_listesi.heading("Ad", text="Ad")
        self.personel_listesi.heading("Soyad", text="Soyad")
        self.personel_listesi.heading("Sicil No", text="Sicil No")
        self.personel_listesi.heading("Pozisyon", text="Pozisyon")

        # Sütun genişlikleri
        self.personel_listesi.column("TC No", width=120)
        self.personel_listesi.column("Ad", width=150)
        self.personel_listesi.column("Soyad", width=150)
        self.personel_listesi.column("Sicil No", width=100)
        self.personel_listesi.column("Pozisyon", width=150)

        self.personel_listesi.pack(fill="both", expand=True)

        # İlk yüklemede listeyi doldur
        self.listeyi_doldur()

    def listeyi_doldur(self):
        """Personel listesini veritabanından yükler"""
        for i in self.personel_listesi.get_children():
            self.personel_listesi.delete(i)

        personeller = db_connect.personelleri_getir()

        if personeller:
            for personel in personeller:
                self.personel_listesi.insert("", tk.END, values=(
                    personel[0],  # TC No
                    personel[1],  # Ad
                    personel[2],  # Soyad
                    personel[3],  # Sicil No
                    personel[4]   # Pozisyon
                ))
            self.controller.guncelle_durum(
                f"✅ {len(personeller)} personel listelendi.", "green"
            )
        else:
            self.controller.guncelle_durum(
                "⚠️ Henüz personel bulunmamaktadır.", "orange"
            )

    def personel_ekle_dialog(self):
        """Yeni personel ekleme penceresi"""
        ekle_pencere = tk.Toplevel(self.controller.ana_pencere)
        ekle_pencere.title("➕ Yeni Personel Ekle")
        ekle_pencere.geometry("500x400")
        ekle_pencere.resizable(False, False)

        # Form alanları
        ttk.Label(ekle_pencere, text="TC Kimlik No *:", 
                  font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        tcno_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=tcno_var, width=30).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(ekle_pencere, text="Ad *:", 
                  font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        ad_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=ad_var, width=30).grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(ekle_pencere, text="Soyad *:", 
                  font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        soyad_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=soyad_var, width=30).grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(ekle_pencere, text="E-posta:", 
                  font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        eposta_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=eposta_var, width=30).grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(ekle_pencere, text="Telefon:", 
                  font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, padx=20, pady=10)
        telno_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=telno_var, width=30).grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(ekle_pencere, text="Sicil No *:", 
                  font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, padx=20, pady=10)
        sicilno_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=sicilno_var, width=30).grid(row=5, column=1, padx=10, pady=10)

        ttk.Label(ekle_pencere, text="Pozisyon *:", 
                  font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, padx=20, pady=10)
        pozisyon_var = tk.StringVar()
        pozisyon_combo = ttk.Combobox(ekle_pencere, textvariable=pozisyon_var, width=28, state="readonly")
        pozisyon_combo['values'] = ('Kütüphaneci', 'Yönetici', 'Teknisyen', 'Güvenlik', 'Temizlik')
        pozisyon_combo.grid(row=6, column=1, padx=10, pady=10)
        pozisyon_combo.current(0)

        ttk.Label(ekle_pencere, text="Ev Adresi:", 
                  font=("Arial", 10)).grid(row=7, column=0, sticky=tk.W, padx=20, pady=10)
        adres_var = tk.StringVar()
        ttk.Entry(ekle_pencere, textvariable=adres_var, width=30).grid(row=7, column=1, padx=10, pady=10)

        def kaydet():
            tcno = tcno_var.get().strip()
            ad = ad_var.get().strip()
            soyad = soyad_var.get().strip()
            eposta = eposta_var.get().strip() or None
            telno = telno_var.get().strip() or None
            sicilno = sicilno_var.get().strip()
            pozisyon = pozisyon_var.get().strip()
            adres = adres_var.get().strip() or None

            if not all([tcno, ad, soyad, sicilno, pozisyon]):
                messagebox.showerror("Hata", "Zorunlu alanları doldurun!")
                return

            if len(tcno) != 11 or not tcno.isdigit():
                messagebox.showerror("Hata", "TC Kimlik No 11 haneli rakam olmalıdır!")
                return

            sonuc = db_connect.personel_ekle(tcno, ad, soyad, eposta, telno, sicilno, pozisyon, adres)

            if sonuc.get("durum") == "Başarılı":
                self.controller.guncelle_durum(f"✅ Personel eklendi: {ad} {soyad}", "green")
                self.listeyi_doldur()
                ekle_pencere.destroy()
            else:
                messagebox.showerror("Hata", f"Personel eklenemedi: {sonuc.get('mesaj')}")

        ttk.Button(ekle_pencere, text="💾 Kaydet", command=kaydet).grid(row=8, column=0, columnspan=2, pady=20)