#!/usr/bin/env python3
"""نظام إدارة محل الحلاقة الرجالية - تطبيق مكتبي كامل"""

import json
import math
import os
import shutil
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkcalendar import DateEntry
except Exception:  # pragma: no cover - مكتبة اختيارية ولكن مهمة للتواريخ
    DateEntry = None


COLORS: Dict[str, str] = {
    "primary": "#1a3a52",
    "secondary": "#2d5270",
    "accent": "#d4af37",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "background": "#f5f5f5",
    "card": "#ffffff",
    "sidebar": "#1a3a52",
    "text_dark": "#2c3e50",
    "text_light": "#ecf0f1",
    "text_muted": "#6c757d",
    "pending": "#f59e0b",
    "confirmed": "#3b82f6",
    "completed": "#10b981",
    "cancelled": "#ef4444",
    "no_show": "#94a3b8",
}

FONTS: Dict[str, Tuple[str, int]] = {
    "family": ("Segoe UI", 11),
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 11),
    "button": ("Segoe UI", 11, "bold"),
    "small": ("Segoe UI", 9),
}

def format_currency(value: float) -> str:
    try:
        return f"{value:,.2f} ر.س".replace(",", "٬")
    except Exception:
        return f"{value} ر.س"

def arabic_message(title: str, message: str, kind: str = "info") -> None:
    if kind == "error":
        messagebox.showerror(title, message)
    elif kind == "warning":
        messagebox.showwarning(title, message)
    else:
        messagebox.showinfo(title, message)


