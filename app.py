"""
================================================================================
NON ISHLAB CHIQARISH SEXI BOSHQARUV TIZIMI
Professional Version 3.0
================================================================================
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter.font import Font
import sqlite3
from datetime import datetime, date, timedelta
import json
import csv
import os
import sys
from decimal import Decimal, getcontext
from collections import defaultdict
import calendar
from typing import Optional, List, Dict, Tuple, Any
import math

# ==================== KONFIGURATSIYA ====================
class Config:
    """Dastur konfiguratsiyasi"""
    DB_NAME = "non_sex.db"
    COMPANY_NAME = "NON SEX BOSHQARUV TIZIMI"
    VERSION = "3.0 Professional"
    
    # Ranglar
    COLORS = {
        'primary': '#2C3E50',
        'secondary': '#34495E',
        'success': '#27AE60',
        'danger': '#E74C3C',
        'warning': '#F39C12',
        'info': '#3498DB',
        'light': '#ECF0F1',
        'dark': '#2C3E50',
        'white': '#FFFFFF',
        'background': '#F8F9FA',
        'sidebar': '#2C3E50',
        'header': '#1ABC9C',
        'text': '#2C3E50',
        'grid': '#BDC3C7'
    }
    
    # O'lchamlar
    WINDOW_SIZE = "1400x800"
    FONTS = {
        'title': ('Arial', 18, 'bold'),
        'heading': ('Arial', 14, 'bold'),
        'normal': ('Arial', 11),
        'small': ('Arial', 10),
        'large': ('Arial', 16, 'bold')
    }
    
    # Sanalar
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    
    @staticmethod
    def get_date():
        """Bugungi sana"""
        return date.today().strftime(Config.DATE_FORMAT)
    
    @staticmethod
    def get_time():
        """Hozirgi vaqt"""
        return datetime.now().strftime(Config.TIME_FORMAT)
    
    @staticmethod
    def get_datetime():
        """Hozirgi sana va vaqt"""
        return datetime.now().strftime(f"{Config.DATE_FORMAT} {Config.TIME_FORMAT}")

# ==================== MA'LUMOTLAR BAZASI ====================
class Database:
    """SQLite ma'lumotlar bazasi"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Bazaga ulanish"""
        try:
            self.conn = sqlite3.connect(Config.DB_NAME, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
            print("✅ Ma'lumotlar bazasiga ulandi")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Bazaga ulanishda xatolik: {e}")
            sys.exit(1)
    
    def create_tables(self):
        """Jadvallarni yaratish"""
        tables = [
            # Xodimlar
            """CREATE TABLE IF NOT EXISTS xodimlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ism TEXT NOT NULL,
                lavozim TEXT NOT NULL,
                telefon TEXT,
                ish_boshlash DATE,
                oylik_maosh DECIMAL(15,2) DEFAULT 0,
                bonus DECIMAL(15,2) DEFAULT 0,
                jarima DECIMAL(15,2) DEFAULT 0,
                reyting DECIMAL(5,2) DEFAULT 100.0,
                status TEXT DEFAULT 'faol',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # Mijozlar
            """CREATE TABLE IF NOT EXISTS mijozlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT NOT NULL,
                telefon TEXT,
                manzil TEXT,
                turi TEXT DEFAULT 'dokon',
                kredit_limit DECIMAL(15,2) DEFAULT 0,
                jami_qarz DECIMAL(15,2) DEFAULT 0,
                jami_tovar DECIMAL(15,2) DEFAULT 0,
                oxirgi_sana DATE,
                status TEXT DEFAULT 'faol',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # Xamir tayyorlash
            """CREATE TABLE IF NOT EXISTS xamir (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana DATE NOT NULL,
                xodim_id INTEGER,
                boshlash_vaqti TIME,
                tugash_vaqti TIME,
                un_qop INTEGER DEFAULT 0,
                xamir_soni INTEGER DEFAULT 0,
                kunlik_norma INTEGER DEFAULT 100,
                kechikish_minut INTEGER DEFAULT 0,
                samaradorlik DECIMAL(5,2) DEFAULT 100.0,
                status TEXT DEFAULT 'tayyor',
                keyingi_bosqich BOOLEAN DEFAULT 0,
                izoh TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (xodim_id) REFERENCES xodimlar(id)
            )""",
            
            # Non yasash
            """CREATE TABLE IF NOT EXISTS non_yasash (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana DATE NOT NULL,
                xamir_id INTEGER,
                xodim_id INTEGER,
                qabul_xamir INTEGER DEFAULT 0,
                chiqqan_non INTEGER DEFAULT 0,
                brak_non INTEGER DEFAULT 0,
                yeyilgan_non INTEGER DEFAULT 0,
                sof_non INTEGER DEFAULT 0,
                brak_sababi TEXT,
                ortacha_unumdorlik DECIMAL(5,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (xodim_id) REFERENCES xodimlar(id),
                FOREIGN KEY (xamir_id) REFERENCES xamir(id)
            )""",
            
            # Tandir
            """CREATE TABLE IF NOT EXISTS tandir (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana DATE NOT NULL,
                tandir_raqami INTEGER,
                tandirchi_id INTEGER,
                kirgan_non INTEGER DEFAULT 0,
                chiqqan_non INTEGER DEFAULT 0,
                brak_non INTEGER DEFAULT 0,
                samaradorlik DECIMAL(5,2) DEFAULT 100.0,
                nosozlik TEXT,
                holat TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tandirchi_id) REFERENCES xodimlar(id)
            )""",
            
            # Sotuvlar
            """CREATE TABLE IF NOT EXISTS sotuvlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana DATE NOT NULL,
                mijoz_id INTEGER,
                non_turi TEXT,
                miqdor INTEGER DEFAULT 0,
                narx_dona DECIMAL(10,2) DEFAULT 0,
                jami_summa DECIMAL(15,2) DEFAULT 0,
                tolov_turi TEXT DEFAULT 'naqd',
                tolandi DECIMAL(15,2) DEFAULT 0,
                qoldiq_qarz DECIMAL(15,2) DEFAULT 0,
                qaytgan_non INTEGER DEFAULT 0,
                qaytish_sababi TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mijoz_id) REFERENCES mijozlar(id)
            )""",
            
            # Xarajatlar
            """CREATE TABLE IF NOT EXISTS xarajatlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana DATE NOT NULL,
                turi TEXT NOT NULL,
                miqdor DECIMAL(10,2) DEFAULT 0,
                narx DECIMAL(10,2) DEFAULT 0,
                jami_summa DECIMAL(15,2) DEFAULT 0,
                izoh TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # Kassa
            """CREATE TABLE IF NOT EXISTS kassa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana DATE NOT NULL,
                kirim DECIMAL(15,2) DEFAULT 0,
                chiqim DECIMAL(15,2) DEFAULT 0,
                balans DECIMAL(15,2) DEFAULT 0,
                izoh TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # Hisobotlar
            """CREATE TABLE IF NOT EXISTS hisobotlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turi TEXT NOT NULL,
                davr TEXT NOT NULL,
                maumot TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # Foydalanuvchilar
            """CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                parol TEXT NOT NULL,
                rol TEXT DEFAULT 'operator',
                ism TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # Harakatlar jurnali
            """CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                foydalanuvchi TEXT,
                harakat TEXT,
                maumot TEXT
            )"""
        ]
        
        try:
            for table in tables:
                self.cursor.execute(table)
            self.conn.commit()
            
            # Boshlang'ich admin foydalanuvchi
            self.cursor.execute(
                "INSERT OR IGNORE INTO foydalanuvchilar (login, parol, rol, ism) VALUES (?, ?, ?, ?)",
                ('admin', 'admin123', 'admin', 'Administrator')
            )
            self.conn.commit()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Jadvallarni yaratishda xatolik: {e}")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """SQL so'rovini bajarish"""
        try:
            return self.cursor.execute(query, params)
        except Exception as e:
            messagebox.showerror("SQL Xatolik", str(e))
            raise
    
    def executemany(self, query: str, params: list):
        """Ko'p ma'lumotlar bilan so'rov"""
        try:
            self.cursor.executemany(query, params)
        except Exception as e:
            messagebox.showerror("SQL Xatolik", str(e))
            raise
    
    def commit(self):
        """O'zgarishlarni saqlash"""
        self.conn.commit()
    
    def fetchall(self, query: str, params: tuple = ()) -> list:
        """Barcha natijalarni olish"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("SQL Xatolik", str(e))
            return []
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Bitta natija olish"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            messagebox.showerror("SQL Xatolik", str(e))
            return None
    
    def close(self):
        """Bazani yopish"""
        if self.conn:
            self.conn.close()

# ==================== YORDAMCHI FUNKSIYALAR ====================
class Utils:
    """Yordamchi funksiyalar"""
    
    @staticmethod
    def format_money(amount: float) -> str:
        """Pulni formatlash"""
        return f"{amount:,.0f} so'm"
    
    @staticmethod
    def format_date(dt: str) -> str:
        """Sanani formatlash"""
        try:
            return datetime.strptime(dt, Config.DATE_FORMAT).strftime("%d.%m.%Y")
        except:
            return dt
    
    @staticmethod
    def format_time(tm: str) -> str:
        """Vaqtni formatlash"""
        try:
            return datetime.strptime(tm, Config.TIME_FORMAT).strftime("%H:%M")
        except:
            return tm
    
    @staticmethod
    def calculate_time_difference(start: str, end: str) -> int:
        """Vaqt farqini hisoblash (daqiqa)"""
        try:
            start_dt = datetime.strptime(start, Config.TIME_FORMAT)
            end_dt = datetime.strptime(end, Config.TIME_FORMAT)
            difference = end_dt - start_dt
            return difference.total_seconds() / 60
        except:
            return 0
    
    @staticmethod
    def calculate_percentage(part: float, whole: float) -> float:
        """Foizni hisoblash"""
        if whole == 0:
            return 0
        return (part / whole) * 100
    
    @staticmethod
    def validate_number(value: str) -> Optional[float]:
        """Raqamni tekshirish"""
        try:
            return float(value.replace(',', '.'))
        except:
            return None
    
    @staticmethod
    def validate_int(value: str) -> Optional[int]:
        """Butun sonni tekshirish"""
        try:
            return int(value)
        except:
            return None
    
    @staticmethod
    def get_color_by_value(value: float, threshold1: float = 70, threshold2: float = 90) -> str:
        """Qiymatga qarab rang berish"""
        if value >= threshold2:
            return Config.COLORS['success']
        elif value >= threshold1:
            return Config.COLORS['warning']
        else:
            return Config.COLORS['danger']
    
    @staticmethod
    def get_qarz_color(qarz: float, limit: float = 0) -> str:
        """Qarz miqdoriga qarab rang"""
        if qarz == 0:
            return Config.COLORS['success']
        elif limit > 0 and qarz <= limit * 0.5:
            return Config.COLORS['warning']
        else:
            return Config.COLORS['danger']
    
    @staticmethod
    def create_tooltip(widget, text: str):
        """Tooltip yaratish"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        
        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
        
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def hide_tooltip(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

# ==================== ASOSIY DASHTBORD ====================
class Dashboard:
    """Asosiy dashbord"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """UI yaratish"""
        # Asosiy frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sarlavha
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="📊 ASOSIY DASHTBORD",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            title_frame,
            text=f"Sana: {Config.get_date()}",
            font=Config.FONTS['normal'],
            foreground=Config.COLORS['dark']
        ).pack(side=tk.RIGHT)
        
        # Statistikalar paneli
        stats_frame = ttk.LabelFrame(self.main_frame, text="📈 UMUMIY STATISTIKA", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 4 ustunli statistikalar
        self.create_stats_row(stats_frame)
        
        # Ikki ustunli asosiy ma'lumotlar
        data_frame = ttk.Frame(self.main_frame)
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chap ustun
        left_frame = ttk.Frame(data_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # O'ng ustun
        right_frame = ttk.Frame(data_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Chap ustundagi widgetlar
        self.create_sales_widget(left_frame)
        self.create_expenses_widget(left_frame)
        
        # O'ng ustundagi widgetlar
        self.create_production_widget(right_frame)
        self.create_debtors_widget(right_frame)
    
    def create_stats_row(self, parent):
        """Statistikalar qatorini yaratish"""
        stats_data = [
            ("💰 KUNLIK TUSHUM", "0 so'm", Config.COLORS['success']),
            ("📦 KUNLIK SOTUV", "0 dona", Config.COLORS['info']),
            ("⚠️  KUNLIK BRAK", "0 dona", Config.COLORS['danger']),
            ("👥 FAOL XODIMLAR", "0 kishi", Config.COLORS['warning'])
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            frame = ttk.Frame(parent)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            ttk.Label(
                frame,
                text=title,
                font=Config.FONTS['small'],
                foreground=Config.COLORS['dark']
            ).pack()
            
            self.stats_label = ttk.Label(
                frame,
                text=value,
                font=Config.FONTS['large'],
                foreground=color
            )
            self.stats_label.pack(pady=5)
            
            parent.columnconfigure(i, weight=1)
    
    def create_sales_widget(self, parent):
        """Sotuvlar widgeti"""
        frame = ttk.LabelFrame(parent, text="📈 OXIRGI SOTUVLAR", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Jadval
        columns = ("ID", "Mijoz", "Miqdor", "Summa", "Holat")
        self.sales_tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_expenses_widget(self, parent):
        """Xarajatlar widgeti"""
        frame = ttk.LabelFrame(parent, text="💸 OXIRGI XARAJATLAR", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Turi", "Summa", "Sana", "Izoh")
        self.expenses_tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expenses_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_production_widget(self, parent):
        """Ishlab chiqarish widgeti"""
        frame = ttk.LabelFrame(parent, text="🏭 ISHLAB CHIQARISH HOLATI", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Ishchi diagrammalar uchun frame
        prod_frame = ttk.Frame(frame)
        prod_frame.pack(fill=tk.BOTH, expand=True)
        
        # 3 ta statistik panel
        prod_stats = [
            ("Xamir Tayyor", "0", Config.COLORS['info']),
            ("Non Yasaldi", "0", Config.COLORS['success']),
            ("Tandirda", "0", Config.COLORS['warning'])
        ]
        
        for i, (title, value, color) in enumerate(prod_stats):
            stat_frame = ttk.Frame(prod_frame)
            stat_frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            
            ttk.Label(
                stat_frame,
                text=title,
                font=Config.FONTS['small'],
                foreground=Config.COLORS['dark']
            ).pack()
            
            ttk.Label(
                stat_frame,
                text=value,
                font=Config.FONTS['large'],
                foreground=color
            ).pack()
            
            prod_frame.columnconfigure(i, weight=1)
        
        # Jadval
        columns = ("Bosqich", "Xodim", "Miqdor", "Holat")
        self.prod_tree = ttk.Treeview(frame, columns=columns, show="headings", height=4)
        
        for col in columns:
            self.prod_tree.heading(col, text=col)
            self.prod_tree.column(col, width=100)
        
        self.prod_tree.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def create_debtors_widget(self, parent):
        """Qarzdorlar widgeti"""
        frame = ttk.LabelFrame(parent, text="⚠️  QARZDOR MIJOZLAR", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Mijoz", "Qarz", "Chegara", "Holat")
        self.debtors_tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.debtors_tree.heading(col, text=col)
            self.debtors_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.debtors_tree.yview)
        self.debtors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.debtors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        today = Config.get_date()
        
        # Kunlik tushum
        result = self.db.fetchone(
            "SELECT SUM(jami_summa) FROM sotuvlar WHERE sana = ? AND status = 'active'",
            (today,)
        )
        daily_income = result[0] if result and result[0] else 0
        
        # Kunlik sotuv
        result = self.db.fetchone(
            "SELECT SUM(miqdor) FROM sotuvlar WHERE sana = ? AND status = 'active'",
            (today,)
        )
        daily_sales = result[0] if result and result[0] else 0
        
        # Kunlik brak
        result = self.db.fetchone(
            """SELECT SUM(brak_non) FROM non_yasash WHERE sana = ?
               UNION ALL
               SELECT SUM(brak_non) FROM tandir WHERE sana = ?""",
            (today, today)
        )
        daily_brak = result[0] if result and result[0] else 0
        
        # Faol xodimlar
        result = self.db.fetchone(
            "SELECT COUNT(*) FROM xodimlar WHERE status = 'faol'"
        )
        active_workers = result[0] if result else 0
        
        # Statistikani yangilash
        for i, widget in enumerate(self.main_frame.winfo_children()[1].winfo_children()):
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and child['text'] in ["0 so'm", "0 dona", "0 kishi"]:
                        if i == 0:
                            child.config(text=Utils.format_money(daily_income))
                        elif i == 1:
                            child.config(text=f"{daily_sales} dona")
                        elif i == 2:
                            child.config(text=f"{daily_brak} dona")
                        elif i == 3:
                            child.config(text=f"{active_workers} kishi")
        
        # Oxirgi sotuvlar
        self.load_recent_sales()
        
        # Oxirgi xarajatlar
        self.load_recent_expenses()
        
        # Ishlab chiqarish holati
        self.load_production_status()
        
        # Qarzdorlar
        self.load_debtors()
    
    def load_recent_sales(self):
        """Oxirgi sotuvlarni yuklash"""
        self.sales_tree.delete(*self.sales_tree.get_children())
        
        results = self.db.fetchall(
            """SELECT s.id, m.nomi, s.miqdor, s.jami_summa, 
                      CASE WHEN s.qoldiq_qarz > 0 THEN 'QARZ' ELSE "TO'LANDI" END
               FROM sotuvlar s
               LEFT JOIN mijozlar m ON s.mijoz_id = m.id
               WHERE s.status = 'active'
               ORDER BY s.id DESC LIMIT 10"""
        )
        
        for row in results:
            self.sales_tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"{row[2]} dona",
                Utils.format_money(row[3]),
                row[4]
            ))
    
    def load_recent_expenses(self):
        """Oxirgi xarajatlarni yuklash"""
        self.expenses_tree.delete(*self.expenses_tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, turi, jami_summa, sana, SUBSTR(izoh, 1, 20) || '...'
               FROM xarajatlar 
               ORDER BY id DESC LIMIT 10"""
        )
        
        for row in results:
            self.expenses_tree.insert("", tk.END, values=(
                row[0],
                row[1],
                Utils.format_money(row[2]),
                Utils.format_date(row[3]),
                row[4] if row[4] else ""
            ))
    
    def load_production_status(self):
        """Ishlab chiqarish holatini yuklash"""
        self.prod_tree.delete(*self.prod_tree.get_children())
        
        today = Config.get_date()
        
        # Xamir tayyorlash
        xamir_result = self.db.fetchone(
            "SELECT COUNT(*), SUM(xamir_soni) FROM xamir WHERE sana = ?",
            (today,)
        )
        xamir_count = xamir_result[0] if xamir_result and xamir_result[0] else 0
        xamir_total = xamir_result[1] if xamir_result and xamir_result[1] else 0
        
        # Non yasash
        non_result = self.db.fetchone(
            "SELECT COUNT(*), SUM(chiqqan_non) FROM non_yasash WHERE sana = ?",
            (today,)
        )
        non_count = non_result[0] if non_result and non_result[0] else 0
        non_total = non_result[1] if non_result and non_result[1] else 0
        
        # Tandir
        tandir_result = self.db.fetchone(
            "SELECT COUNT(*), SUM(chiqqan_non) FROM tandir WHERE sana = ?",
            (today,)
        )
        tandir_count = tandir_result[0] if tandir_result and tandir_result[0] else 0
        tandir_total = tandir_result[1] if tandir_result and tandir_result[1] else 0
        
        # Statistikani yangilash
        prod_frame = self.prod_tree.master.master.winfo_children()[0]
        for i, child in enumerate(prod_frame.winfo_children()):
            if isinstance(child, ttk.Frame):
                for label in child.winfo_children():
                    if isinstance(label, ttk.Label) and label['text'] in ["0"]:
                        if i == 0:
                            label.config(text=f"{xamir_total}")
                        elif i == 1:
                            label.config(text=f"{non_total}")
                        elif i == 2:
                            label.config(text=f"{tandir_total}")
        
        # Jadval ma'lumotlari
        results = self.db.fetchall(
            """SELECT 'Xamir Tayyor' as bosqich, x.ism, xm.xamir_soni, xm.status
               FROM xamir xm
               LEFT JOIN xodimlar x ON xm.xodim_id = x.id
               WHERE xm.sana = ?
               UNION ALL
               SELECT 'Non Yasash' as bosqich, x.ism, ny.chiqqan_non, 'tayyor' as status
               FROM non_yasash ny
               LEFT JOIN xodimlar x ON ny.xodim_id = x.id
               WHERE ny.sana = ?
               UNION ALL
               SELECT 'Tandirda' as bosqich, x.ism, t.chiqqan_non, t.holat
               FROM tandir t
               LEFT JOIN xodimlar x ON t.tandirchi_id = x.id
               WHERE t.sana = ?
               LIMIT 5""",
            (today, today, today)
        )
        
        for row in results:
            self.prod_tree.insert("", tk.END, values=row)
    
    def load_debtors(self):
        """Qarzdorlarni yuklash"""
        self.debtors_tree.delete(*self.debtors_tree.get_children())
        
        results = self.db.fetchall(
            """SELECT nomi, jami_qarz, kredit_limit,
                      CASE 
                          WHEN jami_qarz = 0 THEN 'YAXSHI'
                          WHEN jami_qarz <= kredit_limit * 0.5 THEN 'OGOH'
                          ELSE 'XAVOLI' 
                      END as holat
               FROM mijozlar 
               WHERE jami_qarz > 0 
               ORDER BY jami_qarz DESC 
               LIMIT 10"""
        )
        
        for row in results:
            color = Utils.get_qarz_color(row[1], row[2])
            self.debtors_tree.insert("", tk.END, values=(
                row[0],
                Utils.format_money(row[1]),
                Utils.format_money(row[2]),
                row[3]
            ), tags=(color,))
            
            self.debtors_tree.tag_configure(color, foreground=color)

# ==================== XAMIR TAYYORLASH MODULI ====================
class XamirTayyorlash:
    """Xamir tayyorlash moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        # Asosiy frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sarlavha
        ttk.Label(
            self.main_frame,
            text="🥖 XAMIR TAYYORLASH",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Forma frame
        form_frame = ttk.LabelFrame(self.main_frame, text="YANGI XAMIR", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 1-qator
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Xodim:", width=15).pack(side=tk.LEFT, padx=5)
        self.xodim_combo = ttk.Combobox(row1, state="readonly", width=30)
        self.xodim_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Boshlash vaqti:", width=15).pack(side=tk.LEFT, padx=5)
        self.boshlash_var = tk.StringVar(value=Config.get_time())
        ttk.Entry(row1, textvariable=self.boshlash_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 2-qator
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Un qopi:", width=15).pack(side=tk.LEFT, padx=5)
        self.un_qop_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.un_qop_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Xamir soni:", width=15).pack(side=tk.LEFT, padx=5)
        self.xamir_soni_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.xamir_soni_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Kunlik norma:", width=15).pack(side=tk.LEFT, padx=5)
        self.norma_var = tk.StringVar(value="100")
        ttk.Entry(row2, textvariable=self.norma_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 3-qator
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, pady=5)
        
        ttk.Label(row3, text="Tugash vaqti:", width=15).pack(side=tk.LEFT, padx=5)
        self.tugash_var = tk.StringVar(value=Config.get_time())
        ttk.Entry(row3, textvariable=self.tugash_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Status:", width=15).pack(side=tk.LEFT, padx=5)
        self.status_combo = ttk.Combobox(row3, values=["tayyor", "jarayonda", "kechikdi"], 
                                         state="readonly", width=15)
        self.status_combo.current(0)
        self.status_combo.pack(side=tk.LEFT, padx=5)
        
        # 4-qator
        row4 = ttk.Frame(form_frame)
        row4.pack(fill=tk.X, pady=5)
        
        ttk.Label(row4, text="Izoh:", width=15).pack(side=tk.LEFT, padx=5)
        self.izoh_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.izoh_var, width=50).pack(side=tk.LEFT, padx=5)
        
        # Tugmalar
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="📝 QAYD ETISH",
            command=self.save_xamir,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 KEYINGI BOSQICH",
            command=self.mark_next_stage
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🧹 TOZALASH",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=5)
        
        # Jadval frame
        table_frame = ttk.LabelFrame(self.main_frame, text="XAMIR TARIXI", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Jadval
        columns = ("ID", "Sana", "Xodim", "Un qopi", "Xamir", "Norma", "Vaqt", "Samara", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Xodimlarni yuklash
        self.load_xodimlar()
        # Ma'lumotlarni yuklash
        self.load_data()
    
    def load_xodimlar(self):
        """Xodimlarni yuklash"""
        results = self.db.fetchall(
            "SELECT id, ism FROM xodimlar WHERE status = 'faol' ORDER BY ism"
        )
        xodimlar = [f"{row[0]} - {row[1]}" for row in results]
        self.xodim_combo['values'] = xodimlar
        if xodimlar:
            self.xodim_combo.current(0)
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT x.id, x.sana, xd.ism, x.un_qop, x.xamir_soni, 
                      x.kunlik_norma, 
                      x.boshlash_vaqti || '-' || x.tugash_vaqti,
                      x.samaradorlik, x.status
               FROM xamir x
               LEFT JOIN xodimlar xd ON x.xodim_id = xd.id
               ORDER BY x.id DESC"""
        )
        
        for row in results:
            samara_color = Utils.get_color_by_value(row[7])
            status_color = Config.COLORS['success'] if row[8] == 'tayyor' else Config.COLORS['warning']
            
            self.tree.insert("", tk.END, values=row, tags=(samara_color,))
            self.tree.tag_configure(samara_color, foreground=samara_color)
    
    def save_xamir(self):
        """Xamirni saqlash"""
        # Validatsiya
        xodim = self.xodim_combo.get()
        un_qop = Utils.validate_int(self.un_qop_var.get())
        xamir_soni = Utils.validate_int(self.xamir_soni_var.get())
        norma = Utils.validate_int(self.norma_var.get())
        
        if not xodim or not un_qop or not xamir_soni or not norma:
            messagebox.showerror("Xatolik", "Barcha maydonlarni to'ldiring!")
            return
        
        # Xodim ID sini olish
        xodim_id = int(xodim.split(" - ")[0])
        
        # Vaqt farqini hisoblash
        kechikish = Utils.calculate_time_difference(
            self.boshlash_var.get(),
            self.tugash_var.get()
        )
        
        # Samaradorlikni hisoblash
        samaradorlik = Utils.calculate_percentage(xamir_soni, norma)
        
        # Ma'lumotlarni saqlash
        try:
            self.db.execute(
                """INSERT INTO xamir 
                   (sana, xodim_id, boshlash_vaqti, tugash_vaqti, 
                    un_qop, xamir_soni, kunlik_norma, kechikish_minut, 
                    samaradorlik, status, izoh) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (Config.get_date(), xodim_id, self.boshlash_var.get(), 
                 self.tugash_var.get(), un_qop, xamir_soni, norma,
                 kechikish, samaradorlik, self.status_combo.get(),
                 self.izoh_var.get())
            )
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", "Xamir muvaffaqiyatli qayd etildi!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def mark_next_stage(self):
        """Keyingi bosqichga o'tkazish"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ogohlantirish", "Iltimos, qaydni tanlang!")
            return
        
        item = self.tree.item(selection[0])
        xamir_id = item['values'][0]
        
        # Keyingi bosqichga o'tkazish
        try:
            self.db.execute(
                "UPDATE xamir SET keyingi_bosqich = 1 WHERE id = ?",
                (xamir_id,)
            )
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", "Keyingi bosqichga o'tkazildi!")
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Yangilashda xatolik: {e}")
    
    def clear_form(self):
        """Formani tozalash"""
        self.un_qop_var.set("")
        self.xamir_soni_var.set("")
        self.norma_var.set("100")
        self.tugash_var.set(Config.get_time())
        self.status_combo.current(0)
        self.izoh_var.set("")

# ==================== NON YASASH MODULI ====================
class NonYasash:
    """Non yasash moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="🍞 NON YASASH",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Forma frame
        form_frame = ttk.LabelFrame(self.main_frame, text="YANGI NON YASASH", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 1-qator
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Xodim:", width=15).pack(side=tk.LEFT, padx=5)
        self.xodim_combo = ttk.Combobox(row1, state="readonly", width=30)
        self.xodim_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Xamir ID:", width=15).pack(side=tk.LEFT, padx=5)
        self.xamir_combo = ttk.Combobox(row1, state="readonly", width=20)
        self.xamir_combo.pack(side=tk.LEFT, padx=5)
        
        # 2-qator
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Qabul xamir:", width=15).pack(side=tk.LEFT, padx=5)
        self.qabul_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.qabul_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Chiqqan non:", width=15).pack(side=tk.LEFT, padx=5)
        self.chiqqan_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.chiqqan_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 3-qator
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, pady=5)
        
        ttk.Label(row3, text="Brak non:", width=15).pack(side=tk.LEFT, padx=5)
        self.brak_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.brak_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Yeyilgan non:", width=15).pack(side=tk.LEFT, padx=5)
        self.yeyilgan_var = tk.StringVar(value="0")
        ttk.Entry(row3, textvariable=self.yeyilgan_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 4-qator
        row4 = ttk.Frame(form_frame)
        row4.pack(fill=tk.X, pady=5)
        
        ttk.Label(row4, text="Brak sababi:", width=15).pack(side=tk.LEFT, padx=5)
        self.brak_sababi_combo = ttk.Combobox(
            row4, 
            values=["Sifat", "Shakl", "Hajm", "Boshqa"],
            state="readonly",
            width=20
        )
        self.brak_sababi_combo.current(0)
        self.brak_sababi_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row4, text="Sof non:", width=15).pack(side=tk.LEFT, padx=5)
        self.sof_non_var = tk.StringVar(value="0")
        ttk.Entry(row4, textvariable=self.sof_non_var, state='readonly', 
                  width=15, foreground=Config.COLORS['success']).pack(side=tk.LEFT, padx=5)
        
        # Tugmalar
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="📝 SAQLASH",
            command=self.save_non,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🧮 HISOBlASH",
            command=self.calculate_sof
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🧹 TOZALASH",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        table_frame = ttk.LabelFrame(self.main_frame, text="NON YASASH TARIXI", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Sana", "Xodim", "Xamir", "Qabul", "Chiqdi", "Brak", 
                   "Yeyildi", "Sof", "Unumdorlik", "Sabab")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ma'lumotlarni yuklash
        self.load_xodimlar()
        self.load_xamirlar()
        self.load_data()
        
        # Avtomatik hisoblash
        self.chiqqan_var.trace('w', self.calculate_sof)
        self.brak_var.trace('w', self.calculate_sof)
        self.yeyilgan_var.trace('w', self.calculate_sof)
    
    def load_xodimlar(self):
        """Xodimlarni yuklash"""
        results = self.db.fetchall(
            "SELECT id, ism FROM xodimlar WHERE status = 'faol' ORDER BY ism"
        )
        xodimlar = [f"{row[0]} - {row[1]}" for row in results]
        self.xodim_combo['values'] = xodimlar
        if xodimlar:
            self.xodim_combo.current(0)
    
    def load_xamirlar(self):
        """Tayyor xamirlarni yuklash"""
        results = self.db.fetchall(
            """SELECT id, xamir_soni FROM xamir 
               WHERE status = 'tayyor' AND keyingi_bosqich = 0
               ORDER BY id DESC"""
        )
        xamirlar = [f"{row[0]} ({row[1]} dona)" for row in results]
        self.xamir_combo['values'] = xamirlar
        if xamirlar:
            self.xamir_combo.current(0)
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT ny.id, ny.sana, xd.ism, xm.xamir_soni, 
                      ny.qabul_xamir, ny.chiqqan_non, ny.brak_non,
                      ny.yeyilgan_non, ny.sof_non, ny.ortacha_unumdorlik,
                      ny.brak_sababi
               FROM non_yasash ny
               LEFT JOIN xodimlar xd ON ny.xodim_id = xd.id
               LEFT JOIN xamir xm ON ny.xamir_id = xm.id
               ORDER BY ny.id DESC"""
        )
        
        for row in results:
            unumdorlik_color = Utils.get_color_by_value(row[9])
            self.tree.insert("", tk.END, values=row, tags=(unumdorlik_color,))
            self.tree.tag_configure(unumdorlik_color, foreground=unumdorlik_color)
    
    def calculate_sof(self, *args):
        """Sof nonni hisoblash"""
        try:
            chiqqan = Utils.validate_int(self.chiqqan_var.get()) or 0
            brak = Utils.validate_int(self.brak_var.get()) or 0
            yeyilgan = Utils.validate_int(self.yeyilgan_var.get()) or 0
            
            sof = chiqqan - brak - yeyilgan
            self.sof_non_var.set(str(sof) if sof >= 0 else "0")
        except:
            self.sof_non_var.set("0")
    
    def save_non(self):
        """Non yasashni saqlash"""
        # Validatsiya
        xodim = self.xodim_combo.get()
        xamir = self.xamir_combo.get()
        qabul = Utils.validate_int(self.qabul_var.get())
        chiqqan = Utils.validate_int(self.chiqqan_var.get())
        brak = Utils.validate_int(self.brak_var.get())
        yeyilgan = Utils.validate_int(self.yeyilgan_var.get())
        
        if not xodim or not xamir or not qabul or not chiqqan:
            messagebox.showerror("Xatolik", "Majburiy maydonlarni to'ldiring!")
            return
        
        # ID larni olish
        xodim_id = int(xodim.split(" - ")[0])
        xamir_id = int(xamir.split(" ")[0])
        
        # Sof non
        sof = chiqqan - brak - yeyilgan
        if sof < 0:
            messagebox.showerror("Xatolik", "Sof non manfiy bo'lishi mumkin emas!")
            return
        
        # O'rtacha unumdorlik
        unumdorlik = Utils.calculate_percentage(sof, qabul) if qabul > 0 else 0
        
        # Saqlash
        try:
            self.db.execute(
                """INSERT INTO non_yasash 
                   (sana, xamir_id, xodim_id, qabul_xamir, chiqqan_non, 
                    brak_non, yeyilgan_non, sof_non, brak_sababi, ortacha_unumdorlik)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (Config.get_date(), xamir_id, xodim_id, qabul, chiqqan,
                 brak, yeyilgan, sof, self.brak_sababi_combo.get(), unumdorlik)
            )
            self.db.commit()
            
            # Xamirni keyingi bosqichga o'tkazish
            self.db.execute(
                "UPDATE xamir SET keyingi_bosqich = 1 WHERE id = ?",
                (xamir_id,)
            )
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", "Non yasash muvaffaqiyatli qayd etildi!")
            self.clear_form()
            self.load_xamirlar()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def clear_form(self):
        """Formani tozalash"""
        self.qabul_var.set("")
        self.chiqqan_var.set("")
        self.brak_var.set("")
        self.yeyilgan_var.set("0")
        self.sof_non_var.set("0")
        self.brak_sababi_combo.current(0)

# ==================== TANDIR MODULI ====================
class TandirModule:
    """Tandir moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="🔥 TANDIR JARAYONI",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Forma frame
        form_frame = ttk.LabelFrame(self.main_frame, text="YANGI TANDIR JARAYONI", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 1-qator
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Tandir raqami:", width=15).pack(side=tk.LEFT, padx=5)
        self.tandir_combo = ttk.Combobox(row1, values=["1", "2", "3", "4"], state="readonly", width=10)
        self.tandir_combo.current(0)
        self.tandir_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Tandirchi:", width=15).pack(side=tk.LEFT, padx=5)
        self.tandirchi_combo = ttk.Combobox(row1, state="readonly", width=30)
        self.tandirchi_combo.pack(side=tk.LEFT, padx=5)
        
        # 2-qator
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Kirgan non:", width=15).pack(side=tk.LEFT, padx=5)
        self.kirgan_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.kirgan_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Chiqgan non:", width=15).pack(side=tk.LEFT, padx=5)
        self.chiqgan_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.chiqgan_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Brak non:", width=15).pack(side=tk.LEFT, padx=5)
        self.brak_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.brak_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 3-qator
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, pady=5)
        
        ttk.Label(row3, text="Samaradorlik:", width=15).pack(side=tk.LEFT, padx=5)
        self.samara_var = tk.StringVar(value="0%")
        ttk.Entry(row3, textvariable=self.samara_var, state='readonly', 
                  width=15, foreground=Config.COLORS['success']).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Holat:", width=15).pack(side=tk.LEFT, padx=5)
        self.holat_combo = ttk.Combobox(
            row3, 
            values=["normal", "nosoz", "ta'mirlash", "boshqa"],
            state="readonly",
            width=15
        )
        self.holat_combo.current(0)
        self.holat_combo.pack(side=tk.LEFT, padx=5)
        
        # 4-qator
        row4 = ttk.Frame(form_frame)
        row4.pack(fill=tk.X, pady=5)
        
        ttk.Label(row4, text="Nosozlik izohi:", width=15).pack(side=tk.LEFT, padx=5)
        self.nosozlik_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.nosozlik_var, width=50).pack(side=tk.LEFT, padx=5)
        
        # Tugmalar
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="📝 SAQLASH",
            command=self.save_tandir,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📊 HISOBlASH",
            command=self.calculate_samara
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🧹 TOZALASH",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        table_frame = ttk.LabelFrame(self.main_frame, text="TANDIR TARIXI", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Sana", "Tandir", "Tandirchi", "Kirgan", "Chiqgan", 
                   "Brak", "Samara", "Holat", "Izoh")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ma'lumotlarni yuklash
        self.load_tandirchilar()
        self.load_data()
        
        # Avtomatik hisoblash
        self.kirgan_var.trace('w', self.calculate_samara)
        self.chiqgan_var.trace('w', self.calculate_samara)
        self.brak_var.trace('w', self.calculate_samara)
    
    def load_tandirchilar(self):
        """Tandirchilarni yuklash"""
        results = self.db.fetchall(
            "SELECT id, ism FROM xodimlar WHERE lavozim LIKE '%tandir%' AND status = 'faol'"
        )
        tandirchilar = [f"{row[0]} - {row[1]}" for row in results]
        self.tandirchi_combo['values'] = tandirchilar
        if tandirchilar:
            self.tandirchi_combo.current(0)
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT t.id, t.sana, t.tandir_raqami, xd.ism, 
                      t.kirgan_non, t.chiqqan_non, t.brak_non,
                      t.samaradorlik, t.holat, t.nosozlik
               FROM tandir t
               LEFT JOIN xodimlar xd ON t.tandirchi_id = xd.id
               ORDER BY t.id DESC"""
        )
        
        for row in results:
            samara_color = Utils.get_color_by_value(row[7])
            holat_color = Config.COLORS['success'] if row[8] == 'normal' else Config.COLORS['danger']
            
            self.tree.insert("", tk.END, values=row, tags=(samara_color,))
            self.tree.tag_configure(samara_color, foreground=samara_color)
    
    def calculate_samara(self, *args):
        """Samaradorlikni hisoblash"""
        try:
            kirgan = Utils.validate_int(self.kirgan_var.get()) or 0
            chiqgan = Utils.validate_int(self.chiqgan_var.get()) or 0
            
            if kirgan > 0:
                samara = (chiqgan / kirgan) * 100
                self.samara_var.set(f"{samara:.1f}%")
            else:
                self.samara_var.set("0%")
        except:
            self.samara_var.set("0%")
    
    def save_tandir(self):
        """Tandir jarayonini saqlash"""
        # Validatsiya
        tandir = self.tandir_combo.get()
        tandirchi = self.tandirchi_combo.get()
        kirgan = Utils.validate_int(self.kirgan_var.get())
        chiqgan = Utils.validate_int(self.chiqgan_var.get())
        brak = Utils.validate_int(self.brak_var.get()) or 0
        
        if not tandir or not tandirchi or not kirgan or not chiqgan:
            messagebox.showerror("Xatolik", "Majburiy maydonlarni to'ldiring!")
            return
        
        if chiqgan > kirgan:
            messagebox.showerror("Xatolik", "Chiqgan non kirgandan ko'p bo'lishi mumkin emas!")
            return
        
        # ID larni olish
        tandirchi_id = int(tandirchi.split(" - ")[0])
        
        # Samaradorlik
        samara = (chiqgan / kirgan) * 100 if kirgan > 0 else 0
        
        # Saqlash
        try:
            self.db.execute(
                """INSERT INTO tandir 
                   (sana, tandir_raqami, tandirchi_id, kirgan_non, 
                    chiqqan_non, brak_non, samaradorlik, nosozlik, holat)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (Config.get_date(), tandir, tandirchi_id, kirgan,
                 chiqgan, brak, samara, self.nosozlik_var.get(), 
                 self.holat_combo.get())
            )
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", "Tandir jarayoni muvaffaqiyatli qayd etildi!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def clear_form(self):
        """Formani tozalash"""
        self.kirgan_var.set("")
        self.chiqgan_var.set("")
        self.brak_var.set("")
        self.samara_var.set("0%")
        self.nosozlik_var.set("")
        self.holat_combo.current(0)

