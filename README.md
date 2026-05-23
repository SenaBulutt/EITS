# EİTS - Eczane İlaç Takip Sistemi

EİTS (Eczane İlaç Takip Sistemi), Veritabanı Yönetim Sistemleri (VTYS) dersi kapsamında geliştirilmiş bir web tabanlı eczane otomasyon projesidir.

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
* SQL tabanlı ilişkisel veritabanı yapısı

---

## Kullanılan Teknolojiler

* Python
* Flask
* SQLite
* SQLAlchemy
* HTML / CSS
* Jinja2

---

## Proje Yapısı

```text
EITS/
├── database/   → SQL script dosyaları
├── docs/       → Proje raporu ve sunum dosyaları
├── src/        → Uygulama kaynak kodları
├── README.md
└── .gitignore
```

---

## Kurulum

### Sanal ortam oluşturma

```bash
python3 -m venv venv
```

### Sanal ortamı aktifleştirme

```bash
source venv/bin/activate
```

### Gerekli bağımlılıkları yükleme

```bash
pip install -r requirements.txt
```

### Uygulamayı çalıştırma

```bash
python3 src/app.py
```

---

## Veritabanı

Veritabanı script dosyası:

```text
database/SQL_Script_Dosyası_EİTS.sql
```

---

## Güvenlik Notu

Projede gerçek kullanıcı verileri, gerçek e-posta bilgileri veya gizli şifreler paylaşılmamıştır. Tüm hassas bilgiler örnek (dummy) veriler ile değiştirilmiştir.

---

## Akademik Amaç

Bu proje, VTYS dersi kapsamında:

* ilişkisel veritabanı tasarımı,
* tablo ilişkileri,
* veri bütünlüğü,
* kullanıcı yönetimi
  ve temel web uygulama geliştirme süreçlerini uygulamalı olarak göstermek amacıyla hazırlanmıştır.