class DatabaseManager:
    """مدير قاعدة البيانات لتسهيل التعامل مع SQLite."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query: str, params: Tuple = (), commit: bool = True) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()

    def fetchall(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()



class BarbershopManagementSystem:
    # الكلاس الرئيسي للنظام
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.db_path = 'database/barbershop.db'
        self.db = DatabaseManager(self.db_path)
        self.settings_cache: Dict[str, str] = {}
        self.current_editing_appointment: Optional[int] = None
        self.current_selected_appointment: Optional[int] = None

        self.create_folders()
        self.setup_window()
        self.setup_database()
        self.load_default_data()
        self.load_settings_cache()
        self.create_main_interface()
        self.update_dashboard()
        self.load_appointments()
        self.setup_keyboard_shortcuts()

    def create_folders(self) -> None:
        folders = ['database', 'backups', 'exports', 'assets']
        for folder in folders:
            Path(folder).mkdir(exist_ok=True)

    def setup_window(self) -> None:
        self.root.title('💈 نظام إدارة محل الحلاقة')
        window_width = 1450
        window_height = 880
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        self.root.configure(bg=COLORS['background'])
        try:
            self.root.iconbitmap('assets/icon.ico')
        except Exception:
            pass

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TLabel', font=FONTS['body'], background=COLORS['background'], foreground=COLORS['text_dark'])
        style.configure('Card.TFrame', background=COLORS['card'])
        style.configure('Card.TLabelframe', background=COLORS['card'], foreground=COLORS['text_dark'], font=FONTS['subtitle'])
        style.configure('Card.TLabelframe.Label', background=COLORS['card'], foreground=COLORS['primary'], font=FONTS['subtitle'])
        style.configure('Accent.TButton', font=FONTS['button'], background=COLORS['accent'], foreground=COLORS['text_dark'])
        style.map('Accent.TButton', background=[('active', COLORS['secondary'])], foreground=[('active', COLORS['text_light'])])
        style.configure('Danger.TButton', font=FONTS['button'], background=COLORS['danger'], foreground=COLORS['text_light'])
        style.map('Danger.TButton', background=[('active', '#b91c1c')])
        style.configure('Success.TButton', font=FONTS['button'], background=COLORS['success'], foreground=COLORS['text_light'])
        style.map('Success.TButton', background=[('active', '#059669')])
        style.configure('Primary.TButton', font=FONTS['button'], background=COLORS['primary'], foreground=COLORS['text_light'])
        style.map('Primary.TButton', background=[('active', COLORS['secondary'])])
        style.configure('Secondary.TButton', font=FONTS['button'], background=COLORS['secondary'], foreground=COLORS['text_light'])
        style.map('Secondary.TButton', background=[('active', COLORS['primary'])])
        style.configure('Treeview', font=FONTS['body'], background=COLORS['card'], fieldbackground=COLORS['card'], rowheight=28)
        style.configure('Treeview.Heading', font=FONTS['body'], background=COLORS['primary'], foreground=COLORS['text_light'])

    def setup_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                birth_date DATE,
                address TEXT,
                preferences TEXT,
                loyalty_points INTEGER DEFAULT 0,
                total_visits INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_visit DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                hire_date DATE,
                specialization TEXT,
                commission_rate REAL DEFAULT 30,
                status TEXT DEFAULT 'active',
                working_days TEXT,
                working_hours TEXT,
                total_services INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0,
                rating REAL DEFAULT 5.0,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                duration INTEGER NOT NULL,
                price REAL NOT NULL,
                cost REAL DEFAULT 0,
                commission_rate REAL,
                status TEXT DEFAULT 'active',
                popularity INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                barber_id INTEGER NOT NULL,
                barber_name TEXT NOT NULL,
                service_id INTEGER NOT NULL,
                service_name TEXT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                duration INTEGER,
                status TEXT DEFAULT 'pending',
                price REAL NOT NULL,
                cost REAL DEFAULT 0,
                commission REAL DEFAULT 0,
                payment_method TEXT,
                payment_status TEXT DEFAULT 'unpaid',
                rating INTEGER,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (barber_id) REFERENCES barbers(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                customer_name TEXT NOT NULL,
                barber_id INTEGER NOT NULL,
                barber_name TEXT NOT NULL,
                services TEXT NOT NULL,
                total_price REAL NOT NULL,
                total_cost REAL DEFAULT 0,
                total_commission REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                final_price REAL NOT NULL,
                payment_method TEXT NOT NULL,
                payment_status TEXT DEFAULT 'paid',
                loyalty_points_earned INTEGER DEFAULT 0,
                loyalty_points_used INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed',
                check_in_time DATETIME,
                check_out_time DATETIME,
                duration INTEGER,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (barber_id) REFERENCES barbers(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def load_default_data(self) -> None:
        services = [
            ('قص شعر عادي', 'قص شعر', 'قص شعر كلاسيكي بسيط', 30, 40, 5, 30, 'active'),
            ('قص شعر + تشكيل', 'قص شعر', 'قص شعر مع تشكيل الشعر', 40, 50, 6, 30, 'active'),
            ('قص شعر للأطفال', 'قص شعر', 'قص شعر للأطفال تحت 12 سنة', 25, 30, 4, 30, 'active'),
            ('قص شعر كلاسيكي', 'قص شعر', 'قص شعر بأسلوب كلاسيكي', 35, 45, 5, 30, 'active'),
            ('قص شعر حديث (Fade)', 'قص شعر', 'قص شعر حديث مع تدرج', 45, 60, 8, 35, 'active'),
            ('حلاقة ذقن عادية', 'حلاقة ذقن', 'حلاقة الذقن بشكل عادي', 20, 30, 3, 30, 'active'),
            ('حلاقة ذقن + تشذيب', 'حلاقة ذقن', 'حلاقة وتشذيب الذقن', 30, 40, 5, 30, 'active'),
            ('تشذيب الذقن فقط', 'حلاقة ذقن', 'تشذيب وتنظيف الذقن', 15, 25, 3, 30, 'active'),
            ('حلاقة ملكية', 'حلاقة ذقن', 'حلاقة فاخرة مع منشفة ساخنة', 40, 70, 10, 35, 'active'),
            ('صبغة شعر كاملة', 'صبغة', 'صبغة الشعر بالكامل', 90, 150, 40, 30, 'active'),
            ('صبغة شعر جزئية', 'صبغة', 'صبغة جزء من الشعر', 60, 100, 25, 30, 'active'),
            ('صبغة ذقن', 'صبغة', 'صبغة شعر الذقن', 45, 80, 20, 30, 'active'),
            ('إزالة الشيب', 'صبغة', 'إخفاء الشعر الأبيض', 75, 120, 30, 30, 'active'),
            ('باكج VIP', 'باكجات', 'قص شعر + حلاقة + تدليك', 90, 120, 20, 35, 'active'),
            ('باكج العريس', 'باكجات', 'باكج كامل للعريس', 120, 200, 40, 35, 'active'),
            ('باكج تجديد كامل', 'باكجات', 'قص + حلاقة + صبغة', 100, 180, 35, 35, 'active'),
            ('غسيل الشعر', 'إضافية', 'غسيل وتنظيف الشعر', 10, 15, 2, 30, 'active'),
            ('تدليك الرأس', 'إضافية', 'تدليك فروة الرأس', 15, 25, 3, 30, 'active'),
            ('ماسك للشعر', 'إضافية', 'ماسك معالج للشعر', 20, 40, 8, 30, 'active'),
            ('تنظيف البشرة', 'إضافية', 'تنظيف عميق للبشرة', 30, 60, 10, 30, 'active'),
            ('تشقير الحواجب', 'إضافية', 'تشقير وتنظيف الحواجب', 20, 35, 5, 30, 'active'),
            ('حمام مغربي', 'إضافية', 'جلسة حمام مغربي', 60, 100, 20, 30, 'active'),
        ]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM services')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO services (name, category, description, duration, price, cost, commission_rate, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', services)
            cursor.execute('SELECT COUNT(*) FROM barbers')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO barbers (name, phone, specialization, commission_rate, status, working_days, working_hours)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'خالد محمد', '0501234567', 'قص شعر حديث', 35, 'active',
                    'السبت,الأحد,الاثنين,الثلاثاء,الأربعاء,الخميس', '09:00-18:00'
                ))
            default_settings = [
                ('shop_name', 'محل الحلاقة'),
                ('shop_address', 'الرياض، المملكة العربية السعودية'),
                ('shop_phone', '0501234567'),
                ('shop_email', 'info@barbershop.com'),
                ('working_hours', '09:00-21:00'),
                ('tax_rate', '15'),
            ]
            for key, value in default_settings:
                cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
            conn.commit()

    def load_settings_cache(self) -> None:
        rows = self.db.fetchall('SELECT key, value FROM settings')
        self.settings_cache = {row['key']: row['value'] for row in rows}

    def create_main_interface(self) -> None:
        self.main_container = ttk.Frame(self.root, padding=20, style='Card.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.create_dashboard_bar()
        self.create_booking_form()
        self.create_appointments_table()
        self.create_action_buttons()


    def create_dashboard_bar(self) -> None:
        bar_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        bar_frame.pack(fill=tk.X, pady=(0, 15))
        stats = [
            ('👥', 'عملاء اليوم', '0'),
            ('📅', 'مواعيد اليوم', '0'),
            ('✂️', 'جلسات منتهية', '0'),
            ('💰', 'إيرادات اليوم', '0'),
            ('💵', 'صافي الربح', '0'),
            ('⭐', 'متوسط التقييم', '0'),
        ]
        self.stats_labels: Dict[str, ttk.Label] = {}
        for icon, label, value in stats:
            card = ttk.Frame(bar_frame, style='Card.TFrame')
            card.pack(side=tk.RIGHT, padx=8, fill=tk.Y)
            ttk.Label(card, text=f"{icon} {label}", font=FONTS['body']).pack(anchor='e')
            value_label = ttk.Label(card, text=value, font=FONTS['subtitle'], foreground=COLORS['primary'])
            value_label.pack(anchor='e')
            self.stats_labels[label] = value_label

    def create_booking_form(self) -> None:
        form_frame = ttk.Labelframe(self.main_container, text='📋 حجز موعد جديد / جلسة سريعة', style='Card.TLabelframe', padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        self.customer_name_var = tk.StringVar()
        self.customer_phone_var = tk.StringVar()
        self.customer_email_var = tk.StringVar()
        self.barber_var = tk.StringVar()
        self.service_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.price_var = tk.DoubleVar()
        self.payment_method_var = tk.StringVar(value='نقدي')
        self.notes_var = tk.StringVar()
        self.payment_status_var = tk.StringVar(value='unpaid')

        ttk.Label(form_frame, text='👤 اسم العميل:').grid(row=0, column=4, sticky='e', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_name_var, width=30, justify='right').grid(row=0, column=3, sticky='e', padx=5, pady=5)
        ttk.Label(form_frame, text='📱 الجوال:').grid(row=0, column=2, sticky='e', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_phone_var, width=20, justify='right').grid(row=0, column=1, sticky='e', padx=5, pady=5)
        ttk.Button(form_frame, text='🔍 بحث', style='Secondary.TButton', command=self.search_customer_dialog).grid(row=0, column=0, padx=5, pady=5)

        ttk.Label(form_frame, text='✂️ الحلاق:').grid(row=1, column=4, sticky='e', padx=5, pady=5)
        self.barber_combo = ttk.Combobox(form_frame, textvariable=self.barber_var, state='readonly', width=28, justify='right')
        self.barber_combo.grid(row=1, column=3, sticky='e', padx=5, pady=5)
        ttk.Label(form_frame, text='💈 الخدمة:').grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.service_combo = ttk.Combobox(form_frame, textvariable=self.service_var, state='readonly', width=28, justify='right')
        self.service_combo.grid(row=1, column=1, sticky='e', padx=5, pady=5)
        self.service_combo.bind('<<ComboboxSelected>>', lambda _: self.update_price_from_service())

        ttk.Label(form_frame, text='📅 التاريخ:').grid(row=2, column=4, sticky='e', padx=5, pady=5)
        if DateEntry:
            self.date_entry = DateEntry(form_frame, textvariable=self.date_var, width=18, date_pattern='yyyy-mm-dd')
            self.date_entry.set_date(date.today())
        else:
            self.date_entry = ttk.Entry(form_frame, textvariable=self.date_var, width=20, justify='right')
            self.date_var.set(date.today().isoformat())
        self.date_entry.grid(row=2, column=3, sticky='e', padx=5, pady=5)

        ttk.Label(form_frame, text='🕐 الوقت:').grid(row=2, column=2, sticky='e', padx=5, pady=5)
        self.time_combo = ttk.Combobox(form_frame, textvariable=self.time_var, state='readonly', width=20, justify='right')
        self.time_combo['values'] = self.generate_time_slots()
        self.time_combo.grid(row=2, column=1, sticky='e', padx=5, pady=5)

        ttk.Label(form_frame, text='💰 السعر:').grid(row=3, column=4, sticky='e', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.price_var, width=20, justify='right').grid(row=3, column=3, sticky='e', padx=5, pady=5)
        ttk.Label(form_frame, text='💳 طريقة الدفع:').grid(row=3, column=2, sticky='e', padx=5, pady=5)
        self.payment_combo = ttk.Combobox(form_frame, textvariable=self.payment_method_var, state='readonly', width=18, justify='right')
        self.payment_combo['values'] = ('نقدي', 'بطاقة', 'تحويل بنكي')
        self.payment_combo.grid(row=3, column=1, sticky='e', padx=5, pady=5)

        ttk.Label(form_frame, text='📝 ملاحظات:').grid(row=4, column=4, sticky='ne', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.notes_var, width=70, justify='right').grid(row=4, column=0, columnspan=4, sticky='we', padx=5, pady=5)

        button_frame = ttk.Frame(form_frame, style='Card.TFrame')
        button_frame.grid(row=5, column=0, columnspan=5, sticky='we', pady=(10, 0))
        ttk.Button(button_frame, text='💾 حفظ الموعد', style='Success.TButton', command=self.save_appointment).pack(side=tk.RIGHT, padx=6)
        ttk.Button(button_frame, text='⚡ جلسة فورية', style='Primary.TButton', command=self.open_walk_in_session).pack(side=tk.RIGHT, padx=6)
        ttk.Button(button_frame, text='🗑️ مسح الحقول', style='Danger.TButton', command=self.clear_booking_form).pack(side=tk.RIGHT, padx=6)

        self.refresh_barber_service_lists()

    def generate_time_slots(self) -> List[str]:
        slots: List[str] = []
        start_time = datetime.strptime('09:00', '%H:%M')
        end_time = datetime.strptime('22:00', '%H:%M')
        while start_time <= end_time:
            slots.append(start_time.strftime('%H:%M'))
            start_time += timedelta(minutes=15)
        return slots

    def create_appointments_table(self) -> None:
        container = ttk.Frame(self.main_container, style='Card.TFrame')
        container.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(container, style='Card.TFrame')
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text='📅 جدول مواعيد اليوم', font=FONTS['subtitle']).pack(side=tk.RIGHT, padx=5)

        filter_frame = ttk.Frame(header_frame, style='Card.TFrame')
        filter_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text='🔎 بحث:').pack(side=tk.LEFT, padx=3)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind('<Return>', lambda _: self.load_appointments())

        ttk.Label(filter_frame, text='📆 التاريخ:').pack(side=tk.LEFT, padx=5)
        self.appointment_date_var = tk.StringVar()
        if DateEntry:
            self.appointment_date_entry = DateEntry(filter_frame, textvariable=self.appointment_date_var, width=12, date_pattern='yyyy-mm-dd')
            self.appointment_date_entry.set_date(date.today())
        else:
            self.appointment_date_entry = ttk.Entry(filter_frame, textvariable=self.appointment_date_var, width=12)
            self.appointment_date_var.set(date.today().isoformat())
        self.appointment_date_entry.pack(side=tk.LEFT, padx=3)
        ttk.Button(filter_frame, text='تحديث', style='Secondary.TButton', command=self.load_appointments).pack(side=tk.LEFT, padx=5)

        columns = ('number', 'time', 'customer', 'phone', 'barber', 'service', 'price', 'status')
        self.appointments_tree = ttk.Treeview(container, columns=columns, show='headings', selectmode='browse')
        headings = ['رقم الموعد', 'الوقت', 'العميل', 'الجوال', 'الحلاق', 'الخدمة', 'السعر', 'الحالة']
        widths = [140, 80, 180, 120, 140, 180, 100, 120]
        for col, title, width in zip(columns, headings, widths):
            self.appointments_tree.heading(col, text=title)
            self.appointments_tree.column(col, anchor='e', width=width)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.appointments_tree.yview)
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.appointments_tree.pack(fill=tk.BOTH, expand=True, padx=(0, 5), pady=10)
        self.appointments_tree.bind('<Double-1>', self.populate_form_from_selection)
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)

    def create_action_buttons(self) -> None:
        actions_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        buttons = [
            ('📅 جدول المواعيد', self.load_appointments),
            ('👥 العملاء', self.open_customers_window),
            ('✂️ الحلاقين', self.open_barbers_window),
            ('💈 الخدمات', self.open_services_window),
            ('📊 التقارير اليومية', self.show_daily_report),
            ('📆 التقارير الشهرية', self.show_monthly_report),
            ('💾 نسخ احتياطي', self.backup_database),
            ('📤 تصدير المواعيد', self.export_to_excel),
            ('⚙️ الإعدادات', self.open_settings_window),
        ]
        for text, command in buttons:
            ttk.Button(actions_frame, text=text, style='Primary.TButton', command=command).pack(side=tk.RIGHT, padx=6)

    def refresh_barber_service_lists(self) -> None:
        barbers = self.db.fetchall("SELECT id, name FROM barbers WHERE status='active' ORDER BY name")
        barber_values = [f"{row['id']} - {row['name']}" for row in barbers]
        self.barber_combo['values'] = barber_values
        if barber_values:
            self.barber_combo.current(0)

        services = self.db.fetchall("SELECT id, name FROM services WHERE status='active' ORDER BY category, name")
        service_values = [f"{row['id']} - {row['name']}" for row in services]
        self.service_combo['values'] = service_values
        if service_values:
            self.service_combo.current(0)
            self.update_price_from_service()


    def update_dashboard(self) -> None:
        today = date.today().isoformat()
        appointments = self.db.fetchone(
            "SELECT COUNT(*) AS count, SUM(price) AS revenue FROM appointments WHERE appointment_date=?",
            (today,)
        )
        sessions = self.db.fetchone(
            "SELECT COUNT(*) AS count, SUM(final_price) AS revenue FROM sessions WHERE DATE(created_at)=?",
            (today,)
        )
        unique_customers = self.db.fetchone(
            "SELECT COUNT(DISTINCT customer_id) AS customers FROM sessions WHERE DATE(created_at)=?",
            (today,)
        )
        profit_data = self.db.fetchone(
            "SELECT SUM(total_price - total_cost - total_commission) AS profit FROM sessions WHERE DATE(created_at)=?",
            (today,)
        )
        rating_data = self.db.fetchone(
            "SELECT AVG(rating) AS rating FROM appointments WHERE appointment_date=? AND rating IS NOT NULL",
            (today,)
        )
        self.stats_labels['عملاء اليوم'].config(text=str(unique_customers['customers'] or 0))
        self.stats_labels['مواعيد اليوم'].config(text=str(appointments['count'] or 0))
        self.stats_labels['جلسات منتهية'].config(text=str(sessions['count'] or 0))
        self.stats_labels['إيرادات اليوم'].config(text=format_currency(sessions['revenue'] or 0))
        self.stats_labels['صافي الربح'].config(text=format_currency(profit_data['profit'] or 0))
        rating = rating_data['rating'] or 0
        self.stats_labels['متوسط التقييم'].config(text=f"{rating:.1f}")

    def clear_booking_form(self) -> None:
        self.customer_name_var.set('')
        self.customer_phone_var.set('')
        self.customer_email_var.set('')
        self.notes_var.set('')
        self.price_var.set(0)
        if DateEntry:
            self.date_entry.set_date(date.today())
        else:
            self.date_var.set(date.today().isoformat())
        self.time_combo.set('')
        self.payment_combo.set('نقدي')
        self.payment_status_var.set('unpaid')
        self.current_editing_appointment = None
        self.appointments_tree.selection_remove(self.appointments_tree.selection())

    def update_price_from_service(self) -> None:
        value = self.service_var.get()
        if not value:
            return
        try:
            service_id = int(value.split('-')[0].strip())
        except (ValueError, IndexError):
            return
        service = self.db.fetchone("SELECT price FROM services WHERE id=?", (service_id,))
        if service:
            self.price_var.set(service['price'])

    def populate_form_from_selection(self, _event: Optional[tk.Event] = None) -> None:
        item = self.appointments_tree.focus()
        if not item:
            return
        values = self.appointments_tree.item(item, 'values')
        appointment_number = values[0]
        appointment = self.db.fetchone("SELECT * FROM appointments WHERE appointment_number=?", (appointment_number,))
        if not appointment:
            return
        self.current_editing_appointment = appointment['id']
        self.customer_name_var.set(appointment['customer_name'])
        self.customer_phone_var.set(appointment['phone'])
        self.notes_var.set(appointment['notes'] or '')
        self.price_var.set(appointment['price'])
        self.payment_method_var.set(appointment['payment_method'] or 'نقدي')
        self.payment_status_var.set(appointment['payment_status'] or 'unpaid')
        if DateEntry:
            self.date_entry.set_date(datetime.strptime(appointment['appointment_date'], '%Y-%m-%d'))
        else:
            self.date_var.set(appointment['appointment_date'])
        self.time_combo.set(appointment['appointment_time'])

        for idx, value in enumerate(self.barber_combo['values']):
            if value.startswith(f"{appointment['barber_id']} "):
                self.barber_combo.current(idx)
                break
        for idx, value in enumerate(self.service_combo['values']):
            if value.startswith(f"{appointment['service_id']} "):
                self.service_combo.current(idx)
                break
        arabic_message('تحرير موعد', 'يمكنك الآن تعديل بيانات الموعد ثم الضغط على "حفظ الموعد".', 'info')

    def on_appointment_select(self, _event: Optional[tk.Event] = None) -> None:
        item = self.appointments_tree.focus()
        if not item:
            self.current_selected_appointment = None
            return
        values = self.appointments_tree.item(item, 'values')
        appointment = self.db.fetchone("SELECT id FROM appointments WHERE appointment_number=?", (values[0],))
        if appointment:
            self.current_selected_appointment = appointment['id']

    def validate_appointment_inputs(self) -> bool:
        if not self.customer_name_var.get().strip():
            arabic_message('تنبيه', 'يرجى إدخال اسم العميل.', 'warning')
            return False
        phone = self.customer_phone_var.get().strip()
        if not phone or len(phone) < 8:
            arabic_message('تنبيه', 'يرجى إدخال رقم جوال صحيح.', 'warning')
            return False
        if not self.barber_var.get():
            arabic_message('تنبيه', 'يرجى اختيار الحلاق.', 'warning')
            return False
        if not self.service_var.get():
            arabic_message('تنبيه', 'يرجى اختيار الخدمة.', 'warning')
            return False
        date_value = self.date_var.get() if not DateEntry else self.date_entry.get_date().isoformat()
        try:
            datetime.strptime(date_value, '%Y-%m-%d')
        except ValueError:
            arabic_message('تنبيه', 'صيغة التاريخ غير صحيحة.', 'warning')
            return False
        if not self.time_var.get():
            arabic_message('تنبيه', 'يرجى اختيار وقت الموعد.', 'warning')
            return False
        return True


    def save_appointment(self) -> None:
        if not self.validate_appointment_inputs():
            return
        try:
            barber_id = int(self.barber_var.get().split('-')[0].strip())
            service_id = int(self.service_var.get().split('-')[0].strip())
        except (ValueError, IndexError):
            arabic_message('خطأ', 'تعذر قراءة بيانات الحلاق أو الخدمة.', 'error')
            return
        appointment_date = self.date_var.get() if not DateEntry else self.date_entry.get_date().isoformat()
        appointment_time = self.time_var.get()
        conflict_query = (
            "SELECT COUNT(*) AS count FROM appointments WHERE barber_id=? AND appointment_date=? AND appointment_time=?"
            " AND status NOT IN ('cancelled', 'completed')"
        )
        if self.current_editing_appointment:
            conflict_query += " AND id != ?"
            conflict_params = (barber_id, appointment_date, appointment_time, self.current_editing_appointment)
        else:
            conflict_params = (barber_id, appointment_date, appointment_time)
        conflict = self.db.fetchone(conflict_query, conflict_params)
        if conflict and conflict['count'] > 0:
            arabic_message('تعارض', 'يوجد موعد آخر للحلاق في نفس الوقت.', 'warning')
            return

        service = self.db.fetchone("SELECT price, cost, duration, commission_rate FROM services WHERE id=?", (service_id,))
        barber = self.db.fetchone("SELECT name, commission_rate FROM barbers WHERE id=?", (barber_id,))
        if not service or not barber:
            arabic_message('خطأ', 'تعذر تحميل بيانات الخدمة أو الحلاق.', 'error')
            return

        price = self.price_var.get() or service['price']
        cost = service['cost']
        duration = service['duration']
        commission_rate = service['commission_rate'] or barber['commission_rate']
        commission_value = (price * commission_rate) / 100

        customer_id = self.ensure_customer_exists(
            name=self.customer_name_var.get().strip(),
            phone=self.customer_phone_var.get().strip(),
            email=self.customer_email_var.get().strip() or None,
        )
        appointment_data = (
            customer_id,
            self.customer_name_var.get().strip(),
            self.customer_phone_var.get().strip(),
            barber_id,
            barber['name'],
            service_id,
            self.service_var.get().split('-', 1)[1].strip(),
            appointment_date,
            appointment_time,
            duration,
            price,
            cost,
            commission_value,
            self.payment_method_var.get(),
            self.payment_status_var.get(),
            self.notes_var.get().strip(),
        )
        try:
            if self.current_editing_appointment:
                query = '''
                    UPDATE appointments
                    SET customer_id=?, customer_name=?, phone=?, barber_id=?, barber_name=?,
                        service_id=?, service_name=?, appointment_date=?, appointment_time=?, duration=?,
                        price=?, cost=?, commission=?, payment_method=?, payment_status=?, notes=?
                    WHERE id=?
                '''
                self.db.execute(query, appointment_data + (self.current_editing_appointment,))
                arabic_message('تم', 'تم تحديث بيانات الموعد بنجاح.', 'info')
            else:
                appointment_number = self.generate_appointment_number()
                insert_query = '''
                    INSERT INTO appointments (
                        appointment_number, customer_id, customer_name, phone, barber_id, barber_name,
                        service_id, service_name, appointment_date, appointment_time, duration,
                        status, price, cost, commission, payment_method, payment_status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)
                '''
                self.db.execute(insert_query, (appointment_number,) + appointment_data)
                arabic_message('تم', 'تم حفظ الموعد الجديد بنجاح.', 'info')
            self.clear_booking_form()
            self.load_appointments()
            self.update_dashboard()
        except sqlite3.IntegrityError as error:
            arabic_message('خطأ', f'تعذر حفظ الموعد\n{error}', 'error')
        except Exception as error:
            arabic_message('خطأ', f'حدث خطأ غير متوقع\n{error}', 'error')

    def ensure_customer_exists(self, name: str, phone: str, email: Optional[str]) -> Optional[int]:
        customer = self.db.fetchone("SELECT id FROM customers WHERE phone=?", (phone,))
        if customer:
            return customer['id']
        self.db.execute(
            '''INSERT INTO customers (name, phone, email, total_visits, total_spent, loyalty_points) VALUES (?, ?, ?, 0, 0, 0)''',
            (name, phone, email)
        )
        new_customer = self.db.fetchone("SELECT id FROM customers WHERE phone=?", (phone,))
        return new_customer['id'] if new_customer else None

    def load_appointments(self) -> None:
        self.appointments_tree.delete(*self.appointments_tree.get_children())
        search_term = f"%{self.search_var.get().strip()}%"
        selected_date = self.appointment_date_var.get() if not DateEntry else self.appointment_date_entry.get_date().isoformat()
        rows = self.db.fetchall('''
            SELECT appointment_number, appointment_time, customer_name, phone, barber_name,
                   service_name, price, status
            FROM appointments
            WHERE appointment_date=? AND (
                appointment_number LIKE ? OR customer_name LIKE ? OR phone LIKE ?
            )
            ORDER BY appointment_time
        ''', (selected_date, search_term, search_term, search_term))
        for row in rows:
            self.appointments_tree.insert('', tk.END, values=(
                row['appointment_number'],
                row['appointment_time'],
                row['customer_name'],
                row['phone'],
                row['barber_name'],
                row['service_name'],
                format_currency(row['price']),
                self.translate_status(row['status']),
            ))
        self.update_dashboard()

    def translate_status(self, status: str) -> str:
        mapping = {
            'pending': '📅 معلق',
            'confirmed': '✅ مؤكد',
            'completed': '✅ مكتمل',
            'cancelled': '❌ ملغي',
            'no_show': '🚫 غائب',
        }
        return mapping.get(status, status)

    def delete_selected_appointment(self) -> None:
        if not self.current_selected_appointment:
            arabic_message('تنبيه', 'يرجى اختيار موعد أولاً.', 'warning')
            return
        if not messagebox.askyesno('تأكيد', 'هل ترغب في حذف الموعد المحدد؟'):
            return
        self.db.execute("DELETE FROM appointments WHERE id=?", (self.current_selected_appointment,))
        self.current_selected_appointment = None
        arabic_message('تم', 'تم حذف الموعد بنجاح.', 'info')
        self.load_appointments()

    def change_appointment_status(self, new_status: str) -> None:
        if not self.current_selected_appointment:
            arabic_message('تنبيه', 'يرجى اختيار موعد أولاً.', 'warning')
            return
        self.db.execute("UPDATE appointments SET status=? WHERE id=?", (new_status, self.current_selected_appointment))
        arabic_message('تم', 'تم تحديث حالة الموعد.', 'info')
        self.load_appointments()


    def complete_appointment(self) -> None:
        if not self.current_selected_appointment:
            arabic_message('تنبيه', 'يرجى اختيار موعد لإكماله.', 'warning')
            return
        appointment = self.db.fetchone("SELECT * FROM appointments WHERE id=?", (self.current_selected_appointment,))
        if not appointment:
            arabic_message('خطأ', 'تعذر العثور على الموعد.', 'error')
            return
        if appointment['status'] == 'completed':
            arabic_message('تنبيه', 'الموعد مكتمل بالفعل.', 'warning')
            return
        total_price = appointment['price']
        total_cost = appointment['cost']
        total_commission = appointment['commission']
        points_earned = int(total_price * 0.1)
        session_number = self.generate_session_number()
        services_json = json.dumps([{
            'service_id': appointment['service_id'],
            'service_name': appointment['service_name'],
            'price': appointment['price'],
            'cost': appointment['cost'],
            'commission': appointment['commission'],
            'duration': appointment['duration'],
        }], ensure_ascii=False)
        self.db.execute('''
            INSERT INTO sessions (
                session_number, customer_id, customer_name, barber_id, barber_name, services,
                total_price, total_cost, total_commission, discount, final_price, payment_method,
                loyalty_points_earned, loyalty_points_used, status, check_in_time, check_out_time, duration, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 0, 'completed', ?, ?, ?, ?)
        ''', (
            session_number,
            appointment['customer_id'],
            appointment['customer_name'],
            appointment['barber_id'],
            appointment['barber_name'],
            services_json,
            total_price,
            total_cost,
            total_commission,
            total_price,
            appointment['payment_method'] or 'نقدي',
            points_earned,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            appointment['duration'],
            appointment['notes'],
        ))
        self.db.execute(
            "UPDATE appointments SET status='completed', completed_at=? WHERE id=?",
            (datetime.now().isoformat(), self.current_selected_appointment)
        )
        self.update_customer_stats(appointment['customer_id'], total_price, points_earned)
        self.update_barber_stats(appointment['barber_id'], total_price)
        arabic_message('تم', 'تم إنهاء الموعد وتحويله إلى جلسة مكتملة.', 'info')
        self.load_appointments()

    def update_customer_stats(self, customer_id: Optional[int], amount: float, points: int) -> None:
        if not customer_id:
            return
        self.db.execute('''
            UPDATE customers
            SET total_visits = total_visits + 1,
                total_spent = total_spent + ?,
                loyalty_points = loyalty_points + ?,
                last_visit = ?
            WHERE id=?
        ''', (amount, points, datetime.now().isoformat(), customer_id))

    def update_barber_stats(self, barber_id: int, amount: float) -> None:
        self.db.execute('''
            UPDATE barbers
            SET total_services = total_services + 1,
                total_revenue = total_revenue + ?
            WHERE id=?
        ''', (amount, barber_id))

    def generate_appointment_number(self) -> str:
        today = datetime.now().strftime('%Y%m%d')
        count = self.db.fetchone(
            "SELECT COUNT(*) AS count FROM appointments WHERE appointment_number LIKE ?",
            (f'APP-{today}%',)
        )['count'] + 1
        return f'APP-{today}-{count:03d}'

    def generate_session_number(self) -> str:
        today = datetime.now().strftime('%Y%m%d')
        count = self.db.fetchone(
            "SELECT COUNT(*) AS count FROM sessions WHERE session_number LIKE ?",
            (f'SES-{today}%',)
        )['count'] + 1
        return f'SES-{today}-{count:03d}'


    def search_customer_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title('البحث عن عميل')
        dialog.geometry('420x400')
        dialog.transient(self.root)
        dialog.grab_set()
        search_var = tk.StringVar()
        ttk.Label(dialog, text='اكتب الاسم أو رقم الجوال:').pack(pady=10)
        entry = ttk.Entry(dialog, textvariable=search_var, width=40)
        entry.pack(pady=5)
        entry.focus()
        results_tree = ttk.Treeview(dialog, columns=('name', 'phone'), show='headings', height=10)
        results_tree.heading('name', text='الاسم')
        results_tree.heading('phone', text='الجوال')
        results_tree.column('name', anchor='e', width=200)
        results_tree.column('phone', anchor='center', width=140)
        results_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def perform_search(*_args: object) -> None:
            results_tree.delete(*results_tree.get_children())
            term = f"%{search_var.get().strip()}%"
            rows = self.db.fetchall('SELECT name, phone FROM customers WHERE name LIKE ? OR phone LIKE ? LIMIT 30', (term, term))
            for row in rows:
                results_tree.insert('', tk.END, values=(row['name'], row['phone']))

        def select_customer() -> None:
            item = results_tree.focus()
            if not item:
                return
            name, phone = results_tree.item(item, 'values')
            self.customer_name_var.set(name)
            self.customer_phone_var.set(phone)
            dialog.destroy()

        ttk.Button(dialog, text='بحث', style='Primary.TButton', command=perform_search).pack(pady=5)
        ttk.Button(dialog, text='اختيار', style='Success.TButton', command=select_customer).pack(pady=5)
        entry.bind('<Return>', perform_search)
        results_tree.bind('<Double-1>', lambda _e: (select_customer()))
        perform_search()

    def open_walk_in_session(self) -> None:
        WalkInSessionWindow(self)

    def open_customers_window(self) -> None:
        CustomersWindow(self)

    def open_barbers_window(self) -> None:
        BarbersWindow(self)

    def open_services_window(self) -> None:
        ServicesWindow(self)

    def show_daily_report(self) -> None:
        DailyReportWindow(self)

    def show_monthly_report(self) -> None:
        MonthlyReportWindow(self)

    def export_to_excel(self) -> None:
        selected_date = self.appointment_date_var.get() if not DateEntry else self.appointment_date_entry.get_date().isoformat()
        rows = self.db.fetchall('''
            SELECT appointment_number, appointment_date, appointment_time, customer_name, phone,
                   barber_name, service_name, price, status
            FROM appointments
            WHERE appointment_date=?
            ORDER BY appointment_time
        ''', (selected_date,))
        if not rows:
            arabic_message('تنبيه', 'لا توجد مواعيد في التاريخ المحدد.', 'warning')
            return
        data = []
        for row in rows:
            data.append({
                'رقم الموعد': row['appointment_number'],
                'التاريخ': row['appointment_date'],
                'الوقت': row['appointment_time'],
                'اسم العميل': row['customer_name'],
                'رقم الجوال': row['phone'],
                'الحلاق': row['barber_name'],
                'الخدمة': row['service_name'],
                'السعر': row['price'],
                'الحالة': self.translate_status(row['status']),
            })
        df = pd.DataFrame(data)
        export_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            initialdir='exports',
            filetypes=[('Excel', '*.xlsx')],
            title='اختر مكان حفظ الملف'
        )
        if not export_path:
            return
        df.to_excel(export_path, index=False)
        arabic_message('تم', f'تم تصدير المواعيد إلى الملف\n{export_path}', 'info')

    def backup_database(self) -> None:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = Path('backups') / f'backup_{timestamp}.db'
            shutil.copy2(self.db_path, backup_file)
            backups = sorted(Path('backups').glob('backup_*.db'))
            if len(backups) > 30:
                for file_path in backups[:-30]:
                    file_path.unlink()
            arabic_message('نجاح', f'تم إنشاء نسخة احتياطية\n{backup_file}', 'info')
        except Exception as error:
            arabic_message('خطأ', f'فشل النسخ الاحتياطي\n{error}', 'error')

    def open_settings_window(self) -> None:
        SettingsWindow(self)

    def setup_keyboard_shortcuts(self) -> None:
        self.root.bind('<Control-n>', lambda _: self.clear_booking_form())
        self.root.bind('<Control-s>', lambda _: self.save_appointment())
        self.root.bind('<Control-f>', lambda _: self.load_appointments())
        self.root.bind('<Control-c>', lambda _: self.open_customers_window())
        self.root.bind('<Control-b>', lambda _: self.open_barbers_window())
        self.root.bind('<Control-m>', lambda _: self.open_services_window())
        self.root.bind('<Control-r>', lambda _: self.show_daily_report())
        self.root.bind('<Control-e>', lambda _: self.export_to_excel())
        self.root.bind('<Control-d>', lambda _: self.backup_database())
        self.root.bind('<F5>', lambda _: self.load_appointments())
        self.root.bind('<Delete>', lambda _: self.delete_selected_appointment())



class WalkInSessionWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('جلسة فورية')
        self.window.geometry('720x560')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.customer_name_var = tk.StringVar(value=app.customer_name_var.get())
        self.customer_phone_var = tk.StringVar(value=app.customer_phone_var.get())
        self.barber_var = tk.StringVar()
        self.payment_method_var = tk.StringVar(value='نقدي')
        self.discount_var = tk.DoubleVar(value=0)
        self.points_to_use_var = tk.IntVar(value=0)
        self.notes_var = tk.StringVar()

        self.selected_services: List[Dict[str, float]] = []

        self.build_interface()
        self.populate_lists()
        self.calculate_totals()

    def build_interface(self) -> None:
        form = ttk.Frame(self.window, padding=10)
        form.pack(fill=tk.X)
        ttk.Label(form, text='اسم العميل:').grid(row=0, column=2, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.customer_name_var, width=28, justify='right').grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text='رقم الجوال:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.customer_phone_var, width=20, justify='right').grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(form, text='الحلاق:').grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.barber_combo = ttk.Combobox(form, textvariable=self.barber_var, state='readonly', width=25, justify='right')
        self.barber_combo.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form, text='طريقة الدفع:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.payment_combo = ttk.Combobox(form, textvariable=self.payment_method_var, state='readonly', values=('نقدي', 'بطاقة', 'تحويل بنكي'), width=18)
        self.payment_combo.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(form, text='الخدمة:').grid(row=2, column=2, sticky='e', padx=5, pady=5)
        self.service_combo = ttk.Combobox(form, state='readonly', width=40, justify='right')
        self.service_combo.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(form, text='إضافة', style='Success.TButton', command=self.add_service).grid(row=2, column=0, padx=5, pady=5)

        columns = ('name', 'price', 'duration')
        self.services_tree = ttk.Treeview(self.window, columns=columns, show='headings', height=10)
        self.services_tree.heading('name', text='الخدمة')
        self.services_tree.heading('price', text='السعر')
        self.services_tree.heading('duration', text='المدة (دقيقة)')
        self.services_tree.column('name', anchor='e', width=280)
        self.services_tree.column('price', anchor='center', width=120)
        self.services_tree.column('duration', anchor='center', width=120)
        self.services_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(self.window, text='حذف الخدمة المختارة', style='Danger.TButton', command=self.remove_service).pack(pady=5)

        totals_frame = ttk.Frame(self.window, padding=10)
        totals_frame.pack(fill=tk.X)
        self.total_price_var = tk.DoubleVar(value=0)
        self.total_cost_var = tk.DoubleVar(value=0)
        self.total_commission_var = tk.DoubleVar(value=0)
        self.final_price_var = tk.DoubleVar(value=0)
        ttk.Label(totals_frame, text='الإجمالي:').grid(row=0, column=3, sticky='e', padx=5, pady=5)
        ttk.Label(totals_frame, textvariable=tk.StringVar(value='0 ر.س'), foreground=COLORS['primary']).grid(row=0, column=2, sticky='e')
        self.total_price_label = ttk.Label(totals_frame, text='0 ر.س', font=FONTS['body'])
        self.total_price_label.grid(row=0, column=1, sticky='e', padx=5)

        ttk.Label(totals_frame, text='الخصم:').grid(row=1, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(totals_frame, textvariable=self.discount_var, width=10, justify='center').grid(row=1, column=2, sticky='e', padx=5)
        ttk.Label(totals_frame, text='النقاط المستخدمة:').grid(row=1, column=1, sticky='e', padx=5)
        ttk.Entry(totals_frame, textvariable=self.points_to_use_var, width=10, justify='center').grid(row=1, column=0, sticky='e', padx=5)

        ttk.Label(totals_frame, text='السعر النهائي:').grid(row=2, column=3, sticky='e', padx=5, pady=5)
        self.final_price_label = ttk.Label(totals_frame, text='0 ر.س', font=FONTS['subtitle'], foreground=COLORS['success'])
        self.final_price_label.grid(row=2, column=2, sticky='e', padx=5)

        ttk.Label(self.window, text='ملاحظات:').pack(anchor='e', padx=15)
        ttk.Entry(self.window, textvariable=self.notes_var, width=80, justify='right').pack(fill=tk.X, padx=15, pady=5)

        buttons = ttk.Frame(self.window, padding=10)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text='إتمام الجلسة', style='Success.TButton', command=self.complete_session).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='إغلاق', style='Danger.TButton', command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def populate_lists(self) -> None:
        barbers = self.app.db.fetchall("SELECT id, name FROM barbers WHERE status='active' ORDER BY name")
        values = [f"{row['id']} - {row['name']}" for row in barbers]
        self.barber_combo['values'] = values
        if values:
            self.barber_combo.current(0)
        services = self.app.db.fetchall("SELECT id, name, price FROM services WHERE status='active' ORDER BY category, name")
        self.service_combo['values'] = [f"{row['id']} - {row['name']} ({format_currency(row['price'])})" for row in services]
        if services:
            self.service_combo.current(0)

    def add_service(self) -> None:
        value = self.service_combo.get()
        if not value:
            return
        try:
            service_id = int(value.split('-')[0].strip())
        except (ValueError, IndexError):
            return
        service = self.app.db.fetchone("SELECT * FROM services WHERE id=?", (service_id,))
        if not service:
            return
        entry = {
            'service_id': service['id'],
            'name': service['name'],
            'price': service['price'],
            'cost': service['cost'],
            'commission_rate': service['commission_rate'],
            'duration': service['duration'],
        }
        self.selected_services.append(entry)
        self.services_tree.insert('', tk.END, values=(entry['name'], format_currency(entry['price']), entry['duration']))
        self.calculate_totals()

    def remove_service(self) -> None:
        item = self.services_tree.focus()
        if not item:
            return
        index = self.services_tree.index(item)
        self.services_tree.delete(item)
        if 0 <= index < len(self.selected_services):
            self.selected_services.pop(index)
        self.calculate_totals()

    def calculate_totals(self) -> None:
        total_price = sum(s['price'] for s in self.selected_services)
        total_cost = sum(s['cost'] for s in self.selected_services)
        total_commission = 0
        barber_rate = 0
        try:
            barber_id = int(self.barber_var.get().split('-')[0].strip())
            barber = self.app.db.fetchone("SELECT commission_rate FROM barbers WHERE id=?", (barber_id,))
            barber_rate = barber['commission_rate'] if barber else 0
        except Exception:
            barber_rate = 0
        for service in self.selected_services:
            rate = service['commission_rate'] or barber_rate
            total_commission += (service['price'] * rate) / 100
        discount = self.discount_var.get() or 0
        points_discount = self.points_to_use_var.get() * 0.5
        final_price = max(total_price - discount - points_discount, 0)
        self.total_price_var.set(total_price)
        self.total_cost_var.set(total_cost)
        self.total_commission_var.set(total_commission)
        self.final_price_var.set(final_price)
        self.total_price_label.config(text=format_currency(total_price))
        self.final_price_label.config(text=format_currency(final_price))

    def complete_session(self) -> None:
        if not self.selected_services:
            arabic_message('تنبيه', 'يرجى إضافة خدمة واحدة على الأقل.', 'warning')
            return
        name = self.customer_name_var.get().strip()
        phone = self.customer_phone_var.get().strip()
        if not name or not phone:
            arabic_message('تنبيه', 'الاسم ورقم الجوال مطلوبان.', 'warning')
            return
        try:
            barber_id = int(self.barber_var.get().split('-')[0].strip())
        except (ValueError, IndexError):
            arabic_message('تنبيه', 'يرجى اختيار الحلاق.', 'warning')
            return
        barber = self.app.db.fetchone("SELECT name, commission_rate FROM barbers WHERE id=?", (barber_id,))
        if not barber:
            arabic_message('خطأ', 'تعذر العثور على بيانات الحلاق.', 'error')
            return
        customer_id = self.app.ensure_customer_exists(name=name, phone=phone, email=None)
        services_json = json.dumps(self.selected_services, ensure_ascii=False)
        session_number = self.app.generate_session_number()
        total_price = self.total_price_var.get()
        total_cost = self.total_cost_var.get()
        total_commission = self.total_commission_var.get()
        discount = self.discount_var.get() or 0
        points_used = max(self.points_to_use_var.get(), 0)
        points_discount = points_used * 0.5
        final_price = max(total_price - discount - points_discount, 0)
        points_earned = int(final_price * 0.1)
        self.app.db.execute('''
            INSERT INTO sessions (
                session_number, customer_id, customer_name, barber_id, barber_name, services,
                total_price, total_cost, total_commission, discount, final_price, payment_method,
                loyalty_points_earned, loyalty_points_used, status, check_in_time, check_out_time, duration, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?, ?, ?, ?)
        ''', (
            session_number,
            customer_id,
            name,
            barber_id,
            barber['name'],
            services_json,
            total_price,
            total_cost,
            total_commission,
            discount + points_discount,
            final_price,
            self.payment_method_var.get(),
            points_earned,
            points_used,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            sum(s['duration'] for s in self.selected_services),
            self.notes_var.get().strip(),
        ))
        self.app.update_customer_stats(customer_id, final_price, points_earned - points_used)
        self.app.update_barber_stats(barber_id, final_price)
        arabic_message('تم', 'تم حفظ الجلسة بنجاح.', 'info')
        self.app.update_dashboard()
        self.window.destroy()



class CustomersWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('إدارة العملاء')
        self.window.geometry('900x600')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.search_var = tk.StringVar()
        self.selected_customer_id: Optional[int] = None

        self.build_interface()
        self.load_customers()

    def build_interface(self) -> None:
        search_frame = ttk.Frame(self.window, padding=10)
        search_frame.pack(fill=tk.X)
        ttk.Label(search_frame, text='🔍 بحث:').pack(side=tk.RIGHT, padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.RIGHT, padx=5)
        search_entry.bind('<Return>', lambda _e: self.load_customers())
        ttk.Button(search_frame, text='بحث', style='Primary.TButton', command=self.load_customers).pack(side=tk.RIGHT, padx=5)

        columns = ('name', 'phone', 'email', 'visits', 'spent', 'points')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', selectmode='browse')
        headings = ['الاسم', 'الجوال', 'البريد', 'الزيارات', 'إجمالي الإنفاق', 'النقاط']
        for col, title in zip(columns, headings):
            self.tree.heading(col, text=title)
            anchor = 'e' if col in ('name', 'phone', 'email') else 'center'
            width = 160 if col == 'name' else 120
            self.tree.column(col, anchor=anchor, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        form = ttk.LabelFrame(self.window, text='بيانات العميل', padding=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        ttk.Label(form, text='الاسم:').grid(row=0, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30, justify='right').grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(form, text='الجوال:').grid(row=0, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.phone_var, width=20, justify='right').grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text='البريد الإلكتروني:').grid(row=1, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.email_var, width=30, justify='right').grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(form, text='العنوان:').grid(row=1, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.address_var, width=30, justify='right').grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text='ملاحظات:').grid(row=2, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.notes_var, width=60, justify='right').grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        buttons = ttk.Frame(self.window, padding=10)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text='إضافة', style='Success.TButton', command=self.add_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='تحديث', style='Primary.TButton', command=self.update_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='حذف', style='Danger.TButton', command=self.delete_customer).pack(side=tk.RIGHT, padx=5)

    def load_customers(self) -> None:
        self.tree.delete(*self.tree.get_children())
        term = f"%{self.search_var.get().strip()}%"
        rows = self.app.db.fetchall('''
            SELECT * FROM customers
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY created_at DESC
        ''', (term, term))
        for row in rows:
            self.tree.insert('', tk.END, values=(
                row['name'],
                row['phone'],
                row['email'] or '',
                row['total_visits'],
                format_currency(row['total_spent']),
                row['loyalty_points'],
            ))

    def on_select(self, _event: Optional[tk.Event] = None) -> None:
        item = self.tree.focus()
        if not item:
            self.selected_customer_id = None
            return
        name, phone, *_rest = self.tree.item(item, 'values')
        customer = self.app.db.fetchone('SELECT * FROM customers WHERE phone=?', (phone,))
        if customer:
            self.selected_customer_id = customer['id']
            self.name_var.set(customer['name'])
            self.phone_var.set(customer['phone'])
            self.email_var.set(customer['email'] or '')
            self.address_var.set(customer['address'] or '')
            self.notes_var.set(customer['notes'] or '')

    def add_customer(self) -> None:
        if not self.name_var.get().strip() or not self.phone_var.get().strip():
            arabic_message('تنبيه', 'الاسم ورقم الجوال حقول إلزامية.', 'warning')
            return
        try:
            self.app.db.execute('''
                INSERT INTO customers (name, phone, email, address, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.name_var.get().strip(),
                self.phone_var.get().strip(),
                self.email_var.get().strip() or None,
                self.address_var.get().strip() or None,
                self.notes_var.get().strip() or None,
            ))
            arabic_message('تم', 'تم إضافة العميل بنجاح.', 'info')
            self.load_customers()
        except sqlite3.IntegrityError:
            arabic_message('خطأ', 'رقم الجوال مسجل مسبقاً.', 'error')

    def update_customer(self) -> None:
        if not self.selected_customer_id:
            arabic_message('تنبيه', 'اختر عميل لتحديث بياناته.', 'warning')
            return
        self.app.db.execute('''
            UPDATE customers
            SET name=?, phone=?, email=?, address=?, notes=?
            WHERE id=?
        ''', (
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip() or None,
            self.address_var.get().strip() or None,
            self.notes_var.get().strip() or None,
            self.selected_customer_id,
        ))
        arabic_message('تم', 'تم تحديث بيانات العميل.', 'info')
        self.load_customers()

    def delete_customer(self) -> None:
        if not self.selected_customer_id:
            arabic_message('تنبيه', 'اختر عميل لحذفه.', 'warning')
            return
        if not messagebox.askyesno('تأكيد', 'سيتم حذف العميل نهائياً، هل أنت متأكد؟'):
            return
        self.app.db.execute('DELETE FROM customers WHERE id=?', (self.selected_customer_id,))
        self.selected_customer_id = None
        arabic_message('تم', 'تم حذف العميل.', 'info')
        self.load_customers()



class BarbersWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('إدارة الحلاقين')
        self.window.geometry('850x560')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.selected_barber_id: Optional[int] = None

        self.build_interface()
        self.load_barbers()

    def build_interface(self) -> None:
        columns = ('name', 'phone', 'status', 'commission', 'services', 'revenue')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', selectmode='browse')
        headings = ['الاسم', 'الجوال', 'الحالة', 'العمولة %', 'عدد الخدمات', 'الإيرادات']
        for col, title in zip(columns, headings):
            self.tree.heading(col, text=title)
            anchor = 'e' if col in ('name', 'phone', 'status') else 'center'
            width = 150 if col in ('name', 'phone') else 110
            self.tree.column(col, anchor=anchor, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        form = ttk.LabelFrame(self.window, text='بيانات الحلاق', padding=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.specialization_var = tk.StringVar()
        self.commission_var = tk.DoubleVar(value=30)
        self.working_days_var = tk.StringVar()
        self.working_hours_var = tk.StringVar(value='09:00-18:00')
        self.status_var = tk.StringVar(value='active')
        ttk.Label(form, text='الاسم:').grid(row=0, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30, justify='right').grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(form, text='الجوال:').grid(row=0, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.phone_var, width=20, justify='right').grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text='البريد:').grid(row=1, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.email_var, width=30, justify='right').grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(form, text='التخصص:').grid(row=1, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.specialization_var, width=20, justify='right').grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text='نسبة العمولة %:').grid(row=2, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.commission_var, width=10, justify='center').grid(row=2, column=2, padx=5, pady=5)
        ttk.Label(form, text='أيام العمل:').grid(row=2, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.working_days_var, width=25, justify='right').grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(form, text='ساعات العمل:').grid(row=3, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.working_hours_var, width=15, justify='center').grid(row=3, column=2, padx=5, pady=5)
        ttk.Label(form, text='الحالة:').grid(row=3, column=1, sticky='e', padx=5, pady=5)
        status_combo = ttk.Combobox(form, textvariable=self.status_var, state='readonly', values=('active', 'inactive', 'vacation'), width=18)
        status_combo.grid(row=3, column=0, padx=5, pady=5)

        buttons = ttk.Frame(self.window, padding=10)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text='إضافة', style='Success.TButton', command=self.add_barber).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='تحديث', style='Primary.TButton', command=self.update_barber).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='حذف', style='Danger.TButton', command=self.delete_barber).pack(side=tk.RIGHT, padx=5)

    def load_barbers(self) -> None:
        self.tree.delete(*self.tree.get_children())
        rows = self.app.db.fetchall('SELECT * FROM barbers ORDER BY status DESC, name ASC')
        for row in rows:
            self.tree.insert('', tk.END, values=(
                row['name'],
                row['phone'],
                row['status'],
                row['commission_rate'],
                row['total_services'],
                format_currency(row['total_revenue']),
            ))

    def on_select(self, _event: Optional[tk.Event] = None) -> None:
        item = self.tree.focus()
        if not item:
            self.selected_barber_id = None
            return
        values = self.tree.item(item, 'values')
        barber = self.app.db.fetchone('SELECT * FROM barbers WHERE phone=?', (values[1],))
        if barber:
            self.selected_barber_id = barber['id']
            self.name_var.set(barber['name'])
            self.phone_var.set(barber['phone'])
            self.email_var.set(barber['email'] or '')
            self.specialization_var.set(barber['specialization'] or '')
            self.commission_var.set(barber['commission_rate'] or 0)
            self.working_days_var.set(barber['working_days'] or '')
            self.working_hours_var.set(barber['working_hours'] or '')
            self.status_var.set(barber['status'])

    def add_barber(self) -> None:
        if not self.name_var.get().strip() or not self.phone_var.get().strip():
            arabic_message('تنبيه', 'الاسم ورقم الجوال مطلوبان.', 'warning')
            return
        self.app.db.execute('''
            INSERT INTO barbers (name, phone, email, specialization, commission_rate, status, working_days, working_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip() or None,
            self.specialization_var.get().strip() or None,
            self.commission_var.get() or 0,
            self.status_var.get(),
            self.working_days_var.get().strip() or None,
            self.working_hours_var.get().strip() or None,
        ))
        arabic_message('تم', 'تم إضافة الحلاق بنجاح.', 'info')
        self.load_barbers()
        self.app.refresh_barber_service_lists()

    def update_barber(self) -> None:
        if not self.selected_barber_id:
            arabic_message('تنبيه', 'اختر حلاقاً لتحديث بياناته.', 'warning')
            return
        self.app.db.execute('''
            UPDATE barbers
            SET name=?, phone=?, email=?, specialization=?, commission_rate=?, status=?, working_days=?, working_hours=?
            WHERE id=?
        ''', (
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip() or None,
            self.specialization_var.get().strip() or None,
            self.commission_var.get() or 0,
            self.status_var.get(),
            self.working_days_var.get().strip() or None,
            self.working_hours_var.get().strip() or None,
            self.selected_barber_id,
        ))
        arabic_message('تم', 'تم تحديث بيانات الحلاق.', 'info')
        self.load_barbers()
        self.app.refresh_barber_service_lists()

    def delete_barber(self) -> None:
        if not self.selected_barber_id:
            arabic_message('تنبيه', 'اختر حلاقاً لحذفه.', 'warning')
            return
        if not messagebox.askyesno('تأكيد', 'سيتم حذف الحلاق نهائياً، هل أنت متأكد؟'):
            return
        self.app.db.execute('DELETE FROM barbers WHERE id=?', (self.selected_barber_id,))
        self.selected_barber_id = None
        arabic_message('تم', 'تم حذف الحلاق.', 'info')
        self.load_barbers()
        self.app.refresh_barber_service_lists()



class ServicesWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('إدارة الخدمات')
        self.window.geometry('820x540')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.selected_service_id: Optional[int] = None
        self.category_filter = tk.StringVar(value='الكل')

        self.build_interface()
        self.load_services()

    def build_interface(self) -> None:
        filter_frame = ttk.Frame(self.window, padding=10)
        filter_frame.pack(fill=tk.X)
        ttk.Label(filter_frame, text='التصنيف:').pack(side=tk.RIGHT, padx=5)
        categories = ['الكل'] + sorted({row['category'] for row in self.app.db.fetchall('SELECT DISTINCT category FROM services')})
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_filter, values=categories, state='readonly', width=18)
        self.category_combo.pack(side=tk.RIGHT, padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', lambda _e: self.load_services())

        columns = ('name', 'category', 'duration', 'price', 'status')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', selectmode='browse')
        headings = ['الخدمة', 'التصنيف', 'المدة (دقيقة)', 'السعر', 'الحالة']
        widths = [220, 150, 120, 120, 100]
        for col, title, width in zip(columns, headings, widths):
            self.tree.heading(col, text=title)
            self.tree.column(col, anchor='e', width=width)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        form = ttk.LabelFrame(self.window, text='بيانات الخدمة', padding=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.duration_var = tk.IntVar(value=30)
        self.price_var = tk.DoubleVar(value=50)
        self.cost_var = tk.DoubleVar(value=0)
        self.commission_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value='active')
        ttk.Label(form, text='الاسم:').grid(row=0, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30, justify='right').grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(form, text='التصنيف:').grid(row=0, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.category_var, width=20, justify='right').grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text='المدة (دقيقة):').grid(row=1, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.duration_var, width=10, justify='center').grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(form, text='السعر:').grid(row=1, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.price_var, width=12, justify='center').grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text='التكلفة:').grid(row=2, column=3, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.cost_var, width=12, justify='center').grid(row=2, column=2, padx=5, pady=5)
        ttk.Label(form, text='عمولة خاصة %:').grid(row=2, column=1, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.commission_var, width=12, justify='center').grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(form, text='الحالة:').grid(row=3, column=3, sticky='e', padx=5, pady=5)
        ttk.Combobox(form, textvariable=self.status_var, values=('active', 'inactive'), state='readonly', width=14).grid(row=3, column=2, padx=5, pady=5)

        buttons = ttk.Frame(self.window, padding=10)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text='إضافة', style='Success.TButton', command=self.add_service).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='تحديث', style='Primary.TButton', command=self.update_service).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text='حذف', style='Danger.TButton', command=self.delete_service).pack(side=tk.RIGHT, padx=5)

    def load_services(self) -> None:
        self.tree.delete(*self.tree.get_children())
        category = self.category_filter.get()
        if category and category != 'الكل':
            rows = self.app.db.fetchall('SELECT * FROM services WHERE category=? ORDER BY category, name', (category,))
        else:
            rows = self.app.db.fetchall('SELECT * FROM services ORDER BY category, name')
        for row in rows:
            self.tree.insert('', tk.END, values=(
                row['name'],
                row['category'],
                row['duration'],
                format_currency(row['price']),
                row['status'],
            ))

    def on_select(self, _event: Optional[tk.Event] = None) -> None:
        item = self.tree.focus()
        if not item:
            self.selected_service_id = None
            return
        name, *_ = self.tree.item(item, 'values')
        service = self.app.db.fetchone('SELECT * FROM services WHERE name=?', (name,))
        if service:
            self.selected_service_id = service['id']
            self.name_var.set(service['name'])
            self.category_var.set(service['category'])
            self.duration_var.set(service['duration'])
            self.price_var.set(service['price'])
            self.cost_var.set(service['cost'])
            self.commission_var.set(service['commission_rate'] or 0)
            self.status_var.set(service['status'])

    def add_service(self) -> None:
        if not self.name_var.get().strip() or not self.category_var.get().strip():
            arabic_message('تنبيه', 'الاسم والتصنيف مطلوبان.', 'warning')
            return
        self.app.db.execute('''
            INSERT INTO services (name, category, description, duration, price, cost, commission_rate, status)
            VALUES (?, ?, NULL, ?, ?, ?, ?, ?)
        ''', (
            self.name_var.get().strip(),
            self.category_var.get().strip(),
            self.duration_var.get(),
            self.price_var.get(),
            self.cost_var.get(),
            self.commission_var.get() or None,
            self.status_var.get(),
        ))
        arabic_message('تم', 'تم إضافة الخدمة.', 'info')
        self.load_services()
        self.app.refresh_barber_service_lists()

    def update_service(self) -> None:
        if not self.selected_service_id:
            arabic_message('تنبيه', 'اختر خدمة لتحديثها.', 'warning')
            return
        self.app.db.execute('''
            UPDATE services
            SET name=?, category=?, duration=?, price=?, cost=?, commission_rate=?, status=?
            WHERE id=?
        ''', (
            self.name_var.get().strip(),
            self.category_var.get().strip(),
            self.duration_var.get(),
            self.price_var.get(),
            self.cost_var.get(),
            self.commission_var.get() or None,
            self.status_var.get(),
            self.selected_service_id,
        ))
        arabic_message('تم', 'تم تحديث الخدمة.', 'info')
        self.load_services()
        self.app.refresh_barber_service_lists()

    def delete_service(self) -> None:
        if not self.selected_service_id:
            arabic_message('تنبيه', 'اختر خدمة لحذفها.', 'warning')
            return
        if not messagebox.askyesno('تأكيد', 'سيتم حذف الخدمة نهائياً، هل أنت متأكد؟'):
            return
        self.app.db.execute('DELETE FROM services WHERE id=?', (self.selected_service_id,))
        self.selected_service_id = None
        arabic_message('تم', 'تم حذف الخدمة.', 'info')
        self.load_services()
        self.app.refresh_barber_service_lists()



class DailyReportWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('التقرير اليومي')
        self.window.geometry('420x420')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.build_interface()
        self.load_report()

    def build_interface(self) -> None:
        frame = ttk.Frame(self.window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text='التاريخ:', font=FONTS['body']).pack(anchor='e')
        if DateEntry:
            self.date_entry = DateEntry(frame, textvariable=self.date_var, width=12, date_pattern='yyyy-mm-dd')
        else:
            self.date_entry = ttk.Entry(frame, textvariable=self.date_var, width=12, justify='center')
        self.date_entry.pack(pady=5)
        ttk.Button(frame, text='تحديث', style='Primary.TButton', command=self.load_report).pack(pady=5)
        self.report_text = tk.Text(frame, height=18, wrap='word', font=('Segoe UI', 11))
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def load_report(self) -> None:
        selected_date = self.date_var.get()
        sessions = self.app.db.fetchone('''
            SELECT COUNT(*) AS sessions, SUM(final_price) AS revenue, SUM(total_cost) AS cost,
                   SUM(total_commission) AS commission, SUM(loyalty_points_earned) AS points
            FROM sessions WHERE DATE(created_at)=?
        ''', (selected_date,))
        appointments = self.app.db.fetchone('SELECT COUNT(*) AS total FROM appointments WHERE appointment_date=?', (selected_date,))
        profit = (sessions['revenue'] or 0) - (sessions['cost'] or 0) - (sessions['commission'] or 0)
        text = (
            f"📅 التاريخ: {selected_date}\n"
            f"👥 عدد العملاء: {sessions['sessions'] or 0}\n"
            f"📊 عدد الخدمات: {appointments['total'] or 0}\n"
            f"💰 الإيرادات: {format_currency(sessions['revenue'] or 0)}\n"
            f"💵 التكاليف: {format_currency(sessions['cost'] or 0)}\n"
            f"💸 العمولات: {format_currency(sessions['commission'] or 0)}\n"
            f"✨ صافي الربح: {format_currency(profit)}\n"
            f"⭐ نقاط الولاء المكتسبة: {sessions['points'] or 0}\n"
        )
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, text)


class MonthlyReportWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('التقرير الشهري')
        self.window.geometry('540x520')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.month_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
        self.build_interface()
        self.load_report()

    def build_interface(self) -> None:
        frame = ttk.Frame(self.window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text='الشهر (YYYY-MM):').pack(anchor='e')
        ttk.Entry(frame, textvariable=self.month_var, width=12, justify='center').pack(pady=5)
        ttk.Button(frame, text='تحديث', style='Primary.TButton', command=self.load_report).pack(pady=5)
        self.report_text = tk.Text(frame, height=22, wrap='word', font=('Segoe UI', 11))
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def load_report(self) -> None:
        month = self.month_var.get()
        sessions = self.app.db.fetchone('''
            SELECT COUNT(*) AS sessions, SUM(final_price) AS revenue, SUM(total_cost) AS cost, SUM(total_commission) AS commission
            FROM sessions WHERE strftime('%Y-%m', created_at)=?
        ''', (month,))
        customers = self.app.db.fetchone('''
            SELECT COUNT(DISTINCT customer_id) AS total, SUM(loyalty_points_earned) AS points
            FROM sessions WHERE strftime('%Y-%m', created_at)=?
        ''', (month,))
        services = self.app.db.fetchall('''
            SELECT json_extract(value, '$.service_name') AS name, COUNT(*) AS count
            FROM sessions, json_each(sessions.services)
            WHERE strftime('%Y-%m', sessions.created_at)=?
            GROUP BY name
            ORDER BY count DESC
            LIMIT 5
        ''', (month,))
        profit = (sessions['revenue'] or 0) - (sessions['cost'] or 0) - (sessions['commission'] or 0)
        text = (
            f"📅 الفترة: {month}\n"
            f"👥 عدد العملاء: {customers['total'] or 0}\n"
            f"💰 الإيرادات: {format_currency(sessions['revenue'] or 0)}\n"
            f"💵 التكاليف: {format_currency(sessions['cost'] or 0)}\n"
            f"💸 العمولات: {format_currency(sessions['commission'] or 0)}\n"
            f"✨ صافي الربح: {format_currency(profit)}\n"
            "\n🏆 أفضل الخدمات:\n"
        )
        for row in services:
            text += f" - {row['name']}: {row['count']} مرة\n"
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, text)



class SettingsWindow:
    def __init__(self, app: BarbershopManagementSystem) -> None:
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('الإعدادات')
        self.window.geometry('400x380')
        self.window.configure(bg=COLORS['background'])
        self.window.transient(app.root)
        self.window.grab_set()

        self.fields = {
            'shop_name': tk.StringVar(value=app.settings_cache.get('shop_name', '')),
            'shop_address': tk.StringVar(value=app.settings_cache.get('shop_address', '')),
            'shop_phone': tk.StringVar(value=app.settings_cache.get('shop_phone', '')),
            'shop_email': tk.StringVar(value=app.settings_cache.get('shop_email', '')),
            'working_hours': tk.StringVar(value=app.settings_cache.get('working_hours', '')),
            'tax_rate': tk.StringVar(value=app.settings_cache.get('tax_rate', '15')),
        }

        self.build_interface()

    def build_interface(self) -> None:
        frame = ttk.Frame(self.window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        labels = {
            'shop_name': 'اسم المحل',
            'shop_address': 'العنوان',
            'shop_phone': 'رقم الجوال',
            'shop_email': 'البريد الإلكتروني',
            'working_hours': 'ساعات العمل',
            'tax_rate': 'نسبة الضريبة %',
        }
        for index, (key, label) in enumerate(labels.items()):
            ttk.Label(frame, text=label + ':').grid(row=index, column=1, sticky='e', padx=5, pady=5)
            ttk.Entry(frame, textvariable=self.fields[key], width=30, justify='right').grid(row=index, column=0, padx=5, pady=5)
        ttk.Button(frame, text='حفظ', style='Success.TButton', command=self.save_settings).grid(row=len(labels), column=0, columnspan=2, pady=15)

    def save_settings(self) -> None:
        for key, var in self.fields.items():
            self.app.db.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, var.get().strip()))
        self.app.load_settings_cache()
        arabic_message('تم', 'تم تحديث الإعدادات بنجاح.', 'info')
        self.window.destroy()



def main() -> None:
    root = tk.Tk()
    app = BarbershopManagementSystem(root)
    root.mainloop()


if __name__ == '__main__':
    main()