# ==================== MIJOZLAR MODULI ====================
class MijozlarModule:
    """Mijozlar moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="🏪 MIJOZLAR BOSHQARUVI",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Forma va jadval uchun frame
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chap tomon - forma
        left_frame = ttk.LabelFrame(content_frame, text="MIJOZ MA'LUMOTLARI", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Forma elementlari
        fields = [
            ("Nomi:", "nomi_var", 30),
            ("Telefon:", "telefon_var", 20),
            ("Manzil:", "manzil_var", 40),
            ("Turi:", "turi_combo", None),
            ("Kredit limiti:", "limit_var", 15),
            ("Holat:", "holat_combo", None)
        ]
        
        self.vars = {}
        for i, (label, var_name, width) in enumerate(fields):
            frame = ttk.Frame(left_frame)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT, padx=5)
            
            if "combo" in var_name:
                if var_name == "turi_combo":
                    combo = ttk.Combobox(frame, values=["dokon", "restoran", "boshqa"], 
                                         state="readonly", width=20)
                    combo.current(0)
                else:
                    combo = ttk.Combobox(frame, values=["faol", "nofaol", "bloklangan"], 
                                         state="readonly", width=20)
                    combo.current(0)
                
                combo.pack(side=tk.LEFT, padx=5)
                self.vars[var_name] = combo
            else:
                entry = ttk.Entry(frame, width=width)
                entry.pack(side=tk.LEFT, padx=5)
                self.vars[var_name] = tk.StringVar()
                entry.config(textvariable=self.vars[var_name])
        
        # Qarz ma'lumotlari
        stats_frame = ttk.LabelFrame(left_frame, text="QARZ MA'LUMOTLARI", padding=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        row1 = ttk.Frame(stats_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Jami qarz:", width=15).pack(side=tk.LEFT, padx=5)
        self.jami_qarz_var = tk.StringVar(value="0 so'm")
        ttk.Label(row1, textvariable=self.jami_qarz_var, 
                  foreground=Config.COLORS['danger']).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Jami tovar:", width=15).pack(side=tk.LEFT, padx=5)
        self.jami_tovar_var = tk.StringVar(value="0 so'm")
        ttk.Label(row1, textvariable=self.jami_tovar_var).pack(side=tk.LEFT, padx=5)
        
        # Tugmalar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        buttons = [
            ("➕ YANGI", self.new_mijoz),
            ("💾 SAQLASH", self.save_mijoz),
            ("✏️  TAHRIRLASH", self.edit_mijoz),
            ("🗑️  O'CHIRISH", self.delete_mijoz),
            ("💰 QARZ TO'LASH", self.pay_debt),
            ("🧹 TOZALASH", self.clear_form)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=5)
            if text == "💾 SAQLASH":
                btn.config(style="Accent.TButton")
        
        # O'ng tomon - jadval
        right_frame = ttk.LabelFrame(content_frame, text="MIJOZLAR RO'YXATI", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Qidiruv
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Qidirish:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍", command=self.search_mijoz, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔄", command=self.load_data, width=3).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        columns = ("ID", "Nomi", "Telefon", "Turi", "Limit", "Qarz", "Holat")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        col_widths = [50, 150, 100, 80, 80, 100, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tanlash hodisasi
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Ma'lumotlarni yuklash
        self.load_data()
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, nomi, telefon, turi, kredit_limit, 
                      jami_qarz, status
               FROM mijozlar 
               ORDER BY nomi"""
        )
        
        for row in results:
            qarz_color = Utils.get_qarz_color(row[5], row[4])
            status_color = Config.COLORS['success'] if row[6] == 'faol' else Config.COLORS['danger']
            
            self.tree.insert("", tk.END, values=row, tags=(qarz_color,))
            self.tree.tag_configure(qarz_color, foreground=qarz_color)
    
    def search_mijoz(self):
        """Mijoz qidirish"""
        query = self.search_var.get().strip()
        if not query:
            self.load_data()
            return
        
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, nomi, telefon, turi, kredit_limit, 
                      jami_qarz, status
               FROM mijozlar 
               WHERE nomi LIKE ? OR telefon LIKE ? OR manzil LIKE ?
               ORDER BY nomi""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        for row in results:
            qarz_color = Utils.get_qarz_color(row[5], row[4])
            self.tree.insert("", tk.END, values=row, tags=(qarz_color,))
            self.tree.tag_configure(qarz_color, foreground=qarz_color)
    
    def on_select(self, event):
        """Jadvaldan tanlash"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        mijoz_id = item['values'][0]
        
        # Ma'lumotlarni olish
        result = self.db.fetchone(
            "SELECT * FROM mijozlar WHERE id = ?",
            (mijoz_id,)
        )
        
        if result:
            self.current_id = mijoz_id
            self.vars['nomi_var'].set(result[1])
            self.vars['telefon_var'].set(result[2] if result[2] else "")
            self.vars['manzil_var'].set(result[3] if result[3] else "")
            self.vars['turi_combo'].set(result[4] if result[4] else "dokon")
            self.vars['limit_var'].set(str(result[5]) if result[5] else "0")
            self.vars['holat_combo'].set(result[9] if result[9] else "faol")
            
            self.jami_qarz_var.set(Utils.format_money(result[6]))
            self.jami_tovar_var.set(Utils.format_money(result[7]))
    
    def new_mijoz(self):
        """Yangi mijoz"""
        self.clear_form()
        self.current_id = None
    
    def save_mijoz(self):
        """Mijozni saqlash"""
        # Validatsiya
        nomi = self.vars['nomi_var'].get().strip()
        if not nomi:
            messagebox.showerror("Xatolik", "Mijoz nomini kiriting!")
            return
        
        telefon = self.vars['telefon_var'].get().strip()
        manzil = self.vars['manzil_var'].get().strip()
        turi = self.vars['turi_combo'].get()
        limit = Utils.validate_number(self.vars['limit_var'].get()) or 0
        holat = self.vars['holat_combo'].get()
        
        try:
            if hasattr(self, 'current_id') and self.current_id:
                # Yangilash
                self.db.execute(
                    """UPDATE mijozlar 
                       SET nomi = ?, telefon = ?, manzil = ?, turi = ?, 
                           kredit_limit = ?, status = ?
                       WHERE id = ?""",
                    (nomi, telefon, manzil, turi, limit, holat, self.current_id)
                )
                message = "Mijoz ma'lumotlari yangilandi!"
            else:
                # Yangi qo'shish
                self.db.execute(
                    """INSERT INTO mijozlar 
                       (nomi, telefon, manzil, turi, kredit_limit, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (nomi, telefon, manzil, turi, limit, holat)
                )
                message = "Yangi mijoz qo'shildi!"
            
            self.db.commit()
            messagebox.showinfo("Muvaffaqiyat", message)
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def edit_mijoz(self):
        """Mijozni tahrirlash"""
        if not hasattr(self, 'current_id') or not self.current_id:
            messagebox.showwarning("Ogohlantirish", "Iltimos, mijozni tanlang!")
            return
        
        self.save_mijoz()
    
    def delete_mijoz(self):
        """Mijozni o'chirish"""
        if not hasattr(self, 'current_id') or not self.current_id:
            messagebox.showwarning("Ogohlantirish", "Iltimos, mijozni tanlang!")
            return
        
        if messagebox.askyesno("Tasdiqlash", "Mijozni o'chirishni istaysizmi?"):
            try:
                self.db.execute(
                    "UPDATE mijozlar SET status = 'nofaol' WHERE id = ?",
                    (self.current_id,)
                )
                self.db.commit()
                
                messagebox.showinfo("Muvaffaqiyat", "Mijoz nofaol holatga o'tkazildi!")
                self.clear_form()
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("Xatolik", f"O'chirishda xatolik: {e}")
    
    def pay_debt(self):
        """Qarz to'lash"""
        if not hasattr(self, 'current_id') or not self.current_id:
            messagebox.showwarning("Ogohlantirish", "Iltimos, mijozni tanlang!")
            return
        
        # Qarz to'lash oynasi
        pay_window = tk.Toplevel(self.parent)
        pay_window.title("Qarz To'lash")
        pay_window.geometry("400x300")
        pay_window.transient(self.parent)
        pay_window.grab_set()
        
        # Ma'lumotlar
        result = self.db.fetchone(
            "SELECT nomi, jami_qarz FROM mijozlar WHERE id = ?",
            (self.current_id,)
        )
        
        if not result:
            pay_window.destroy()
            return
        
        mijoz_nomi, qarz = result
        
        ttk.Label(pay_window, text=f"Mijoz: {mijoz_nomi}", 
                  font=Config.FONTS['heading']).pack(pady=10)
        
        ttk.Label(pay_window, text=f"Jami qarz: {Utils.format_money(qarz)}",
                  foreground=Config.COLORS['danger']).pack(pady=5)
        
        ttk.Label(pay_window, text="To'lov summasi:").pack(pady=10)
        
        summa_var = tk.StringVar()
        ttk.Entry(pay_window, textvariable=summa_var, width=20).pack(pady=5)
        
        ttk.Label(pay_window, text="To'lov turi:").pack(pady=10)
        
        tolov_combo = ttk.Combobox(pay_window, values=["naqd", "bank", "boshqa"], 
                                   state="readonly", width=15)
        tolov_combo.current(0)
        tolov_combo.pack(pady=5)
        
        def process_payment():
            summa = Utils.validate_number(summa_var.get())
            if not summa or summa <= 0:
                messagebox.showerror("Xatolik", "To'g'ri summa kiriting!")
                return
            
            if summa > qarz:
                messagebox.showerror("Xatolik", "To'lov summasi qarzdan katta!")
                return
            
            try:
                # Qarzni kamaytirish
                self.db.execute(
                    "UPDATE mijozlar SET jami_qarz = jami_qarz - ? WHERE id = ?",
                    (summa, self.current_id)
                )
                
                # Kassa yozuvi
                self.db.execute(
                    """INSERT INTO kassa (sana, kirim, chiqim, balans, izoh)
                       VALUES (?, ?, 0, ?, ?)""",
                    (Config.get_date(), summa, summa, 
                     f"Qarz to'lovi: {mijoz_nomi}")
                )
                
                self.db.commit()
                
                messagebox.showinfo("Muvaffaqiyat", "Qarz to'landi!")
                pay_window.destroy()
                self.clear_form()
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("Xatolik", f"To'lovda xatolik: {e}")
        
        ttk.Button(pay_window, text="💳 TO'LASH", 
                  command=process_payment, style="Accent.TButton").pack(pady=20)
    
    def clear_form(self):
        """Formani tozalash"""
        for var_name, widget in self.vars.items():
            if isinstance(widget, ttk.Combobox):
                widget.current(0)
            elif isinstance(widget, tk.StringVar):
                widget.set("")
        
        if hasattr(self, 'current_id'):
            del self.current_id
        
        self.jami_qarz_var.set("0 so'm")
        self.jami_tovar_var.set("0 so'm")

