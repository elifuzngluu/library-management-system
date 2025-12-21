# main_app.py

import tkinter as tk
from arayüz.main_pencere import KutuphaneUygulamasi

if __name__ == '__main__':
    kok = tk.Tk()
    uygulama = KutuphaneUygulamasi(kok)
    kok.mainloop()