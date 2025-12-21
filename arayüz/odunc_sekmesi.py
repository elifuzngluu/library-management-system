# arayüz/odunc_sekmesi.py

import tkinter as tk
from tkinter import ttk, messagebox
import db_connect

class OduncSekmesi:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.kur_arayuz()

    def kur_arayuz(self):
        ttk.Label(self.parent, text="📚 ÖDÜNÇ ALMA/İADE SİSTEMİ", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Üst Butonlar
        buton_frame = ttk.Frame(self.parent)
        buton_frame.pack(pady=10)

        ttk.Button(buton_frame, text="➕ Yeni Ödünç Ver", command=self.odunc_ver_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="↩️ İade Al", command=self.iade_al_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="💰 Ceza Öde", command=self.ceza_ode_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_frame, text="🔄 Listeyi Yenile", command=self.listeyi_doldur).pack(side=tk.LEFT, padx=5)

        # Aktif Ödünçler Listesi
        liste_frame = ttk.Frame(self.parent)
        liste_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(liste_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.odunc_listesi = ttk.Treeview(
            liste_frame,
            columns=("Ödünç ID", "Üye", "Materyal", "Ödünç Tarihi", "İade Tarihi", "Durum"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(command=self.odunc_listesi.yview)

        # Sütun başlıkları
        self.odunc_listesi.heading("Ödünç ID", text="ID")
        self.odunc_listesi.heading("Üye", text="Üye Adı")
        self.odunc_listesi.heading("Materyal", text="Materyal")
        self.odunc_listesi.heading("Ödünç Tarihi", text="Ödünç Tarihi")
        self.odunc_listesi.heading("İade Tarihi", text="Beklenen İade")
        self.odunc_listesi.heading("Durum", text="Durum")

        # Sütun genişlikleri
        self.odunc_listesi.column("Ödünç ID", width=60)
        self.odunc_listesi.column("Üye", width=150)
        self.odunc_listesi.column("Materyal", width=250)
        self.odunc_listesi.column("Ödünç Tarihi", width=100)
        self.odunc_listesi.column("İade Tarihi", width=100)
        self.odunc_listesi.column("Durum", width=100)

        self.odunc_listesi.pack(fill="both", expand=True)

        # Renklendirme için tag'ler
        self.odunc_listesi.tag_configure('gecikmiş', background='#ffcccc')
        self.odunc_listesi.tag_configure('aktif', background='#ccffcc')

        # İlk yüklemede listeyi doldur
        self.listeyi_doldur()

    def listeyi_doldur(self):
        """Aktif ödünçleri listeler"""
        for i in self.odunc_listesi.get_children():
            self.odunc_listesi.delete(i)

        oduncler = db_connect.aktif_oduncler()

        if oduncler:
            for odunc in oduncler:
                tag = 'gecikmiş' if odunc[6] == 'GECİKMİŞ' else 'aktif'
                self.odunc_listesi.insert("", tk.END, values=odunc, tags=(tag,))
            self.controller.guncelle_durum(f"✅ {len(oduncler)} aktif ödünç listelendi.", "green")
        else:
            self.controller.guncelle_durum("⚠️ Aktif ödünç bulunmamaktadır.", "orange")

    def odunc_ver_dialog(self):
        """Yeni ödünç verme penceresi"""
        dialog = tk.Toplevel(self.controller.ana_pencere)
        dialog.title("➕ Yeni Ödünç Ver")
        dialog.geometry("600x500")
        dialog.resizable(False, False)

        # Üye Seçimi
        ttk.Label(dialog, text="Üye TC No veya Üye No:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        uye_var = tk.StringVar()
        uye_entry = ttk.Entry(dialog, textvariable=uye_var, width=30)
        uye_entry.grid(row=0, column=1, padx=10, pady=10)

        # Üye bilgisi gösterme alanı
        uye_bilgi_label = ttk.Label(dialog, text="", font=("Arial", 9), foreground="blue")
        uye_bilgi_label.grid(row=1, column=0, columnspan=3, padx=20, pady=5, sticky=tk.W)

        def uye_kontrol():
            uye_tc = uye_var.get().strip()
            if not uye_tc:
                messagebox.showwarning("Uyarı", "Üye TC No veya Üye No giriniz!")
                return

            # Üye bilgisini getir
            uye = db_connect.uye_detay_getir(uye_tc)
            if not uye:
                # Üye no ile de dene
                sorgu = "SELECT tcno FROM \"Üye\" WHERE \"üyeNo\" = %s;"
                sonuc = db_connect.sorgu_calistir(sorgu, (uye_tc,), fetch_one=True)
                if sonuc:
                    uye = db_connect.uye_detay_getir(sonuc[0])
            
            if not uye:
                messagebox.showerror("Hata", "Üye bulunamadı!")
                uye_bilgi_label.config(text="")
                return

            # Ödünç verebilir mi kontrolü
            kontrol = db_connect.odunc_verebilir_mi(uye['tcno'])
            
            bilgi_text = f"👤 {uye['ad']} {uye['soyad']} ({uye['uye_tipi']})\n"
            
            if kontrol['durum']:
                bilgi_text += f"✅ {kontrol['mesaj']} (Kalan hak: {kontrol['kalan_hak']})"
                uye_bilgi_label.config(text=bilgi_text, foreground="green")
            else:
                bilgi_text += f"❌ {kontrol['mesaj']}"
                uye_bilgi_label.config(text=bilgi_text, foreground="red")
                messagebox.showerror("Ödünç Verilemez", kontrol['mesaj'])

        ttk.Button(dialog, text="🔍 Üye Kontrol", command=uye_kontrol).grid(row=0, column=2, padx=5, pady=10)

        ttk.Separator(dialog, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)

        # Kitap Arama
        ttk.Label(dialog, text="Kitap Ara:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        kitap_arama_var = tk.StringVar()
        kitap_entry = ttk.Entry(dialog, textvariable=kitap_arama_var, width=30)
        kitap_entry.grid(row=3, column=1, padx=10, pady=10)

        # Kitap sonuçları
        sonuc_frame = ttk.Frame(dialog)
        sonuc_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

        sonuc_tree = ttk.Treeview(
            sonuc_frame,
            columns=("ID", "Kitap", "Stok"),
            show="headings",
            height=8
        )

        sonuc_tree.heading("ID", text="ID")
        sonuc_tree.heading("Kitap", text="Kitap Adı")
        sonuc_tree.heading("Stok", text="Müsait")

        sonuc_tree.column("ID", width=50)
        sonuc_tree.column("Kitap", width=350)
        sonuc_tree.column("Stok", width=80)

        sonuc_tree.pack(fill="both", expand=True)

        def kitap_ara():
            for item in sonuc_tree.get_children():
                sonuc_tree.delete(item)

            arama = kitap_arama_var.get().strip()
            if not arama:
                return

            sonuclar = db_connect.kitap_ara(arama)
            if sonuclar:
                for sonuc in sonuclar:
                    sonuc_tree.insert("", tk.END, values=sonuc)
            else:
                messagebox.showinfo("Bilgi", "Kitap bulunamadı!")

        ttk.Button(dialog, text="🔍 Ara", command=kitap_ara).grid(row=3, column=2, padx=5, pady=10)

        def odunc_ver():
            uye_tc = uye_var.get().strip()
            secili = sonuc_tree.focus()

            if not secili:
                messagebox.showwarning("Uyarı", "Lütfen kitap seçiniz!")
                return

            if not uye_tc.isdigit() or len(uye_tc) != 11:
                sorgu = "SELECT tcno FROM \"Üye\" WHERE \"üyeNo\" = %s;"
                sonuc = db_connect.sorgu_calistir(sorgu, (uye_tc,), fetch_one=True)
                if sonuc:
                    uye_tc = sonuc[0]
                else:
                    messagebox.showerror("Hata", "Üye bulunamadı!")
                    return

            kitap_values = sonuc_tree.item(secili, 'values')
            materyal_no = kitap_values[0]
            stok = int(kitap_values[2])

            if stok == 0:
                messagebox.showerror("Hata", "Bu kitaptan müsait kopya yok!")
                return

            # Müsait kopya seç
            kopyalar = db_connect.musait_kopyalar(materyal_no)
            if not kopyalar:
                messagebox.showerror("Hata", "Müsait kopya bulunamadı!")
                return

            kopya_id = kopyalar[0][0]

            # Ödünç ver
            sonuc = db_connect.odunc_ver(uye_tc, kopya_id)

            if sonuc.get("durum") == "Başarılı":
                messagebox.showinfo("Başarılı", sonuc['mesaj'])
                self.controller.guncelle_durum(f"✅ Ödünç verildi: {kitap_values[1]}", "green")
                self.listeyi_doldur()
                dialog.destroy()
            else:
                messagebox.showerror("Hata", f"Ödünç verilemedi:\n{sonuc.get('mesaj')}")

        ttk.Button(dialog, text="✅ Ödünç Ver", command=odunc_ver).grid(row=5, column=0, columnspan=3, pady=20)

    def iade_al_dialog(self):
        """İade alma penceresi"""
        dialog = tk.Toplevel(self.controller.ana_pencere)
        dialog.title("↩️ İade Al")
        dialog.geometry("500x300")

        ttk.Label(dialog, text="Ödünç ID:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        odunc_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=odunc_id_var, width=20).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(dialog, text="veya", font=("Arial", 9)).grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Label(dialog, text="Üye TC No:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        uye_tc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=uye_tc_var, width=20).grid(row=2, column=1, padx=10, pady=10)

        odunc_listbox = tk.Listbox(dialog, height=6)
        odunc_listbox.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        def uye_odunclerini_getir():
            odunc_listbox.delete(0, tk.END)
            uye_tc = uye_tc_var.get().strip()

            if not uye_tc:
                return

            if not uye_tc.isdigit() or len(uye_tc) != 11:
                sorgu = "SELECT tcno FROM \"Üye\" WHERE \"üyeNo\" = %s;"
                sonuc = db_connect.sorgu_calistir(sorgu, (uye_tc,), fetch_one=True)
                if sonuc:
                    uye_tc = sonuc[0]
                else:
                    messagebox.showerror("Hata", "Üye bulunamadı!")
                    return

            oduncler = db_connect.uye_odunc_durumu(uye_tc)
            if oduncler:
                for odunc in oduncler:
                    odunc_listbox.insert(tk.END, f"ID: {odunc[0]} - {odunc[1]} (İade: {odunc[4]})")
            else:
                messagebox.showinfo("Bilgi", "Bu üyenin aktif ödüncü yok!")

        ttk.Button(dialog, text="🔍 Ödünçleri Getir", command=uye_odunclerini_getir).grid(row=2, column=2, padx=5)

        def iade_al():
            odunc_id = odunc_id_var.get().strip()

            if not odunc_id and odunc_listbox.curselection():
                # Listeden seçileni al
                secili_text = odunc_listbox.get(odunc_listbox.curselection())
                odunc_id = secili_text.split()[1]  # "ID: 123" -> "123"

            if not odunc_id:
                messagebox.showwarning("Uyarı", "Ödünç ID giriniz veya listeden seçiniz!")
                return

            sonuc = db_connect.iade_al(odunc_id)

            if sonuc.get("durum") == "Başarılı":
                messagebox.showinfo("Başarılı", sonuc['mesaj'])
                self.controller.guncelle_durum(f"✅ İade alındı (ID: {odunc_id})", "green")
                self.listeyi_doldur()
                dialog.destroy()
            else:
                messagebox.showerror("Hata", f"İade alınamadı:\n{sonuc.get('mesaj')}")

        ttk.Button(dialog, text="✅ İade Al", command=iade_al).grid(row=4, column=0, columnspan=3, pady=20)

    def ceza_ode_dialog(self):
        """Ceza ödeme penceresi"""
        dialog = tk.Toplevel(self.controller.ana_pencere)
        dialog.title("💰 Ceza Öde")
        dialog.geometry("600x400")

        ttk.Label(dialog, text="Üye TC No veya üye no:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        uye_tc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=uye_tc_var, width=30).grid(row=0, column=1, padx=10, pady=10)

        ceza_frame = ttk.Frame(dialog)
        ceza_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

        ceza_tree = ttk.Treeview(
            ceza_frame,
            columns=("Ceza ID", "Tutar", "Tarih", "Kitap"),
            show="headings",
            height=10
        )

        ceza_tree.heading("Ceza ID", text="ID")
        ceza_tree.heading("Tutar", text="Tutar")
        ceza_tree.heading("Tarih", text="İade Tarihi")
        ceza_tree.heading("Kitap", text="Kitap")

        ceza_tree.pack(fill="both", expand=True)

        toplam_label = ttk.Label(dialog, text="Toplam: 0.00 TL", font=("Arial", 11, "bold"), foreground="red")
        toplam_label.grid(row=2, column=0, columnspan=3, pady=10)

        def cezalari_getir():
            for item in ceza_tree.get_children():
                ceza_tree.delete(item)

            uye_tc = uye_tc_var.get().strip()
            if not uye_tc:
                messagebox.showwarning("Uyarı", "Üye TC No giriniz!")
                return

            if not uye_tc.isdigit() or len(uye_tc) != 11:
                sorgu = "SELECT tcno FROM \"Üye\" WHERE \"üyeNo\" = %s;"
                sonuc = db_connect.sorgu_calistir(sorgu, (uye_tc,), fetch_one=True)
                if sonuc:
                    uye_tc = sonuc[0]
                else:
                    messagebox.showerror("Hata", "Üye bulunamadı!")
                    return
                    
            cezalar = db_connect.uye_ceza_durumu(uye_tc)
            toplam = 0

            if cezalar:
                for ceza in cezalar:
                    ceza_tree.insert("", tk.END, values=(ceza[0], f"{ceza[1]:.2f} TL", ceza[2], ceza[3]))
                    toplam += ceza[1]
                toplam_label.config(text=f"Toplam: {toplam:.2f} TL")
            else:
                messagebox.showinfo("Bilgi", "Bu üyenin ödenmemiş cezası yok!")
                toplam_label.config(text="Toplam: 0.00 TL")

        ttk.Button(dialog, text="🔍 Cezaları Getir", command=cezalari_getir).grid(row=0, column=2, padx=5)

        def ceza_ode():
            secili = ceza_tree.focus()
            if not secili:
                messagebox.showwarning("Uyarı", "Lütfen ödenecek cezayı seçiniz!")
                return

            ceza_values = ceza_tree.item(secili, 'values')
            ceza_id = ceza_values[0]

            onay = messagebox.askyesno("Onay", f"{ceza_values[1]} tutarındaki cezayı ödemek istediğinizden emin misiniz?")
            if not onay:
                return

            sonuc = db_connect.ceza_ode(ceza_id)

            if sonuc.get("durum") == "Başarılı":
                messagebox.showinfo("Başarılı", "Ceza ödendi!")
                cezalari_getir()  # Listeyi yenile
                self.controller.guncelle_durum(f"✅ Ceza ödendi (ID: {ceza_id})", "green")
            else:
                messagebox.showerror("Hata", f"Ceza ödenemedi:\n{sonuc.get('mesaj')}")

        ttk.Button(dialog, text="💵 Seçili Cezayı Öde", command=ceza_ode).grid(row=3, column=0, columnspan=3, pady=20)