# ==================== SOTUV MODULI ====================
class SotuvModule:
    """Sotuv moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="💰 SOTUV VA TARQATISH",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Ikki ustunli tuzilma
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chap ustun - forma
        left_frame = ttk.LabelFrame(content_frame, text="YANGI SOTUV", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Forma
        fields = [
            ("Mijoz:", "mijoz_combo", None),
            ("Non turi:", "non_turi_combo", None),
            ("Miqdor (dona):", "miqdor_var", 15),
            ("Narx (dona):", "narx_var", 15),
            ("Jami summa:", "jami_var", 20),
            ("To'lov turi:", "tolov_combo", None),
            ("To'landi:", "tolandi_var", 15),
            ("Qoldiq qarz:", "qoldiq_var", 15),
            ("Qaytgan non:", "qaytgan_var", 15),
            ("Sababi:", "sabab_combo", None)
        ]
        
        self.vars = {}
        for i, (label, var_name, width) in enumerate(fields):
            frame = ttk.Frame(left_frame)
            frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT, padx=5)
            
            if "combo" in var_name:
                if var_name == "mijoz_combo":
                    combo = ttk.Combobox(frame, state="readonly", width=30)
                elif var_name == "non_turi_combo":
                    combo = ttk.Combobox(frame, values=["Oddiy", "Yumaloq", "Patir", "Qalampir"], 
                                         state="readonly", width=20)
                    combo.current(0)
                elif var_name == "tolov_combo":
                    combo = ttk.Combobox(frame, values=["naqd", "qarz", "qisman"], 
                                         state="readonly", width=20)
                    combo.current(0)
                else:
                    combo = ttk.Combobox(frame, values=["Sifat", "Yetkazish", "Boshqa"], 
                                         state="readonly", width=20)
                    combo.current(0)
                
                combo.pack(side=tk.LEFT, padx=5)
                self.vars[var_name] = combo
            else:
                state = 'readonly' if var_name in ['jami_var', 'qoldiq_var'] else 'normal'
                entry = ttk.Entry(frame, width=width, state=state)
                entry.pack(side=tk.LEFT, padx=5)
                
                self.vars[var_name] = tk.StringVar()
                entry.config(textvariable=self.vars[var_name])
                
                if var_name == 'jami_var':
                    entry.config(foreground=Config.COLORS['success'])
                elif var_name == 'qoldiq_var':
                    entry.config(foreground=Config.COLORS['danger'])
        
        # Tugmalar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="🧮 HISOBlASH",
            command=self.calculate_total
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="📝 SAQLASH",
            command=self.save_sotuv,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🧹 TOZALASH",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=2)
        
        # O'ng ustun - jadval
        right_frame = ttk.LabelFrame(content_frame, text="SOTUV TARIXI", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Filtrlash
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Sana:").pack(side=tk.LEFT, padx=5)
        self.filter_date_var = tk.StringVar(value=Config.get_date())
        ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🔍", command=self.filter_data, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="🔄", command=self.load_data, width=3).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        columns = ("ID", "Sana", "Mijoz", "Non", "Miqdor", "Summa", "To'lov", "Holat")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        col_widths = [50, 80, 120, 80, 60, 90, 80, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ma'lumotlarni yuklash
        self.load_mijozlar()
        self.load_data()
        
        # Avtomatik hisoblash
        self.vars['miqdor_var'].trace('w', self.calculate_total)
        self.vars['narx_var'].trace('w', self.calculate_total)
        self.vars['tolandi_var'].trace('w', self.calculate_qoldiq)
        self.vars['tolov_combo'].trace('w', self.on_tolov_change)
    
    def load_mijozlar(self):
        """Mijozlarni yuklash"""
        results = self.db.fetchall(
            "SELECT id, nomi FROM mijozlar WHERE status = 'faol' ORDER BY nomi"
        )
        mijozlar = [f"{row[0]} - {row[1]}" for row in results]
        self.vars['mijoz_combo']['values'] = mijozlar
        if mijozlar:
            self.vars['mijoz_combo'].current(0)
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT s.id, s.sana, m.nomi, s.non_turi, s.miqdor, 
                      s.jami_summa, s.tolov_turi,
                      CASE 
                          WHEN s.qoldiq_qarz > 0 THEN 'QARZ'
                          ELSE "TO'LANDI"
                      END as holat
               FROM sotuvlar s
               LEFT JOIN mijozlar m ON s.mijoz_id = m.id
               WHERE s.status = 'active'
               ORDER BY s.id DESC
               LIMIT 100"""
        )
        
        for row in results:
            holat_color = Config.COLORS['success'] if row[7] == "TO'LANDI" else Config.COLORS['danger']
            self.tree.insert("", tk.END, values=row, tags=(holat_color,))
            self.tree.tag_configure(holat_color, foreground=holat_color)
    
    def filter_data(self):
        """Ma'lumotlarni filtrlash"""
        sana = self.filter_date_var.get().strip()
        if not sana:
            sana = Config.get_date()
        
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT s.id, s.sana, m.nomi, s.non_turi, s.miqdor, 
                      s.jami_summa, s.tolov_turi,
                      CASE 
                          WHEN s.qoldiq_qarz > 0 THEN 'QARZ'
                          ELSE "TO'LANDI"
                      END as holat
               FROM sotuvlar s
               LEFT JOIN mijozlar m ON s.mijoz_id = m.id
               WHERE s.sana = ? AND s.status = 'active'
               ORDER BY s.id DESC""",
            (sana,)
        )
        
        for row in results:
            holat_color = Config.COLORS['success'] if row[7] == "TO'LANDI" else Config.COLORS['danger']
            self.tree.insert("", tk.END, values=row, tags=(holat_color,))
            self.tree.tag_configure(holat_color, foreground=holat_color)
    
    def calculate_total(self, *args):
        """Jami summani hisoblash"""
        try:
            miqdor = Utils.validate_number(self.vars['miqdor_var'].get()) or 0
            narx = Utils.validate_number(self.vars['narx_var'].get()) or 0
            
            jami = miqdor * narx
            self.vars['jami_var'].set(f"{jami:,.0f}")
            
            # Qoldiq qarzni yangilash
            self.calculate_qoldiq()
            
        except:
            self.vars['jami_var'].set("0")
    
    def calculate_qoldiq(self, *args):
        """Qoldiq qarzni hisoblash"""
        try:
            jami_text = self.vars['jami_var'].get().replace(',', '')
            jami = float(jami_text) if jami_text else 0
            tolandi = Utils.validate_number(self.vars['tolandi_var'].get()) or 0
            
            qoldiq = max(0, jami - tolandi)
            self.vars['qoldiq_var'].set(f"{qoldiq:,.0f}")
            
        except:
            self.vars['qoldiq_var'].set("0")
    
    def on_tolov_change(self, *args):
        """To'lov turi o'zgarganda"""
        tolov_turi = self.vars['tolov_combo'].get()
        
        if tolov_turi == "naqd":
            self.vars['tolandi_var'].set(self.vars['jami_var'].get())
            self.vars['tolandi_var'].config(state='readonly')
        elif tolov_turi == "qarz":
            self.vars['tolandi_var'].set("0")
            self.vars['tolandi_var'].config(state='readonly')
        else:  # qisman
            self.vars['tolandi_var'].config(state='normal')
            self.vars['tolandi_var'].set("0")
    
    def save_sotuv(self):
        """Sotuvni saqlash"""
        # Validatsiya
        mijoz = self.vars['mijoz_combo'].get()
        non_turi = self.vars['non_turi_combo'].get()
        miqdor = Utils.validate_int(self.vars['miqdor_var'].get())
        narx = Utils.validate_number(self.vars['narx_var'].get())
        tolov_turi = self.vars['tolov_combo'].get()
        
        if not mijoz or not miqdor or not narx:
            messagebox.showerror("Xatolik", "Majburiy maydonlarni to'ldiring!")
            return
        
        # ID larni olish
        mijoz_id = int(mijoz.split(" - ")[0])
        
        # Summalar
        jami_text = self.vars['jami_var'].get().replace(',', '')
        jami = float(jami_text) if jami_text else 0
        
        tolandi_text = self.vars['tolandi_var'].get().replace(',', '')
        tolandi = float(tolandi_text) if tolandi_text else 0
        
        qoldiq_text = self.vars['qoldiq_var'].get().replace(',', '')
        qoldiq = float(qoldiq_text) if qoldiq_text else 0
        
        qaytgan = Utils.validate_int(self.vars['qaytgan_var'].get()) or 0
        
        try:
            # Sotuvni saqlash
            self.db.execute(
                """INSERT INTO sotuvlar 
                   (sana, mijoz_id, non_turi, miqdor, narx_dona, 
                    jami_summa, tolov_turi, tolandi, qoldiq_qarz,
                    qaytgan_non, qaytish_sababi)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (Config.get_date(), mijoz_id, non_turi, miqdor, narx,
                 jami, tolov_turi, tolandi, qoldiq,
                 qaytgan, self.vars['sabab_combo'].get())
            )
            
            # Mijoz qarzini yangilash
            if qoldiq > 0:
                self.db.execute(
                    "UPDATE mijozlar SET jami_qarz = jami_qarz + ? WHERE id = ?",
                    (qoldiq, mijoz_id)
                )
            
            # Mijoz jami tovarini yangilash
            self.db.execute(
                "UPDATE mijozlar SET jami_tovar = jami_tovar + ?, oxirgi_sana = ? WHERE id = ?",
                (jami, Config.get_date(), mijoz_id)
            )
            
            # Kassa yozuvi
            if tolandi > 0:
                self.db.execute(
                    """INSERT INTO kassa (sana, kirim, chiqim, balans, izoh)
                       VALUES (?, ?, 0, ?, ?)""",
                    (Config.get_date(), tolandi, tolandi, 
                     f"Sotuv: {mijoz.split(' - ')[1]}")
                )
            
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", "Sotuv muvaffaqiyatli qayd etildi!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def clear_form(self):
        """Formani tozalash"""
        for var_name, widget in self.vars.items():
            if isinstance(widget, ttk.Combobox):
                if var_name == 'mijoz_combo':
                    if widget['values']:
                        widget.current(0)
                elif var_name == 'non_turi_combo':
                    widget.current(0)
                elif var_name == 'tolov_combo':
                    widget.current(0)
                    self.on_tolov_change()
                elif var_name == 'sabab_combo':
                    widget.current(0)
            elif isinstance(widget, tk.StringVar):
                if var_name == 'jami_var':
                    widget.set("0")
                elif var_name == 'qoldiq_var':
                    widget.set("0")
                elif var_name == 'tolandi_var':
                    widget.set("0")
                elif var_name == 'qaytgan_var':
                    widget.set("0")
                else:
                    widget.set("")

