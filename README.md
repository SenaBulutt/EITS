# EİTS - Eczane İlaç Takip Sistemi

EİTS (Eczane İlaç Takip Sistemi), Veri Tabanı Yönetim Sistemleri (VTYS) dersi kapsamında geliştirilmiş bir web tabanlı eczane otomasyon projesidir.

Bu sistem; ilaç stok yönetimi, satış işlemleri, kullanıcı yönetimi, hasta kayıtları ve raporlama süreçlerini dijital ortamda yönetmek amacıyla geliştirilmiştir.

---

## Özellikler

* Kullanıcı kayıt ve giriş sistemi
* Şifre sıfırlama ve e-posta doğrulama
* İlaç ekleme, güncelleme ve silme işlemleri
* İlaç stok takibi
* Satış işlemleri yönetimi
* Hasta kayıt sistemi
* Dashboard ve log sistemi
* Düşük stok ve son kullanma tarihi takibi
* SQL tabanlı ilişkisel veri tabanı yapısı

---

## Kullanılan Teknolojiler

* Python
* Flask
* SQLite
* SQLAlchemy
* HTML / CSS / JavaScript
* Werkzeug Security
* SMTP

---

## Proje Yapısı

```text
EITS/
├── database/        → SQL script dosyaları
├── src/             → Uygulama kaynak kodları
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Kurulum

### Sanal ortam oluşturma

```bash
# Windows
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

### Sanal ortamı aktifleştirme

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Gerekli bağımlılıkları yükleme

```bash
pip install -r requirements.txt
```

### Uygulamayı çalıştırma

```bash
# Windows
python src/app.py

# macOS / Linux
python3 src/app.py
```

---
## Not:Projeyi çalıştırmadan önce app.py dosyasında bulunan aşağıdaki örnek değerler kullanıcı tarafından kendi bilgileri ile değiştirilmelidir:

SECRET_KEY = "your_secret_key_here"
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_gmail_app_password"

## Veritabanı

Veritabanı script dosyası:

```text
database/SQL_Script_Dosyası_EİTS.sql
```
