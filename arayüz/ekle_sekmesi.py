# arayüz/ekle_sekmesi.py

import tkinter as tk
from tkinter import ttk, messagebox
import db_connect
from datetime import datetime, timedelta

class EkleSekmesi:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.kur_arayuz()

    def kur_arayuz(self):
        ttk.Label(self.parent, text="➕ YENİ ÜYE EKLEME", font=("Arial", 16, "bold")).pack(pady=20)

        # Üye Türü Seçimi
        tür_frame = ttk.Frame(self.parent)
        tür_frame.pack(pady=10)

        ttk.Label(tür_frame, text="Üye Türü:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        self.uye_turu_var = tk.StringVar(value="Öğrenci")
        türler = ["Öğrenci", "Öğretmen", "Diğer Üye"]

        for tur in türler:
            rb = ttk.Radiobutton(
                tür_frame,
                text=tur,
                variable=self.uye_turu_var,
                value=tur,
                command=self.guncelle_form_alani
            )
            rb.pack(side=tk.LEFT, padx=10)

        # Form Alanları için çerçeve
        self.form_cercevesi = ttk.Frame(self.parent)
        self.form_cercevesi.pack(padx=50, pady=10)

        # Girdi Değişkenleri
        self.tcno_var = tk.StringVar()
        self.ad_var = tk.StringVar()
        self.soyad_var = tk.StringVar()
        self.eposta_var = tk.StringVar()
        self.telno_var = tk.StringVar()
        self.ogrno_var = tk.StringVar()
        self.sinif_var = tk.StringVar()
        self.okul_var = tk.StringVar()
        self.brans_var = tk.StringVar()
        self.isyeri_var = tk.StringVar()
        self.gerekce_var = tk.StringVar()
        self.gecerlilik_var = tk.StringVar()

        self.guncelle_form_alani()

        ttk.Button(self.parent, text="✅ ÜYE KAYDI YAP", command=self.uye_kaydi_yap_action).pack(pady=20)

    def guncelle_form_alani(self):
        for widget in self.form_cercevesi.winfo_children():
            widget.destroy()

        tur = self.uye_turu_var.get()
        row = 0

        # Ortak Alanlar
        ttk.Label(self.form_cercevesi, text="TC Kimlik No *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
        ttk.Entry(self.form_cercevesi, textvariable=self.tcno_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(self.form_cercevesi, text="Adı *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
        ttk.Entry(self.form_cercevesi, textvariable=self.ad_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(self.form_cercevesi, text="Soyadı *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
        ttk.Entry(self.form_cercevesi, textvariable=self.soyad_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(self.form_cercevesi, text="E-posta:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
        ttk.Entry(self.form_cercevesi, textvariable=self.eposta_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(self.form_cercevesi, text="Telefon:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
        ttk.Entry(self.form_cercevesi, textvariable=self.telno_var, width=30).grid(row=row, column=1, pady=5)
        row += 1

        # Türe Özel Alanlar
        if tur == "Öğrenci":
            ttk.Label(self.form_cercevesi, text="Öğrenci No *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            ttk.Entry(self.form_cercevesi, textvariable=self.ogrno_var, width=30).grid(row=row, column=1, pady=5)
            row += 1

            ttk.Label(self.form_cercevesi, text="Sınıf Düzeyi *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            ttk.Entry(self.form_cercevesi, textvariable=self.sinif_var, width=30).grid(row=row, column=1, pady=5)
            row += 1

            ttk.Label(self.form_cercevesi, text="Okul Bilgisi:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            ttk.Entry(self.form_cercevesi, textvariable=self.okul_var, width=30).grid(row=row, column=1, pady=5)
            row += 1

        elif tur == "Öğretmen":
            ttk.Label(self.form_cercevesi, text="Branş *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            ttk.Entry(self.form_cercevesi, textvariable=self.brans_var, width=30).grid(row=row, column=1, pady=5)
            row += 1

            ttk.Label(self.form_cercevesi, text="İş Yeri:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            ttk.Entry(self.form_cercevesi, textvariable=self.isyeri_var, width=30).grid(row=row, column=1, pady=5)
            row += 1

        elif tur == "Diğer Üye":
            ttk.Label(self.form_cercevesi, text="Gerekçe *:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            ttk.Entry(self.form_cercevesi, textvariable=self.gerekce_var, width=30).grid(row=row, column=1, pady=5)
            row += 1

            ttk.Label(self.form_cercevesi, text="Geçerlilik Tarihi:", width=18, anchor='w').grid(row=row, column=0, pady=5, sticky=tk.W)
            
            # Varsayılan: 1 yıl sonra
            varsayilan_tarih = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            self.gecerlilik_var.set(varsayilan_tarih)
            
            ttk.Entry(self.form_cercevesi, textvariable=self.gecerlilik_var, width=30).grid(row=row, column=1, pady=5)
            ttk.Label(self.form_cercevesi, text="(YYYY-MM-DD)", font=("Arial", 8), foreground="gray").grid(row=row, column=2, pady=5, padx=5)
            row += 1

    def uye_kaydi_yap_action(self):
        tcno = self.tcno_var.get().strip()
        ad = self.ad_var.get().strip()
        soyad = self.soyad_var.get().strip()
        eposta = self.eposta_var.get().strip() or None
        telno = self.telno_var.get().strip() or None
        tur = self.uye_turu_var.get()

        # Temel Validasyonlar
        if not all([tcno, ad, soyad]):
            messagebox.showerror("Hata", "Ad, Soyad ve TC Kimlik No zorunludur!")
            return

        if len(tcno) != 11 or not tcno.isdigit():
            messagebox.showerror("Hata", "TC Kimlik No 11 haneli rakam olmalıdır!")
            return

        try:
            if tur == "Öğrenci":
                ogrno = self.ogrno_var.get().strip()
                sinif = self.sinif_var.get().strip()
                okul = self.okul_var.get().strip() or None

                if not all([ogrno, sinif]):
                    messagebox.showerror("Hata", "Öğrenci No ve Sınıf Düzeyi zorunludur!")
                    return

                sonuc = db_connect.ogrenci_ekle(
                    tcno=tcno,
                    ad=ad,
                    soyad=soyad,
                    eposta=eposta,
                    telno=telno,
                    ogrno=ogrno,
                    sinif_duzeyi=sinif,
                    okul_bilgisi=okul
                )

            elif tur == "Öğretmen":
                brans = self.brans_var.get().strip()
                isyeri = self.isyeri_var.get().strip() or None

                if not brans:
                    messagebox.showerror("Hata", "Branş zorunludur!")
                    return

                sonuc = db_connect.ogretmen_ekle(
                    tcno=tcno,
                    ad=ad,
                    soyad=soyad,
                    eposta=eposta,
                    telno=telno,
                    brans=brans,
                    isyeri=isyeri
                )

            elif tur == "Diğer Üye":
                gerekce = self.gerekce_var.get().strip()
                gecerlilik = self.gecerlilik_var.get().strip()

                if not gerekce:
                    messagebox.showerror("Hata", "Gerekçe zorunludur!")
                    return

                if not gecerlilik:
                    gecerlilik = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

                sonuc = db_connect.diger_uye_ekle(
                    tcno=tcno,
                    ad=ad,
                    soyad=soyad,
                    eposta=eposta,
                    telno=telno,
                    gerekce=gerekce,
                    gecerlilik_tarihi=gecerlilik
                )

            else:
                messagebox.showerror("Hata", "Geçersiz üye türü!")
                return

            # Sonuç kontrolü
            if sonuc.get("durum") == "Başarılı":
                messagebox.showinfo("Başarılı", f"{tur} başarıyla eklendi:\n{ad} {soyad}")
                self.controller.guncelle_durum(f"✅ {tur} eklendi: {ad} {soyad}", "green")
                self.temizle_form()
                
                # Arama sekmesindeki listeyi güncelle
                if hasattr(self.controller, 'arama_arayuzu'):
                    self.controller.arama_arayuzu.listeyi_doldur()
            else:
                messagebox.showerror("Hata", f"Üye eklenemedi:\n{sonuc.get('mesaj')}")
                self.controller.guncelle_durum(f"❌ Hata: {sonuc.get('mesaj')}", "red")

        except Exception as e:
            messagebox.showerror("Beklenmeyen Hata", f"Bir hata oluştu:\n{str(e)}")
            self.controller.guncelle_durum(f"❌ Beklenmeyen hata: {str(e)}", "red")

    def temizle_form(self):
        """Form alanlarını temizler"""
        self.tcno_var.set("")
        self.ad_var.set("")
        self.soyad_var.set("")
        self.eposta_var.set("")
        self.telno_var.set("")
        self.ogrno_var.set("")
        self.sinif_var.set("")
        self.okul_var.set("")
        self.brans_var.set("")
        self.isyeri_var.set("")
        self.gerekce_var.set("")
        self.gecerlilik_var.set("")