# ==================== KASSA MODULI ====================
class KassaModule:
    """Kassa moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="💰 KASSA VA MOLIYA",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Statistikalar
        stats_frame = ttk.LabelFrame(self.main_frame, text="BUGUNGI HOLAT", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 4 ta statistik panel
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        self.stats_vars = {}
        stats_data = [
            ("Kunlik kirim", "kirim_var", Config.COLORS['success']),
            ("Kunlik chiqim", "chiqim_var", Config.COLORS['danger']),
            ("Bugungi balans", "balans_var", Config.COLORS['info']),
            ("Umumiy balans", "umumiy_var", Config.COLORS['warning'])
        ]
        
        for i, (title, var_name, color) in enumerate(stats_data):
            frame = ttk.Frame(stats_grid)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            
            ttk.Label(frame, text=title, font=Config.FONTS['small']).pack()
            
            var = tk.StringVar(value="0 so'm")
            ttk.Label(frame, textvariable=var, font=Config.FONTS['large'],
                     foreground=color).pack(pady=5)
            
            self.stats_vars[var_name] = var
            
            stats_grid.columnconfigure(i, weight=1)
        
        # Ikki ustunli tuzilma
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chap ustun - kirim/chiqim
        left_frame = ttk.LabelFrame(content_frame, text="KIRIM/CHIQIM", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Kirim/chiqim tanlash
        type_frame = ttk.Frame(left_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        self.trans_type = tk.StringVar(value="kirim")
        ttk.Radiobutton(type_frame, text="Kirim", variable=self.trans_type, 
                       value="kirim").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Chiqim", variable=self.trans_type, 
                       value="chiqim").pack(side=tk.LEFT, padx=10)
        
        # Summa
        summa_frame = ttk.Frame(left_frame)
        summa_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(summa_frame, text="Summa:", width=10).pack(side=tk.LEFT, padx=5)
        self.summa_var = tk.StringVar()
        ttk.Entry(summa_frame, textvariable=self.summa_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Izoh
        izoh_frame = ttk.Frame(left_frame)
        izoh_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(izoh_frame, text="Izoh:", width=10).pack(side=tk.LEFT, padx=5)
        self.izoh_var = tk.StringVar()
        ttk.Entry(izoh_frame, textvariable=self.izoh_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Tugmalar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="➕ KIRIM QO'SHISH",
            command=lambda: self.add_transaction("kirim"),
            style="Success.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="➖ CHIQIM QO'SHISH",
            command=lambda: self.add_transaction("chiqim"),
            style="Danger.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        # O'ng ustun - tarix
        right_frame = ttk.LabelFrame(content_frame, text="KASSA TARIXI", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Filtrlash
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Sana:").pack(side=tk.LEFT, padx=5)
        self.filter_date_var = tk.StringVar(value=Config.get_date())
        ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🔍", command=self.filter_data, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="🔄", command=self.load_data, width=3).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        columns = ("ID", "Sana", "Kirim", "Chiqim", "Balans", "Izoh")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        col_widths = [50, 80, 100, 100, 100, 150]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ma'lumotlarni yuklash
        self.load_stats()
        self.load_data()
    
    def load_stats(self):
        """Statistikani yuklash"""
        today = Config.get_date()
        
        # Bugungi kirim/chiqim
        result = self.db.fetchone(
            "SELECT SUM(kirim), SUM(chiqim) FROM kassa WHERE sana = ?",
            (today,)
        )
        
        kunlik_kirim = result[0] if result and result[0] else 0
        kunlik_chiqim = result[1] if result and result[1] else 0
        bugungi_balans = kunlik_kirim - kunlik_chiqim
        
        # Umumiy balans
        result = self.db.fetchone(
            "SELECT SUM(kirim) - SUM(chiqim) FROM kassa"
        )
        umumiy_balans = result[0] if result and result[0] else 0
        
        # Yangilash
        self.stats_vars['kirim_var'].set(Utils.format_money(kunlik_kirim))
        self.stats_vars['chiqim_var'].set(Utils.format_money(kunlik_chiqim))
        self.stats_vars['balans_var'].set(Utils.format_money(bugungi_balans))
        self.stats_vars['umumiy_var'].set(Utils.format_money(umumiy_balans))
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, sana, kirim, chiqim, balans, 
                      SUBSTR(izoh, 1, 30) || '...' as izoh
               FROM kassa 
               ORDER BY id DESC
               LIMIT 100"""
        )
        
        for row in results:
            self.tree.insert("", tk.END, values=(
                row[0],
                Utils.format_date(row[1]),
                Utils.format_money(row[2]),
                Utils.format_money(row[3]),
                Utils.format_money(row[4]),
                row[5]
            ))
    
    def filter_data(self):
        """Ma'lumotlarni filtrlash"""
        sana = self.filter_date_var.get().strip()
        if not sana:
            sana = Config.get_date()
        
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, sana, kirim, chiqim, balans, 
                      SUBSTR(izoh, 1, 30) || '...' as izoh
               FROM kassa 
               WHERE sana = ?
               ORDER BY id DESC""",
            (sana,)
        )
        
        for row in results:
            self.tree.insert("", tk.END, values=(
                row[0],
                Utils.format_date(row[1]),
                Utils.format_money(row[2]),
                Utils.format_money(row[3]),
                Utils.format_money(row[4]),
                row[5]
            ))
        
        # Statistikani yangilash
        self.load_stats()
    
    def add_transaction(self, trans_type: str):
        """Tranzaksiya qo'shish"""
        summa = Utils.validate_number(self.summa_var.get())
        izoh = self.izoh_var.get().strip()
        
        if not summa or summa <= 0:
            messagebox.showerror("Xatolik", "To'g'ri summa kiriting!")
            return
        
        if not izoh:
            messagebox.showerror("Xatolik", "Izohni kiriting!")
            return
        
        kirim = summa if trans_type == "kirim" else 0
        chiqim = summa if trans_type == "chiqim" else 0
        
        # Oldingi balansni olish
        result = self.db.fetchone(
            "SELECT balans FROM kassa ORDER BY id DESC LIMIT 1"
        )
        old_balans = result[0] if result else 0
        new_balans = old_balans + kirim - chiqim
        
        # Balansni tekshirish
        if new_balans < 0 and trans_type == "chiqim":
            if not messagebox.askyesno("Ogohlantirish", 
                                      "Chiqim balansni manfiyga olib chiqadi. Davom etasizmi?"):
                return
        
        try:
            # Kassa yozuvi
            self.db.execute(
                """INSERT INTO kassa (sana, kirim, chiqim, balans, izoh)
                   VALUES (?, ?, ?, ?, ?)""",
                (Config.get_date(), kirim, chiqim, new_balans, izoh)
            )
            
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", 
                               f"{trans_type.capitalize()} muvaffaqiyatli qo'shildi!")
            
            # Tozalash va yangilash
            self.summa_var.set("")
            self.izoh_var.set("")
            self.load_stats()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Qo'shishda xatolik: {e}")

