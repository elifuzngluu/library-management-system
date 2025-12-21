# arayüz/arama_sekmesi.py

import tkinter as tk
from tkinter import ttk, messagebox
import db_connect


class AramaSekmesi:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.kur_arayuz()

    def kur_arayuz(self):
        ttk.Label(
            self.parent,
            text="KAYITLI ÜYELER VE ARAMA",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Treeview
        self.uye_listesi = ttk.Treeview(
            self.parent,
            columns=("Adı", "Soyadı", "Üye No", "TC No"),
            show="headings"
        )

        self.uye_listesi.heading("Adı", text="Adı")
        self.uye_listesi.heading("Soyadı", text="Soyadı")
        self.uye_listesi.heading("Üye No", text="Üye No")
        self.uye_listesi.heading("TC No", text="TC No")

        self.uye_listesi.column("Adı", width=150)
        self.uye_listesi.column("Soyadı", width=150)
        self.uye_listesi.column("Üye No", width=100)
        self.uye_listesi.column("TC No", width=120)

        self.uye_listesi.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(
            self.parent,
            text="Listeyi Yenile",
            command=self.listeyi_doldur
        ).pack(pady=5)

        self.uye_listesi.bind("<<TreeviewSelect>>", self.kayit_secildi)

        buton_frame = ttk.Frame(self.parent)
        buton_frame.pack(pady=5)

        ttk.Button(
            buton_frame,
            text="📋 Detay Göster",
            command=self.secili_uye_detay_goster
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buton_frame,
            text="🔍 Üye Ara",
            command=self.uye_ara_dialog
        ).pack(side=tk.LEFT, padx=5)

        self.listeyi_doldur()

    def listeyi_doldur(self):
        # Önce listeyi temizle
        for i in self.uye_listesi.get_children():
            self.uye_listesi.delete(i)

        uyeler = db_connect.uyeleri_getir()

        if uyeler:
            for uye in uyeler:
                self.uye_listesi.insert("", tk.END, values=(
                    uye[0],  # Ad
                    uye[1],  # Soyad
                    uye[2],  # Üye No
                    uye[3]   # TC No
                ))

            self.controller.guncelle_durum(
                f"✅ Toplam {len(uyeler)} üye listelendi.", "black"
            )
        else:
            self.controller.guncelle_durum(
                "⚠️ Listelenecek üye yok.", "orange"
            )

    def kayit_secildi(self, event):
        secili = self.uye_listesi.focus()
        degerler = self.uye_listesi.item(secili, "values")

        if degerler:
            self.guncelleme_formu_olustur(degerler)

    def guncelleme_formu_olustur(self, uye):
        if hasattr(self, "guncelleme_cercevesi"):
            self.guncelleme_cercevesi.destroy()

        self.guncelleme_cercevesi = ttk.LabelFrame(
            self.parent, text="Seçili Kaydı Güncelle / Sil"
        )
        self.guncelleme_cercevesi.pack(fill="x", padx=10, pady=10)

        self.g_tcno_var = tk.StringVar(value=uye[3])
        self.g_ad_var = tk.StringVar(value=uye[0])
        self.g_soyad_var = tk.StringVar(value=uye[1])

        ttk.Label(self.guncelleme_cercevesi, text="TC No:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(
            self.guncelleme_cercevesi,
            textvariable=self.g_tcno_var,
            state="readonly"
        ).grid(row=0, column=1)

        ttk.Label(self.guncelleme_cercevesi, text="Adı:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(
            self.guncelleme_cercevesi,
            textvariable=self.g_ad_var
        ).grid(row=1, column=1)

        ttk.Label(self.guncelleme_cercevesi, text="Soyadı:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(
            self.guncelleme_cercevesi,
            textvariable=self.g_soyad_var
        ).grid(row=2, column=1)

        ttk.Button(
            self.guncelleme_cercevesi,
            text="GÜNCELLE",
            command=self.uye_guncelle_action
        ).grid(row=3, column=0, pady=10)

        ttk.Button(
            self.guncelleme_cercevesi,
            text="SİL",
            command=self.uye_sil_action
        ).grid(row=3, column=1, pady=10)

    def uye_guncelle_action(self):
        sonuc = db_connect.uye_guncelle(
            tcno=self.g_tcno_var.get(),
            ad=self.g_ad_var.get(),
            soyad=self.g_soyad_var.get(),
            eposta=None,
            telno=None
        )

        if sonuc.get("durum") == "Başarılı":
            self.controller.guncelle_durum("✅ Üye güncellendi.", "green")
            self.listeyi_doldur()
        else:
            self.controller.guncelle_durum(sonuc.get("mesaj"), "red")

    def uye_sil_action(self):
        tcno = self.g_tcno_var.get()

        if not messagebox.askyesno("Onay", "Üye silinsin mi?"):
            return

        sonuc = db_connect.uye_sil(tcno)

        if sonuc.get("durum") == "Başarılı":
            self.controller.guncelle_durum("🗑️ Üye silindi.", "red")
            self.listeyi_doldur()
            self.guncelleme_cercevesi.destroy()
        else:
            self.controller.guncelle_durum(sonuc.get("mesaj"), "red")

    def secili_uye_detay_goster(self):
        secili = self.uye_listesi.focus()
        if not secili:
            return

        tcno = self.uye_listesi.item(secili, "values")[3]
        self.uye_detay_goster(tcno)

    def uye_detay_goster(self, tcno):
        uye = db_connect.uye_detay_getir(tcno)
        if not uye:
            return

        pencere = tk.Toplevel(self.controller.ana_pencere)
        pencere.title("Üye Detay")
        pencere.geometry("600x450")

        notebook = ttk.Notebook(pencere)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # TEMEL BİLGİLER
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📋 Temel Bilgiler")

        bilgiler = [
            ("TC No", uye["tcno"]),
            ("Ad", uye["ad"]),
            ("Soyad", uye["soyad"]),
            ("E-posta", uye["eposta"] or "-"),
            ("Telefon", uye["telno"] or "-"),
            ("Üye No", uye["uye_no"]),
            ("Üye Tipi", uye["uye_tipi"]),
        ]

        for i, (k, v) in enumerate(bilgiler):
            ttk.Label(frame, text=k, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            ttk.Label(frame, text=v).grid(row=i, column=1, sticky=tk.W)

        ttk.Button(pencere, text="Kapat", command=pencere.destroy).pack(pady=10)

    def uye_ara_dialog(self):
        pencere = tk.Toplevel(self.controller.ana_pencere)
        pencere.title("Üye Ara")
        pencere.geometry("500x400")

        arama_var = tk.StringVar()
        ttk.Entry(pencere, textvariable=arama_var).pack(pady=5)

        tree = ttk.Treeview(
            pencere,
            columns=("Ad", "Soyad", "Üye No", "TC No", "Tip"),
            show="headings"
        )
        for c in ("Ad", "Soyad", "Üye No", "TC No", "Tip"):
            tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def ara():
            for i in tree.get_children():
                tree.delete(i)
            for s in db_connect.uye_ara(arama_var.get()):
                tree.insert("", tk.END, values=s)

        ttk.Button(pencere, text="Ara", command=ara).pack(pady=5)
