# arayüz/main_pencere.py

import tkinter as tk
from tkinter import ttk
from .ekle_sekmesi import EkleSekmesi
from .arama_sekmesi import AramaSekmesi
from .kitap_sekmesi import KitapSekmesi
from .odunc_sekmesi import OduncSekmesi
from .personel_sekmesi import PersonelSekmesi

class KutuphaneUygulamasi:
    def __init__(self, ana_pencere):
        self.ana_pencere = ana_pencere
        ana_pencere.title("📚 Kütüphane Yönetim Sistemi")
        ana_pencere.geometry("800x600")

        self.notebook = ttk.Notebook(ana_pencere)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Sekmeleri Tanımlama
        self.ekle_sekmesi = ttk.Frame(self.notebook)
        self.arama_sekmesi = ttk.Frame(self.notebook)
        self.kitap_sekmesi = ttk.Frame(self.notebook)
        self.odunc_sekmesi = ttk.Frame(self.notebook) 
        self.personel_sekmesi = ttk.Frame(self.notebook)

        self.notebook.add(self.ekle_sekmesi, text="➕ Yeni Kayıt Ekle")
        self.notebook.add(self.arama_sekmesi, text="🔍 Arama & Güncelleme")
        self.notebook.add(self.kitap_sekmesi, text="📚 Kitap Yönetimi")
        self.notebook.add(self.odunc_sekmesi, text="📖 Ödünç İşlemleri")
        self.notebook.add(self.personel_sekmesi, text="👔 Personel Yönetimi")

         # Durum Çubuğu
        self.durum_cubugu = tk.Label(ana_pencere, text="Uygulama hazır.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.durum_cubugu.pack(side=tk.BOTTOM, fill=tk.X)

        # Sekmeleri başlat
        self.ekle_arayuzu = EkleSekmesi(self.ekle_sekmesi, self)
        self.arama_arayuzu = AramaSekmesi(self.arama_sekmesi, self)
        self.kitap_arayuzu = KitapSekmesi(self.kitap_sekmesi, self)
        self.odunc_arayuzu = OduncSekmesi(self.odunc_sekmesi, self)
        self.personel_arayuzu = PersonelSekmesi(self.personel_sekmesi, self)

       
    def guncelle_durum(self, mesaj, renk="black"):
        self.durum_cubugu.config(text=mesaj, foreground=renk)

    def listeyi_doldur(self):
        self.arama_arayuzu.listeyi_doldur()