# ==================== XARAJATLAR MODULI ====================
class XarajatlarModule:
    """Xarajatlar moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="💸 XARAJATLAR BOSHQARUVI",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Statistikalar
        stats_frame = ttk.LabelFrame(self.main_frame, text="OYLIK XARAJATLAR", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Xarajat turlari bo'yicha
        self.load_monthly_stats()
        
        # Ikki ustunli tuzilma
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chap ustun - yangi xarajat
        left_frame = ttk.LabelFrame(content_frame, text="YANGI XARAJAT", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Forma
        fields = [
            ("Turi:", "turi_combo", None),
            ("Miqdor:", "miqdor_var", 15),
            ("Narx:", "narx_var", 15),
            ("Jami summa:", "jami_var", 20),
            ("Izoh:", "izoh_var", 40)
        ]
        
        self.vars = {}
        for i, (label, var_name, width) in enumerate(fields):
            frame = ttk.Frame(left_frame)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT, padx=5)
            
            if var_name == "turi_combo":
                combo = ttk.Combobox(frame, values=[
                    "un", "gaz", "elektr", "suv", "ish_haqi", 
                    "transport", "ta'mirlash", "boshqa"
                ], state="readonly", width=20)
                combo.current(0)
                combo.pack(side=tk.LEFT, padx=5)
                self.vars[var_name] = combo
            else:
                state = 'readonly' if var_name == 'jami_var' else 'normal'
                entry = ttk.Entry(frame, width=width, state=state)
                entry.pack(side=tk.LEFT, padx=5)
                
                self.vars[var_name] = tk.StringVar()
                entry.config(textvariable=self.vars[var_name])
                
                if var_name == 'jami_var':
                    entry.config(foreground=Config.COLORS['danger'])
        
        # Tugmalar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="🧮 HISOBlASH",
            command=self.calculate_total
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="💾 SAQLASH",
            command=self.save_xarajat,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🧹 TOZALASH",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=2)
        
        # Avtomatik hisoblash
        self.vars['miqdor_var'].trace('w', self.calculate_total)
        self.vars['narx_var'].trace('w', self.calculate_total)
        
        # O'ng ustun - tarix
        right_frame = ttk.LabelFrame(content_frame, text="XARAJATLAR TARIXI", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Filtrlash
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Oy:").pack(side=tk.LEFT, padx=5)
        
        months = [f"{i:02d}" for i in range(1, 13)]
        self.filter_month_combo = ttk.Combobox(filter_frame, values=months, 
                                              state="readonly", width=5)
        self.filter_month_combo.set(date.today().strftime("%m"))
        self.filter_month_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Yil:").pack(side=tk.LEFT, padx=5)
        current_year = date.today().year
        years = [str(y) for y in range(current_year-2, current_year+3)]
        self.filter_year_combo = ttk.Combobox(filter_frame, values=years, 
                                             state="readonly", width=5)
        self.filter_year_combo.set(str(current_year))
        self.filter_year_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🔍", command=self.filter_data, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="🔄", command=self.load_data, width=3).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        columns = ("ID", "Sana", "Turi", "Miqdor", "Narx", "Summa", "Izoh")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        col_widths = [50, 80, 80, 70, 80, 100, 150]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ma'lumotlarni yuklash
        self.load_data()
    
    def load_monthly_stats(self):
        """Oylik statistikani yuklash"""
        current_month = date.today().strftime("%Y-%m")
        
        results = self.db.fetchall(
            """SELECT turi, SUM(jami_summa) as total
               FROM xarajatlar 
               WHERE strftime('%Y-%m', sana) = ?
               GROUP BY turi
               ORDER BY total DESC""",
            (current_month,)
        )
        
        # Statistikani ko'rsatish
        stats_frame = self.main_frame.winfo_children()[1]
        for widget in stats_frame.winfo_children():
            widget.destroy()
        
        if results:
            # Diagramma uchun frame
            chart_frame = ttk.Frame(stats_frame)
            chart_frame.pack(fill=tk.X, pady=10)
            
            total = sum(row[1] for row in results)
            
            for turi, summa in results:
                frame = ttk.Frame(chart_frame)
                frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(frame, text=turi, width=15).pack(side=tk.LEFT)
                
                # Progress bar
                percent = (summa / total * 100) if total > 0 else 0
                progress = ttk.Progressbar(frame, length=200, 
                                          maximum=100, value=percent)
                progress.pack(side=tk.LEFT, padx=5)
                
                ttk.Label(frame, text=f"{summa:,.0f} so'm ({percent:.1f}%)",
                         width=20).pack(side=tk.LEFT)
            
            # Jami
            total_frame = ttk.Frame(stats_frame)
            total_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(total_frame, text="JAMI:", font=Config.FONTS['heading']).pack(side=tk.LEFT)
            ttk.Label(total_frame, text=f"{total:,.0f} so'm", 
                     font=Config.FONTS['heading'],
                     foreground=Config.COLORS['danger']).pack(side=tk.LEFT, padx=10)
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, sana, turi, miqdor, narx, jami_summa,
                      SUBSTR(izoh, 1, 30) || '...' as izoh
               FROM xarajatlar 
               ORDER BY id DESC
               LIMIT 100"""
        )
        
        for row in results:
            self.tree.insert("", tk.END, values=(
                row[0],
                Utils.format_date(row[1]),
                row[2],
                f"{row[3]:.1f}" if row[3] else "0",
                Utils.format_money(row[4]) if row[4] else "0",
                Utils.format_money(row[5]),
                row[6]
            ))
        
        # Oylik statistikani yangilash
        self.load_monthly_stats()
    
    def filter_data(self):
        """Ma'lumotlarni filtrlash"""
        month = self.filter_month_combo.get()
        year = self.filter_year_combo.get()
        
        if not month or not year:
            return
        
        period = f"{year}-{month}"
        
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, sana, turi, miqdor, narx, jami_summa,
                      SUBSTR(izoh, 1, 30) || '...' as izoh
               FROM xarajatlar 
               WHERE strftime('%Y-%m', sana) = ?
               ORDER BY id DESC""",
            (period,)
        )
        
        for row in results:
            self.tree.insert("", tk.END, values=(
                row[0],
                Utils.format_date(row[1]),
                row[2],
                f"{row[3]:.1f}" if row[3] else "0",
                Utils.format_money(row[4]) if row[4] else "0",
                Utils.format_money(row[5]),
                row[6]
            ))
    
    def calculate_total(self, *args):
        """Jami summani hisoblash"""
        try:
            miqdor = Utils.validate_number(self.vars['miqdor_var'].get()) or 0
            narx = Utils.validate_number(self.vars['narx_var'].get()) or 0
            
            jami = miqdor * narx
            self.vars['jami_var'].set(f"{jami:,.0f}")
            
        except:
            self.vars['jami_var'].set("0")
    
    def save_xarajat(self):
        """Xarajatni saqlash"""
        # Validatsiya
        turi = self.vars['turi_combo'].get()
        miqdor = Utils.validate_number(self.vars['miqdor_var'].get())
        narx = Utils.validate_number(self.vars['narx_var'].get())
        izoh = self.vars['izoh_var'].get().strip()
        
        if not turi or not miqdor or not narx:
            messagebox.showerror("Xatolik", "Majburiy maydonlarni to'ldiring!")
            return
        
        # Jami summa
        jami_text = self.vars['jami_var'].get().replace(',', '')
        jami = float(jami_text) if jami_text else 0
        
        try:
            # Xarajatni saqlash
            self.db.execute(
                """INSERT INTO xarajatlar (sana, turi, miqdor, narx, jami_summa, izoh)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (Config.get_date(), turi, miqdor, narx, jami, izoh)
            )
            
            # Kassa chiqimi
            self.db.execute(
                """INSERT INTO kassa (sana, kirim, chiqim, balans, izoh)
                   VALUES (?, 0, ?, ?, ?)""",
                (Config.get_date(), jami, -jami, f"Xarajat: {turi} - {izoh}")
            )
            
            self.db.commit()
            
            messagebox.showinfo("Muvaffaqiyat", "Xarajat muvaffaqiyatli qayd etildi!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def clear_form(self):
        """Formani tozalash"""
        for var_name, widget in self.vars.items():
            if isinstance(widget, ttk.Combobox):
                if var_name == 'turi_combo':
                    widget.current(0)
            elif isinstance(widget, tk.StringVar):
                widget.set("")

# ==================== XODIMLAR MODULI ====================
class XodimlarModule:
    """Xodimlar moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="👥 XODIMLAR BOSHQARUVI",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Statistikalar
        stats_frame = ttk.LabelFrame(self.main_frame, text="XODIM STATISTIKASI", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 3 ta statistik panel
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        self.stats_vars = {}
        stats_data = [
            ("Jami xodimlar", "jami_var", Config.COLORS['info']),
            ("Faol xodimlar", "faol_var", Config.COLORS['success']),
            ("O'rtacha reyting", "reyting_var", Config.COLORS['warning'])
        ]
        
        for i, (title, var_name, color) in enumerate(stats_data):
            frame = ttk.Frame(stats_grid)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            
            ttk.Label(frame, text=title, font=Config.FONTS['small']).pack()
            
            var = tk.StringVar(value="0")
            ttk.Label(frame, textvariable=var, font=Config.FONTS['large'],
                     foreground=color).pack(pady=5)
            
            self.stats_vars[var_name] = var
            
            stats_grid.columnconfigure(i, weight=1)
        
        # Ikki ustunli tuzilma
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chap ustun - forma
        left_frame = ttk.LabelFrame(content_frame, text="XODIM MA'LUMOTLARI", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Forma
        fields = [
            ("Ism:", "ism_var", 30),
            ("Lavozim:", "lavozim_combo", None),
            ("Telefon:", "telefon_var", 20),
            ("Ish boshlash:", "ish_boshlash_var", 15),
            ("Oylik maosh:", "maosh_var", 15),
            ("Bonus:", "bonus_var", 15),
            ("Jarima:", "jarima_var", 15),
            ("Reyting:", "reyting_var_form", 15),
            ("Holat:", "holat_combo", None)
        ]
        
        self.vars = {}
        for i, (label, var_name, width) in enumerate(fields):
            frame = ttk.Frame(left_frame)
            frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT, padx=5)
            
            if "combo" in var_name:
                if var_name == "lavozim_combo":
                    combo = ttk.Combobox(frame, values=[
                        "xamirchi", "tandirchi", "sotuvchi", 
                        "menejer", "direktor", "boshqa"
                    ], state="readonly", width=20)
                    combo.current(0)
                else:
                    combo = ttk.Combobox(frame, values=["faol", "nofaol"], 
                                         state="readonly", width=20)
                    combo.current(0)
                
                combo.pack(side=tk.LEFT, padx=5)
                self.vars[var_name] = combo
            else:
                state = 'readonly' if var_name == 'reyting_var_form' else 'normal'
                entry = ttk.Entry(frame, width=width, state=state)
                entry.pack(side=tk.LEFT, padx=5)
                
                self.vars[var_name] = tk.StringVar()
                entry.config(textvariable=self.vars[var_name])
                
                if var_name == 'reyting_var_form':
                    entry.config(foreground=Config.COLORS['warning'])
                elif var_name in ['bonus_var', 'jarima_var']:
                    entry.config(foreground=Config.COLORS['danger'])
        
        # Tugmalar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="➕ YANGI",
            command=self.new_xodim
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="💾 SAQLASH",
            command=self.save_xodim,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="✏️  TAHRIRLASH",
            command=self.edit_xodim
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🧹 TOZALASH",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=2)
        
        # O'ng ustun - jadval
        right_frame = ttk.LabelFrame(content_frame, text="XODIMLAR RO'YXATI", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Qidiruv
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Qidirish:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍", command=self.search_xodim, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔄", command=self.load_data, width=3).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        columns = ("ID", "Ism", "Lavozim", "Telefon", "Maosh", "Bonus", "Jarima", "Reyting", "Holat")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        col_widths = [50, 120, 80, 100, 80, 70, 70, 70, 70]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tanlash hodisasi
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Ma'lumotlarni yuklash
        self.load_stats()
        self.load_data()
    
    def load_stats(self):
        """Statistikani yuklash"""
        # Jami xodimlar
        result = self.db.fetchone("SELECT COUNT(*) FROM xodimlar")
        jami = result[0] if result else 0
        
        # Faol xodimlar
        result = self.db.fetchone("SELECT COUNT(*) FROM xodimlar WHERE status = 'faol'")
        faol = result[0] if result else 0
        
        # O'rtacha reyting
        result = self.db.fetchone("SELECT AVG(reyting) FROM xodimlar WHERE status = 'faol'")
        reyting = result[0] if result and result[0] else 0
        
        self.stats_vars['jami_var'].set(str(jami))
        self.stats_vars['faol_var'].set(str(faol))
        self.stats_vars['reyting_var'].set(f"{reyting:.1f}")
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, ism, lavozim, telefon, oylik_maosh, 
                      bonus, jarima, reyting, status
               FROM xodimlar 
               ORDER BY ism"""
        )
        
        for row in results:
            reyting_color = Utils.get_color_by_value(row[7])
            status_color = Config.COLORS['success'] if row[8] == 'faol' else Config.COLORS['danger']
            
            self.tree.insert("", tk.END, values=row, tags=(reyting_color,))
            self.tree.tag_configure(reyting_color, foreground=reyting_color)
    
    def search_xodim(self):
        """Xodim qidirish"""
        query = self.search_var.get().strip()
        if not query:
            self.load_data()
            return
        
        self.tree.delete(*self.tree.get_children())
        
        results = self.db.fetchall(
            """SELECT id, ism, lavozim, telefon, oylik_maosh, 
                      bonus, jarima, reyting, status
               FROM xodimlar 
               WHERE ism LIKE ? OR lavozim LIKE ? OR telefon LIKE ?
               ORDER BY ism""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        for row in results:
            reyting_color = Utils.get_color_by_value(row[7])
            self.tree.insert("", tk.END, values=row, tags=(reyting_color,))
            self.tree.tag_configure(reyting_color, foreground=reyting_color)
    
    def on_select(self, event):
        """Jadvaldan tanlash"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        xodim_id = item['values'][0]
        
        # Ma'lumotlarni olish
        result = self.db.fetchone(
            "SELECT * FROM xodimlar WHERE id = ?",
            (xodim_id,)
        )
        
        if result:
            self.current_id = xodim_id
            self.vars['ism_var'].set(result[1])
            self.vars['lavozim_combo'].set(result[2])
            self.vars['telefon_var'].set(result[3] if result[3] else "")
            self.vars['ish_boshlash_var'].set(result[4] if result[4] else "")
            self.vars['maosh_var'].set(str(result[5]) if result[5] else "0")
            self.vars['bonus_var'].set(str(result[6]) if result[6] else "0")
            self.vars['jarima_var'].set(str(result[7]) if result[7] else "0")
            self.vars['reyting_var_form'].set(str(result[8]) if result[8] else "100")
            self.vars['holat_combo'].set(result[9] if result[9] else "faol")
    
    def new_xodim(self):
        """Yangi xodim"""
        self.clear_form()
        self.current_id = None
        self.vars['ish_boshlash_var'].set(Config.get_date())
        self.vars['reyting_var_form'].set("100.0")
    
    def save_xodim(self):
        """Xodimni saqlash"""
        # Validatsiya
        ism = self.vars['ism_var'].get().strip()
        lavozim = self.vars['lavozim_combo'].get()
        maosh = Utils.validate_number(self.vars['maosh_var'].get())
        
        if not ism or not lavozim or not maosh:
            messagebox.showerror("Xatolik", "Majburiy maydonlarni to'ldiring!")
            return
        
        telefon = self.vars['telefon_var'].get().strip()
        ish_boshlash = self.vars['ish_boshlash_var'].get().strip() or Config.get_date()
        bonus = Utils.validate_number(self.vars['bonus_var'].get()) or 0
        jarima = Utils.validate_number(self.vars['jarima_var'].get()) or 0
        reyting = Utils.validate_number(self.vars['reyting_var_form'].get()) or 100.0
        holat = self.vars['holat_combo'].get()
        
        try:
            if hasattr(self, 'current_id') and self.current_id:
                # Yangilash
                self.db.execute(
                    """UPDATE xodimlar 
                       SET ism = ?, lavozim = ?, telefon = ?, ish_boshlash = ?,
                           oylik_maosh = ?, bonus = ?, jarima = ?, reyting = ?, status = ?
                       WHERE id = ?""",
                    (ism, lavozim, telefon, ish_boshlash, maosh, 
                     bonus, jarima, reyting, holat, self.current_id)
                )
                message = "Xodim ma'lumotlari yangilandi!"
            else:
                # Yangi qo'shish
                self.db.execute(
                    """INSERT INTO xodimlar 
                       (ism, lavozim, telefon, ish_boshlash, oylik_maosh, 
                        bonus, jarima, reyting, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (ism, lavozim, telefon, ish_boshlash, maosh, 
                     bonus, jarima, reyting, holat)
                )
                message = "Yangi xodim qo'shildi!"
            
            self.db.commit()
            messagebox.showinfo("Muvaffaqiyat", message)
            self.clear_form()
            self.load_stats()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Saqlashda xatolik: {e}")
    
    def edit_xodim(self):
        """Xodimni tahrirlash"""
        if not hasattr(self, 'current_id') or not self.current_id:
            messagebox.showwarning("Ogohlantirish", "Iltimos, xodimni tanlang!")
            return
        
        self.save_xodim()
    
    def clear_form(self):
        """Formani tozalash"""
        for var_name, widget in self.vars.items():
            if isinstance(widget, ttk.Combobox):
                if var_name == 'lavozim_combo':
                    widget.current(0)
                elif var_name == 'holat_combo':
                    widget.current(0)
            elif isinstance(widget, tk.StringVar):
                if var_name in ['bonus_var', 'jarima_var']:
                    widget.set("0")
                elif var_name == 'reyting_var_form':
                    widget.set("100.0")
                else:
                    widget.set("")
        
        if hasattr(self, 'current_id'):
            del self.current_id

# ==================== HISOBOTLAR MODULI ====================
class HisobotlarModule:
    """Hisobotlar moduli"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            self.main_frame,
            text="📊 HISOBOTLAR VA TAHLLILAR",
            font=Config.FONTS['title'],
            foreground=Config.COLORS['primary']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Hisobot turlari
        report_frame = ttk.LabelFrame(self.main_frame, text="HISOBOT TURLARI", padding=15)
        report_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 3 ustunli tugmalar
        button_grid = ttk.Frame(report_frame)
        button_grid.pack(fill=tk.X)
        
        reports = [
            ("📅 Kunlik hisobot", self.daily_report),
            ("📆 Haftalik hisobot", self.weekly_report),
            ("📊 Oylik hisobot", self.monthly_report),
            ("📈 Yillik hisobot", self.yearly_report),
            ("💰 Foyda/zarar", self.profit_report),
            ("⚠️  Brak tahlili", self.brak_report),
            ("🏭 Ishlab chiqarish", self.production_report),
            ("👥 Xodimlar", self.workers_report),
            ("📉 Qarzdorlik", self.debt_report)
        ]
        
        for i, (text, command) in enumerate(reports):
            row = i // 3
            col = i % 3
            
            if col == 0:
                frame = ttk.Frame(button_grid)
                frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
                button_grid.rowconfigure(row, weight=1)
            
            btn = ttk.Button(frame, text=text, command=command, width=25)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Filtrlash parametrlari
        filter_frame = ttk.LabelFrame(self.main_frame, text="FILTRLASH", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Sana oralig'i
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Dan:", width=10).pack(side=tk.LEFT, padx=5)
        self.start_date_var = tk.StringVar(value=Config.get_date())
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="Gacha:", width=10).pack(side=tk.LEFT, padx=5)
        self.end_date_var = tk.StringVar(value=Config.get_date())
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(date_frame, text="🔄 Bugun", command=self.set_today, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(date_frame, text="📅 Oy", command=self.set_month, width=8).pack(side=tk.LEFT, padx=5)
        
        # Hisobot natijalari
        result_frame = ttk.LabelFrame(self.main_frame, text="HISOBOT NATIJALARI", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Matn maydoni
        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Eksport tugmalari
        export_frame = ttk.Frame(result_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            export_frame,
            text="💾 Excel ga saqlash",
            command=self.export_excel
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="🖨️  Chop etish",
            command=self.print_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="🧹 Tozalash",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)
    
    def set_today(self):
        """Bugungi sana"""
        today = Config.get_date()
        self.start_date_var.set(today)
        self.end_date_var.set(today)
    
    def set_month(self):
        """Oylik sana"""
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        
        self.start_date_var.set(first_day.strftime(Config.DATE_FORMAT))
        self.end_date_var.set(last_day.strftime(Config.DATE_FORMAT))
    
    def daily_report(self):
        """Kunlik hisobot"""
        sana = self.start_date_var.get()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"📅 KUNLIK HISOBOT: {sana}\n")
        self.result_text.insert(tk.END, "="*50 + "\n\n")
        
        # Sotuvlar
        self.result_text.insert(tk.END, "💰 SOTUVLAR:\n")
        results = self.db.fetchall(
            """SELECT m.nomi, SUM(s.miqdor), SUM(s.jami_summa), 
                      SUM(s.qoldiq_qarz)
               FROM sotuvlar s
               LEFT JOIN mijozlar m ON s.mijoz_id = m.id
               WHERE s.sana = ? AND s.status = 'active'
               GROUP BY m.nomi
               ORDER BY SUM(s.jami_summa) DESC""",
            (sana,)
        )
        
        total_sales = 0
        total_qarz = 0
        
        for row in results:
            self.result_text.insert(tk.END, 
                f"  {row[0]}: {row[1]} dona, {row[2]:,.0f} so'm")
            if row[3] > 0:
                self.result_text.insert(tk.END, f" (qarz: {row[3]:,.0f} so'm)")
            self.result_text.insert(tk.END, "\n")
            
            total_sales += row[2] if row[2] else 0
            total_qarz += row[3] if row[3] else 0
        
        self.result_text.insert(tk.END, 
            f"\n  JAMI: {total_sales:,.0f} so'm, Qarz: {total_qarz:,.0f} so'm\n\n")
        
        # Ishlab chiqarish
        self.result_text.insert(tk.END, "🏭 ISHLAB CHIQARISH:\n")
        
        # Xamir
        result = self.db.fetchone(
            "SELECT COUNT(*), SUM(xamir_soni) FROM xamir WHERE sana = ?",
            (sana,)
        )
        if result and result[0]:
            self.result_text.insert(tk.END, 
                f"  Xamir: {result[0]} marta, {result[1]} dona\n")
        
        # Non yasash
        result = self.db.fetchone(
            "SELECT SUM(chiqqan_non), SUM(brak_non) FROM non_yasash WHERE sana = ?",
            (sana,)
        )
        if result and result[0]:
            self.result_text.insert(tk.END, 
                f"  Non yasash: {result[0]} dona, Brak: {result[1]} dona\n")
        
        # Tandir
        result = self.db.fetchone(
            "SELECT SUM(chiqqan_non), SUM(brak_non) FROM tandir WHERE sana = ?",
            (sana,)
        )
        if result and result[0]:
            self.result_text.insert(tk.END, 
                f"  Tandir: {result[0]} dona, Brak: {result[1]} dona\n")
        
        self.result_text.insert(tk.END, "\n")
        
        # Kassa
        self.result_text.insert(tk.END, "💰 KASSA HOLATI:\n")
        result = self.db.fetchone(
            "SELECT SUM(kirim), SUM(chiqim) FROM kassa WHERE sana = ?",
            (sana,)
        )
        if result:
            kirim = result[0] if result[0] else 0
            chiqim = result[1] if result[1] else 0
            balans = kirim - chiqim
            
            self.result_text.insert(tk.END, 
                f"  Kirim: {kirim:,.0f} so'm\n")
            self.result_text.insert(tk.END, 
                f"  Chiqim: {chiqim:,.0f} so'm\n")
            self.result_text.insert(tk.END, 
                f"  Balans: {balans:,.0f} so'm\n")
        
        self.result_text.see(1.0)
    
    def weekly_report(self):
        """Haftalik hisobot"""
        end_date = datetime.strptime(self.end_date_var.get(), Config.DATE_FORMAT)
        start_date = end_date - timedelta(days=6)
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, 
            f"📆 HAFTALIK HISOBOT: {start_date.date()} - {end_date.date()}\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        
        # Kunlik statistika
        self.result_text.insert(tk.END, "📈 KUNLIK STATISTIKA:\n")
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime(Config.DATE_FORMAT)
            
            # Sotuvlar
            result = self.db.fetchone(
                "SELECT SUM(miqdor), SUM(jami_summa) FROM sotuvlar WHERE sana = ?",
                (date_str,)
            )
            
            sales = result[0] if result and result[0] else 0
            amount = result[1] if result and result[1] else 0
            
            self.result_text.insert(tk.END, 
                f"  {date_str}: {sales} dona, {amount:,.0f} so'm\n")
        
        self.result_text.insert(tk.END, "\n")
        
        # Haftalik yig'indi
        self.result_text.insert(tk.END, "📊 HAFTALIK YIG'INDI:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   SUM(s.miqdor) as total_sales,
                   SUM(s.jami_summa) as total_amount,
                   SUM(s.qoldiq_qarz) as total_debt,
                   SUM(x.jami_summa) as total_expenses
               FROM sotuvlar s
               LEFT JOIN xarajatlar x ON x.sana BETWEEN ? AND ?
               WHERE s.sana BETWEEN ? AND ?""",
            (start_date.strftime(Config.DATE_FORMAT), end_date.strftime(Config.DATE_FORMAT),
             start_date.strftime(Config.DATE_FORMAT), end_date.strftime(Config.DATE_FORMAT))
        )
        
        if results:
            row = results[0]
            profit = (row[1] or 0) - (row[3] or 0)
            
            self.result_text.insert(tk.END, 
                f"  Jami sotuv: {row[0] or 0} dona\n")
            self.result_text.insert(tk.END, 
                f"  Jami tushum: {row[1] or 0:,.0f} so'm\n")
            self.result_text.insert(tk.END, 
                f"  Jami qarz: {row[2] or 0:,.0f} so'm\n")
            self.result_text.insert(tk.END, 
                f"  Jami xarajat: {row[3] or 0:,.0f} so'm\n")
            self.result_text.insert(tk.END, 
                f"  Sof foyda: {profit:,.0f} so'm\n")
        
        self.result_text.see(1.0)
    
    def monthly_report(self):
        """Oylik hisobot"""
        start_date = self.start_date_var.get()
        year, month = start_date.split('-')[:2]
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"📊 OYLIK HISOBOT: {year}-{month}\n")
        self.result_text.insert(tk.END, "="*50 + "\n\n")
        
        # Sotuvlar statistika
        self.result_text.insert(tk.END, "💰 SOTUV STATISTIKASI:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   m.nomi,
                   SUM(s.miqdor) as total_qty,
                   SUM(s.jami_summa) as total_amount,
                   SUM(s.qoldiq_qarz) as total_debt
               FROM sotuvlar s
               LEFT JOIN mijozlar m ON s.mijoz_id = m.id
               WHERE strftime('%Y-%m', s.sana) = ?
               GROUP BY m.nomi
               ORDER BY total_amount DESC
               LIMIT 10""",
            (f"{year}-{month}",)
        )
        
        for row in results:
            self.result_text.insert(tk.END, 
                f"  {row[0]}: {row[1]} dona, {row[2]:,.0f} so'm")
            if row[3] > 0:
                self.result_text.insert(tk.END, f" (qarz: {row[3]:,.0f} so'm)")
            self.result_text.insert(tk.END, "\n")
        
        self.result_text.insert(tk.END, "\n")
        
        # Xarajatlar statistika
        self.result_text.insert(tk.END, "💸 XARAJATLAR STATISTIKASI:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   turi,
                   SUM(jami_summa) as total
               FROM xarajatlar 
               WHERE strftime('%Y-%m', sana) = ?
               GROUP BY turi
               ORDER BY total DESC""",
            (f"{year}-{month}",)
        )
        
        total_expenses = 0
        for row in results:
            self.result_text.insert(tk.END, 
                f"  {row[0]}: {row[1]:,.0f} so'm\n")
            total_expenses += row[1]
        
        self.result_text.insert(tk.END, 
            f"\n  Jami xarajat: {total_expenses:,.0f} so'm\n\n")
        
        # Ishlab chiqarish statistika
        self.result_text.insert(tk.END, "🏭 ISHLAB CHIQARISH STATISTIKASI:\n")
        
        # Brak foizi
        results = self.db.fetchall(
            """SELECT 
                   'Xamir' as bosqich,
                   SUM(xamir_soni) as total,
                   SUM(xamir_soni * (100 - samaradorlik) / 100) as brak
               FROM xamir 
               WHERE strftime('%Y-%m', sana) = ?
               UNION ALL
               SELECT 
                   'Non yasash' as bosqich,
                   SUM(chiqqan_non) as total,
                   SUM(brak_non) as brak
               FROM non_yasash 
               WHERE strftime('%Y-%m', sana) = ?
               UNION ALL
               SELECT 
                   'Tandir' as bosqich,
                   SUM(chiqqan_non) as total,
                   SUM(brak_non) as brak
               FROM tandir 
               WHERE strftime('%Y-%m', sana) = ?""",
            (f"{year}-{month}", f"{year}-{month}", f"{year}-{month}")
        )
        
        for row in results:
            if row[1] and row[1] > 0:
                brak_percent = (row[2] / row[1] * 100) if row[1] > 0 else 0
                self.result_text.insert(tk.END, 
                    f"  {row[0]}: {row[1]:.0f} dona, Brak: {brak_percent:.1f}%\n")
        
        self.result_text.see(1.0)
    
    def profit_report(self):
        """Foyda/zarar hisoboti"""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, 
            f"💰 FOYDA/ZARAR HISOBOTI: {start_date} - {end_date}\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        
        # Kirimlar (sotuvlar)
        result = self.db.fetchone(
            "SELECT SUM(jami_summa) FROM sotuvlar WHERE sana BETWEEN ? AND ?",
            (start_date, end_date)
        )
        total_income = result[0] if result and result[0] else 0
        
        # Xarajatlar
        result = self.db.fetchone(
            "SELECT SUM(jami_summa) FROM xarajatlar WHERE sana BETWEEN ? AND ?",
            (start_date, end_date)
        )
        total_expenses = result[0] if result and result[0] else 0
        
        # Sof foyda
        net_profit = total_income - total_expenses
        
        self.result_text.insert(tk.END, "📈 KIRIMLAR:\n")
        self.result_text.insert(tk.END, f"  Sotuvlar: {total_income:,.0f} so'm\n\n")
        
        self.result_text.insert(tk.END, "📉 CHIQIMLAR:\n")
        
        # Xarajatlar turlari bo'yicha
        results = self.db.fetchall(
            """SELECT turi, SUM(jami_summa) 
               FROM xarajatlar 
               WHERE sana BETWEEN ? AND ?
               GROUP BY turi
               ORDER BY SUM(jami_summa) DESC""",
            (start_date, end_date)
        )
        
        for row in results:
            self.result_text.insert(tk.END, f"  {row[0]}: {row[1]:,.0f} so'm\n")
        
        self.result_text.insert(tk.END, f"\n  Jami xarajat: {total_expenses:,.0f} so'm\n\n")
        
        self.result_text.insert(tk.END, "📊 NATIJA:\n")
        self.result_text.insert(tk.END, f"  Jami kirim: {total_income:,.0f} so'm\n")
        self.result_text.insert(tk.END, f"  Jami chiqim: {total_expenses:,.0f} so'm\n")
        self.result_text.insert(tk.END, f"  Sof foyda: {net_profit:,.0f} so'm\n")
        
        # Holat rang bilan
        if net_profit > 0:
            self.result_text.insert(tk.END, "✅ FOYDA", 'profit')
            self.result_text.tag_config('profit', foreground=Config.COLORS['success'], 
                                       font=('Arial', 11, 'bold'))
        else:
            self.result_text.insert(tk.END, "❌ ZARAR", 'loss')
            self.result_text.tag_config('loss', foreground=Config.COLORS['danger'], 
                                       font=('Arial', 11, 'bold'))
        
        self.result_text.see(1.0)
    
    def brak_report(self):
        """Brak tahlili"""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, 
            f"⚠️  BRAK TAHLILI: {start_date} - {end_date}\n")
        self.result_text.insert(tk.END, "="*50 + "\n\n")
        
        # Non yasashda brak
        self.result_text.insert(tk.END, "🍞 NON YASASHDA BRAK:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   brak_sababi,
                   COUNT(*) as count,
                   SUM(brak_non) as total_brak,
                   AVG(brak_non) as avg_brak
               FROM non_yasash 
               WHERE sana BETWEEN ? AND ? AND brak_non > 0
               GROUP BY brak_sababi
               ORDER BY total_brak DESC""",
            (start_date, end_date)
        )
        
        for row in results:
            self.result_text.insert(tk.END, 
                f"  {row[0]}: {row[1]} marta, {row[2]} dona (o'rtacha: {row[3]:.1f})\n")
        
        self.result_text.insert(tk.END, "\n")
        
        # Tandirda brak
        self.result_text.insert(tk.END, "🔥 TANDIRDA BRAK:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   t.tandir_raqami,
                   x.ism,
                   COUNT(*) as count,
                   SUM(t.brak_non) as total_brak,
                   AVG(t.samaradorlik) as avg_samara
               FROM tandir t
               LEFT JOIN xodimlar x ON t.tandirchi_id = x.id
               WHERE t.sana BETWEEN ? AND ? AND t.brak_non > 0
               GROUP BY t.tandir_raqami, x.ism
               ORDER BY total_brak DESC""",
            (start_date, end_date)
        )
        
        for row in results:
            self.result_text.insert(tk.END, 
                f"  Tandir {row[0]} ({row[1]}): {row[2]} marta, {row[3]} dona (samara: {row[4]:.1f}%)\n")
        
        self.result_text.see(1.0)
    
    def production_report(self):
        """Ishlab chiqarish hisoboti"""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, 
            f"🏭 ISHLAB CHIQARISH HISOBOTI: {start_date} - {end_date}\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        
        # Xamir tayyorlash
        self.result_text.insert(tk.END, "🥖 XAMIR TAYYORLASH:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   x.ism,
                   COUNT(*) as count,
                   SUM(xm.xamir_soni) as total,
                   AVG(xm.samaradorlik) as avg_samara,
                   SUM(xm.kechikish_minut) as total_late
               FROM xamir xm
               LEFT JOIN xodimlar x ON xm.xodim_id = x.id
               WHERE xm.sana BETWEEN ? AND ?
               GROUP BY x.ism
               ORDER BY total DESC""",
            (start_date, end_date)
        )
        
        for row in results:
            self.result_text.insert(tk.END, 
                f"  {row[0]}: {row[1]} marta, {row[2]} dona, samara: {row[3]:.1f}%")
            if row[4] > 0:
                self.result_text.insert(tk.END, f", kechikish: {row[4]} daqiqa")
            self.result_text.insert(tk.END, "\n")
        
        self.result_text.insert(tk.END, "\n")
        
        # Non yasash
        self.result_text.insert(tk.END, "🍞 NON YASASH:\n")
        
        results = self.db.fetchall(
            """SELECT 
                   x.ism,
                   COUNT(*) as count,
                   SUM(ny.chiqqan_non) as total_produced,
                   SUM(ny.brak_non) as total_brak,
                   AVG(ny.ortacha_unumdorlik) as avg_productivity
               FROM non_yasash ny
               LEFT JOIN xodimlar x ON ny.xodim_id = x.id
               WHERE ny.sana BETWEEN ? AND ?
               GROUP BY x.ism
               ORDER BY total_produced DESC""",
            (start_date, end_date)
        )
        
        for row in results:
            brak_percent = (row[3] / row[2] * 100) if row[2] > 0 else 0
            self.result_text.insert(tk.END, 
                f"  {row[0]}: {row[1]} marta, {row[2]} dona, brak: {brak_percent:.1f}%, unumdorlik: {row[4]:.1f}%\n")
        
        self.result_text.see(1.0)
    
    def workers_report(self):
        """Xodimlar hisoboti"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "👥 XODIMLAR HISOBOTI\n")
        self.result_text.insert(tk.END, "="*40 + "\n\n")
        
        # Barcha xodimlar
        results = self.db.fetchall(
            """SELECT 
                   ism,
                   lavozim,
                   oylik_maosh,
                   bonus,
                   jarima,
                   reyting,
                   status
               FROM xodimlar 
               ORDER BY lavozim, reyting DESC"""
        )
        
        for row in results:
            status_icon = "✅" if row[6] == 'faol' else "⛔"
            reyting_color = "🟢" if row[5] >= 90 else "🟡" if row[5] >= 70 else "🔴"
            
            self.result_text.insert(tk.END, 
                f"{status_icon} {row[0]} ({row[1]})\n")
            self.result_text.insert(tk.END, 
                f"  Maosh: {row[2]:,.0f} so'm, Bonus: {row[3]:,.0f} so'm, Jarima: {row[4]:,.0f} so'm\n")
            self.result_text.insert(tk.END, 
                f"  Reyting: {reyting_color} {row[5]:.1f}%\n\n")
        
        self.result_text.see(1.0)
    
    def debt_report(self):
        """Qarzdorlik hisoboti"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "📉 QARZDORLIK HISOBOTI\n")
        self.result_text.insert(tk.END, "="*40 + "\n\n")
        
        # Qarzdor mijozlar
        results = self.db.fetchall(
            """SELECT 
                   nomi,
                   telefon,
                   jami_qarz,
                   kredit_limit,
                   oxirgi_sana
               FROM mijozlar 
               WHERE jami_qarz > 0
               ORDER BY jami_qarz DESC"""
        )
        
        total_debt = 0
        for row in results:
            debt_percent = (row[2] / row[3] * 100) if row[3] > 0 else 100
            status = "🟢" if debt_percent < 50 else "🟡" if debt_percent < 80 else "🔴"
            
            self.result_text.insert(tk.END, 
                f"{status} {row[0]} ({row[1]})\n")
            self.result_text.insert(tk.END, 
                f"  Qarz: {row[2]:,.0f} so'm, Limit: {row[3]:,.0f} so'm ({debt_percent:.0f}%)\n")
            self.result_text.insert(tk.END, 
                f"  Oxirgi sotuv: {row[4] or 'yoq'}\n\n")
            
            total_debt += row[2]
        
        self.result_text.insert(tk.END, 
            f"💰 JAMI QARZ: {total_debt:,.0f} so'm\n")
        
        self.result_text.see(1.0)
    
    def yearly_report(self):
        """Yillik hisobot"""
        year = date.today().year
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"📊 YILLIK HISOBOT: {year}\n")
        self.result_text.insert(tk.END, "="*50 + "\n\n")
        
        # Oylik statistika
        self.result_text.insert(tk.END, "📈 OYLIK STATISTIKA:\n")
        
        for month in range(1, 13):
            month_str = f"{year}-{month:02d}"
            
            # Sotuvlar
            result = self.db.fetchone(
                "SELECT SUM(jami_summa) FROM sotuvlar WHERE strftime('%Y-%m', sana) = ?",
                (month_str,)
            )
            sales = result[0] if result and result[0] else 0
            
            # Xarajatlar
            result = self.db.fetchone(
                "SELECT SUM(jami_summa) FROM xarajatlar WHERE strftime('%Y-%m', sana) = ?",
                (month_str,)
            )
            expenses = result[0] if result and result[0] else 0
            
            profit = sales - expenses
            
            self.result_text.insert(tk.END, 
                f"  {month:02d}/{year}: Sotuv: {sales:,.0f} so'm, Xarajat: {expenses:,.0f} so'm, Foyda: {profit:,.0f} so'm\n")
        
        self.result_text.see(1.0)
    
    def export_excel(self):
        """Excel ga eksport qilish"""
        # Bu funksiya to'liq amalga oshirilishi uchun pandas kutubxonasi kerak
        messagebox.showinfo("Eksport", 
            "Excel eksport qilish funktsiyasi. Pandas kutubxonasi o'rnatilgan bo'lsa ishlaydi.")
    
    def print_report(self):
        """Chop etish"""
        content = self.result_text.get(1.0, tk.END)
        if len(content.strip()) < 10:
            messagebox.showwarning("Ogohlantirish", "Chop etish uchun hisobot yarating!")
            return
        
        # Faylga saqlash
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Muvaffaqiyat", f"Hisobot {filename} fayliga saqlandi!")
            except Exception as e:
                messagebox.showerror("Xatolik", f"Faylga yozishda xatolik: {e}")
    
    def clear_results(self):
        """Natijalarni tozalash"""
        self.result_text.delete(1.0, tk.END)

# ==================== ASOSIY DASTUR ====================
class NonSexApp:
    """Asosiy dastur"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{Config.COMPANY_NAME} v{Config.VERSION}")
        self.root.geometry(Config.WINDOW_SIZE)
        self.root.configure(bg=Config.COLORS['background'])
        
        # Database
        self.db = Database()
        
        # Stil konfiguratsiyasi
        self.setup_styles()
        
        # Login oynasi
        self.show_login()
        
    def setup_styles(self):
        """Tkinter stillarini sozlash"""
        style = ttk.Style()
        
        # Asosiy stillar
        style.theme_use('clam')
        
        # Tugma stillari
        style.configure('Accent.TButton', 
                       background=Config.COLORS['info'],
                       foreground='white',
                       font=Config.FONTS['normal'],
                       padding=10)
        
        style.configure('Success.TButton',
                       background=Config.COLORS['success'],
                       foreground='white')
        
        style.configure('Danger.TButton',
                       background=Config.COLORS['danger'],
                       foreground='white')
        
        # Treeview stillari
        style.configure('Treeview',
                       background=Config.COLORS['white'],
                       foreground=Config.COLORS['text'],
                       fieldbackground=Config.COLORS['white'])
        
        style.configure('Treeview.Heading',
                       background=Config.COLORS['primary'],
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        # LabelFrame stillari
        style.configure('TLabelframe',
                       background=Config.COLORS['background'],
                       foreground=Config.COLORS['primary'])
        
        style.configure('TLabelframe.Label',
                       background=Config.COLORS['background'],
                       foreground=Config.COLORS['primary'],
                       font=Config.FONTS['heading'])
    
    def show_login(self):
        """Login oynasini ko'rsatish"""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Tizimga Kirish")
        self.login_window.geometry("400x300")
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        self.login_window.configure(bg=Config.COLORS['background'])
        
        # Markazlashtirish
        frame = ttk.Frame(self.login_window, padding=30)
        frame.pack(expand=True)
        
        ttk.Label(frame, text="🔐 TIZIMGA KIRISH", 
                 font=Config.FONTS['title']).pack(pady=20)
        
        ttk.Label(frame, text="Login:").pack(pady=5)
        self.login_entry = ttk.Entry(frame, width=25)
        self.login_entry.pack(pady=5)
        self.login_entry.insert(0, "Admin")
        
        ttk.Label(frame, text="Parol:").pack(pady=5)
        self.password_entry = ttk.Entry(frame, width=25, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Admin")
        
        ttk.Button(frame, text="Kirish", 
                  command=self.check_login,
                  style="Accent.TButton",
                  width=15).pack(pady=20)
        
        # Test login
        ttk.Button(frame, text="Test (Operator)", 
                  command=lambda: self.set_test_login("operator"),
                  width=15).pack(pady=5)
    
    def set_test_login(self, role: str):
        """Test login"""
        self.login_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        
        if role == "operator":
            self.login_entry.insert(0, "operator")
            self.password_entry.insert(0, "operator123")
    
    def check_login(self):
        """Login tekshirish"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        result = self.db.fetchone(
            "SELECT rol, ism FROM foydalanuvchilar WHERE login = ? AND parol = ? AND status = 'active'",
            (login, password)
        )
        
        if result:
            self.user_role = result[0]
            self.user_name = result[1]
            self.login_window.destroy()
            self.setup_main_window()
        else:
            messagebox.showerror("Xatolik", "Noto'g'ri login yoki parol!")
    
    def setup_main_window(self):
        """Asosiy oynani yaratish"""
        # Sarlavha
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            title_frame,
            text=f"🏭 {Config.COMPANY_NAME}",
            font=('Arial', 20, 'bold'),
            foreground=Config.COLORS['primary']
        ).pack(side=tk.LEFT)
        
        user_info = ttk.Frame(title_frame)
        user_info.pack(side=tk.RIGHT)
        
        ttk.Label(
            user_info,
            text=f"👤 {self.user_name} ({self.user_role})",
            font=Config.FONTS['small']
        ).pack(side=tk.RIGHT)
        
        ttk.Label(
            user_info,
            text=f"📅 {Config.get_date()}",
            font=Config.FONTS['small']
        ).pack(side=tk.RIGHT, padx=10)
        
        # Asosiy menyu
        self.setup_main_menu()
        
        # Dashbord
        self.show_dashboard()
        
        # Chiqish tugmasi
        exit_frame = ttk.Frame(self.root)
        exit_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        ttk.Button(
            exit_frame,
            text="🚪 Chiqish",
            command=self.root.quit,
            style="Danger.TButton"
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            exit_frame,
            text="🔄 Yangilash",
            command=self.refresh_all
        ).pack(side=tk.RIGHT, padx=10)
    
    def setup_main_menu(self):
        """Asosiy menyuni yaratish"""
        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        menu_items = [
            ("📊 Dashbord", self.show_dashboard),
            ("🥖 Xamir", self.show_xamir),
            ("🍞 Non yasash", self.show_non_yasash),
            ("🔥 Tandir", self.show_tandir),
            ("🏪 Mijozlar", self.show_mijozlar),
            ("💰 Sotuv", self.show_sotuv),
            ("💸 Xarajatlar", self.show_xarajatlar),
            ("💰 Kassa", self.show_kassa),
            ("👥 Xodimlar", self.show_xodimlar),
            ("📊 Hisobotlar", self.show_hisobotlar)
        ]
        
        for text, command in menu_items:
            btn = ttk.Button(
                menu_frame,
                text=text,
                command=command,
                width=15
            )
            btn.pack(side=tk.LEFT, padx=2)
    
    def clear_main_frame(self):
        """Asosiy freymni tozalash"""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame) and widget not in [
                self.root.winfo_children()[0],  # title_frame
                self.root.winfo_children()[1],  # menu_frame
                self.root.winfo_children()[-1]  # exit_frame
            ]:
                widget.destroy()
    
    def show_dashboard(self):
        """Dashbordni ko'rsatish"""
        self.clear_main_frame()
        self.dashboard = Dashboard(self.root, self.db)
    
    def show_xamir(self):
        """Xamir modulini ko'rsatish"""
        self.clear_main_frame()
        self.xamir_module = XamirTayyorlash(self.root, self.db)
    
    def show_non_yasash(self):
        """Non yasash modulini ko'rsatish"""
        self.clear_main_frame()
        self.non_yasash_module = NonYasash(self.root, self.db)
    
    def show_tandir(self):
        """Tandir modulini ko'rsatish"""
        self.clear_main_frame()
        self.tandir_module = TandirModule(self.root, self.db)
    
    def show_mijozlar(self):
        """Mijozlar modulini ko'rsatish"""
        self.clear_main_frame()
        self.mijozlar_module = MijozlarModule(self.root, self.db)
    
    def show_sotuv(self):
        """Sotuv modulini ko'rsatish"""
        self.clear_main_frame()
        self.sotuv_module = SotuvModule(self.root, self.db)
    
    def show_xarajatlar(self):
        """Xarajatlar modulini ko'rsatish"""
        self.clear_main_frame()
        self.xarajatlar_module = XarajatlarModule(self.root, self.db)
    
    def show_kassa(self):
        """Kassa modulini ko'rsatish"""
        self.clear_main_frame()
        self.kassa_module = KassaModule(self.root, self.db)
    
    def show_xodimlar(self):
        """Xodimlar modulini ko'rsatish"""
        self.clear_main_frame()
        self.xodimlar_module = XodimlarModule(self.root, self.db)
    
    def show_hisobotlar(self):
        """Hisobotlar modulini ko'rsatish"""
        self.clear_main_frame()
        self.hisobotlar_module = HisobotlarModule(self.root, self.db)
    
    def refresh_all(self):
        """Hamma ma'lumotlarni yangilash"""
        current_module = None
        
        # Joriy modulni aniqlash
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                if hasattr(widget, 'load_data'):
                    current_module = widget
                    break
        
        if current_module and hasattr(current_module, 'load_data'):
            current_module.load_data()
            messagebox.showinfo("Yangilash", "Ma'lumotlar yangilandi!")
        else:
            self.show_dashboard()
    
    def run(self):
        """Dasturni ishga tushirish"""
        self.root.mainloop()

# ==================== DASTURNI ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    print("🚀 Non Sex Boshqaruv Tizimi yuklanmoqda...")
    print(f"📊 Versiya: {Config.VERSION}")
    print(f"💾 Ma'lumotlar bazasi: {Config.DB_NAME}")
    
    app = NonSexApp()
    app.run()