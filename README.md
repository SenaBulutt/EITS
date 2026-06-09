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
## App.py Üzerinde Yapılması Gereken Ayarlar

Projeyi çalıştırmadan önce `app.py` dosyasında bulunan örnek güvenlik ve e-posta ayarları kullanıcı tarafından güncellenmelidir.

```python
app.secret_key = "gizli-anahtar-degistirilmeli"

SMTP_USERNAME = "KENDI_GMAIL_ADRESINIZ@gmail.com"
SMTP_PASSWORD = "KENDI_GMAIL_APP_SIFRENIZ"

## Veritabanı

Veritabanı script dosyası:

```text
database/SQL_Script_Dosyası_EİTS.sql
```
