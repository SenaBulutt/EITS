-- ==============================================
-- EİTS (Eczane İlaç Takip Sistemi) SQL Script Dosyası
-- Veritabanı: eczane.db (SQLite)
-- ==============================================

-- 1. KULLANICI TABLOSU (USER)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);

-- 2. KATEGORİ TABLOSU (KATEGORI)
CREATE TABLE kategori (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kategori_adi VARCHAR(100) UNIQUE NOT NULL
);

-- 3. FİRMA TABLOSU (FIRMA)
CREATE TABLE firma (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firma_adi VARCHAR(150) UNIQUE NOT NULL
);

-- 4. HASTA TABLOSU (HASTA)
CREATE TABLE hasta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hasta_tc VARCHAR(11) UNIQUE NOT NULL,
    hasta_ad VARCHAR(100) NOT NULL,
    hasta_soyad VARCHAR(100) NOT NULL
);

-- 5. İLAÇ TABLOSU (ILAC)
CREATE TABLE ilac (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad VARCHAR(100) NOT NULL,
    aktif_bilesen VARCHAR(100) NOT NULL,
    fiyat REAL NOT NULL,
    stok_miktari INTEGER NOT NULL,
    son_kullanma_tarihi VARCHAR(20) NOT NULL,
    aciklama TEXT,
    kategori_id INTEGER NOT NULL,
    firma_id INTEGER NOT NULL,
    FOREIGN KEY (kategori_id) REFERENCES kategori(id) ON DELETE CASCADE,
    FOREIGN KEY (firma_id) REFERENCES firma(id) ON DELETE CASCADE
);

-- 6. SATILAN İLAÇLAR TABLOSU (SOLD)
CREATE TABLE sold (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ilac_id INTEGER,
    user_id INTEGER,
    tarih_saat DATETIME DEFAULT CURRENT_TIMESTAMP,
    miktar INTEGER NOT NULL,
    satis_fiyati REAL NOT NULL DEFAULT 0,
    hasta_id INTEGER NOT NULL,
    FOREIGN KEY (ilac_id) REFERENCES ilac(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (hasta_id) REFERENCES hasta(id) ON DELETE CASCADE
);

-- 7. LOG TABLOSU (LOG)
CREATE TABLE log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(200) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details VARCHAR(300),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL
);

-- 8. SETTINGS TABLOSU (SETTINGS)
CREATE TABLE settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    eczane_ad VARCHAR(150) DEFAULT 'Modern Eczanesi',
    telefon VARCHAR(50) DEFAULT '(0212) 123 45 67',
    vergi_no VARCHAR(50) DEFAULT '1234567890',
    adres TEXT DEFAULT 'İstiklal Caddesi No:123 Beyoğlu/İstanbul',
    eposta VARCHAR(150) DEFAULT 'info@modernezcanesi.com',
    calisma_saatleri VARCHAR(150) DEFAULT '08:00 - 22:00 (Her Gün)',
    theme_color VARCHAR(30) DEFAULT '75, 85, 99',
    theme_dark VARCHAR(20) DEFAULT '#374151',
    theme_gradient VARCHAR(120) DEFAULT 'linear-gradient(135deg, #9ca3af, #4b5563)',
    kayit_sayisi INTEGER DEFAULT 25,
    zaman_dilimi VARCHAR(50) DEFAULT 'İstanbul (GMT+3)',
    low_stock_notification BOOLEAN DEFAULT 1,
    expiry_notification BOOLEAN DEFAULT 1,
    email_notification BOOLEAN DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 20,
    expiry_warning_days INTEGER DEFAULT 90,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 9. PASSWORD RESET TOKEN TABLOSU
CREATE TABLE password_reset_token (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(100) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- ==============================================
-- ÖRNEK VERİLER
-- ==============================================

-- Admin kullanıcısı (şifre: 123456)
INSERT INTO user (username, email, password) VALUES 
('admin', 'admin@gmail.com', 'pbkdf2:sha256:260000$3U2b8zF7H9qR6tXy$...');

-- Kategoriler
INSERT INTO kategori (id, kategori_adi) VALUES
(1, 'Ağrı Kesici'),
(2, 'Antibiyotik'),
(3, 'Mide İlacı'),
(4, 'Vitamin'),
(5, 'Alerji'),
(6, 'Öksürük Şurubu'),
(7, 'Kalp İlacı'),
(8, 'Tansiyon İlacı'),
(9, 'Şeker İlacı'),
(10, 'Antidepresan'),
(11, 'Antiviral'),
(12, 'Krem/Merhem'),
(13, 'Göz Damlası'),
(14, 'Kulak Damlası'),
(15, 'Burun Spreyi');

-- Firmalar
INSERT INTO firma (id, firma_adi) VALUES
(1, 'Abdi İbrahim'),
(2, 'Nobel İlaç'),
(3, 'Sanofi'),
(4, 'GlaxoSmithKline'),
(5, 'Pfizer'),
(6, 'Roche'),
(7, 'Merck'),
(8, 'Bayer'),
(9, 'Johnson & Johnson'),
(10, 'AstraZeneca'),
(11, 'Novartis'),
(12, 'Gilead Sciences'),
(13, 'Eli Lilly'),
(14, 'Bristol-Myers Squibb'),
(15, 'Teva'),
(16, 'Sandoz'),
(17, 'Mylan'),
(18, 'Dr. Reddy''s'),
(19, 'Sun Pharmaceutical'),
(20, 'Lupin Limited');

-- Hastalar
INSERT INTO hasta (hasta_tc, hasta_ad, hasta_soyad) VALUES
('12345678901', 'Ayşe', 'Yılmaz'),
('23456789012', 'Halil', 'Yalçın'),
('34567890123', 'Ahmet', 'Arslan'),
('45678901234', 'Seda', 'Toprak'),
('56789012345', 'Abdullah', 'Kılıç'),
('67890123456', 'Naciye', 'Aydın'),
('78901234567', 'Elif', 'Öztürk'),
('89012345678', 'Hülya', 'Yıldırım'),
('90123456789', 'Hasan', 'Demir'),
('01234567890', 'Zeliha', 'Çetin');

-- İlaçlar
INSERT INTO ilac (ad, aktif_bilesen, fiyat, stok_miktari, son_kullanma_tarihi, aciklama, kategori_id, firma_id) VALUES
('Parol', 'Parasetamol', 24.9, 120, '30.06.2027', 'Ateş ve ağrı kesici', 1, 1),
('Voltaren', 'Diklofenak Sodyum', 46.8, 65, '31.05.2027', 'Antienflamatuar jel', 1, 8),
('Augmentin', 'Amoksisilin/Klavulanat', 89.9, 45, '31.05.2027', 'Geniş spektrumlu antibiyotik', 2, 3),
('Januvia', 'Sitagliptin', 125.9, 40, '31.03.2027', 'Diyabet tedavisi', 9, 7),
('Zyrtec', 'Setirizin', 36.9, 105, '30.06.2027', 'Antihistaminik', 5, 10),
('Supradyn', 'Multivitamin', 79.9, 90, '31.12.2028', 'Multivitamin kompleksi', 4, 7),
('Diax', 'Valsartan', 68.9, 65, '31.12.2027', 'Tansiyon düşürücü', 8, 11),
('Lansor', 'Lansoprazol', 48.9, 75, '31.12.2027', 'Mide koruyucu', 3, 2),
('Selectra', 'Essitalopram', 78.9, 55, '31.05.2027', 'Antidepresan', 10, 2),
('Benical', 'Karbosistein', 34.9, 80, '31.05.2027', 'Balgam sökücü', 6, 1),
('Arveles', 'Dexketoprofen Trometamol', 38.75, 95, '31.03.2027', 'Ağrı kesici', 1, 1),
('Cipro', 'Siprofloksasin', 52.4, 50, '31.03.2027', 'Florokinolon antibiyotik', 2, 6),
('Nexium', 'Esomeprazol', 65.5, 60, '30.09.2027', 'Proton pompa inhibitörü', 3, 3),
('Berocca', 'B Kompleks Vitaminleri', 62.5, 70, '30.06.2027', 'B vitamini kompleksi', 4, 5),
('Aerius', 'Desloratadin', 42.5, 85, '31.03.2027', 'Alerji tedavisi', 5, 11),
('Solmucol', 'Asetilsistein', 29.5, 95, '30.09.2027', 'Balgam sökücü şurup', 6, 1),
('Coraspin', 'Asetilsalisilik Asit', 15.9, 150, '31.12.2027', 'Kan sulandırıcı', 7, 8),
('Cozap', 'Olmesartan Medoksomil', 75.5, 55, '30.09.2026', 'Hipertansiyon tedavisi', 8, 11),
('Glifor', 'Metformin', 32.5, 95, '31.12.2027', 'Tip 2 diyabet', 9, 2),
('Cipralex', 'Essitalopram', 85.5, 50, '30.09.2027', 'Depresyon tedavisi', 10, 5),
('Majezik', 'Dexketoprofen Trometamol', 42.5, 85, '31.12.2026', 'Ağrı kesici tablet', 1, 1),
('Klacid', 'Klaritromisin', 75.5, 55, '30.09.2026', 'Makrolid antibiyotik', 2, 5),
('Gaviscon', 'Aljinik Asit', 22.9, 100, '31.03.2027', 'Antiasit şurup', 3, 4),
('Redoxon', 'C Vitamini', 29.9, 130, '31.03.2027', 'C vitamini takviyesi', 4, 7),
('Telfast', 'Feksofenadin', 38.75, 95, '30.09.2026', 'Alerji ilacı', 5, 5),
('Bisolvon', 'Bromheksin', 26.8, 110, '31.03.2027', 'Öksürük şurubu', 6, 2),
('Plavix', 'Klopidogrel', 89.5, 55, '30.09.2027', 'Antiagregan', 7, 3),
('Norvasc', 'Amlodipin Besilat', 42.8, 80, '31.03.2027', 'Tansiyon ilacı', 8, 5),
('Diabet', 'Glibenklamid', 28.9, 85, '30.09.2026', 'Şeker hastalığı ilacı', 9, 2),
('Prozac', 'Fluoksetin', 72.8, 60, '31.03.2027', 'Antidepresan', 10, 5),
('Dolorex', 'Naproksen Sodyum', 35.2, 70, '30.09.2026', 'Antienflamatuar ağrı kesici', 1, 1),
('Sefaksin', 'Sefaleksin', 42.8, 65, '31.12.2026', 'Sefalosporin antibiyotik', 2, 1),
('Rennie', 'Kalsiyum Karbonat', 18.5, 120, '30.11.2026', 'Çiğneme tableti', 3, 3),
('Calcimax D3', 'Kalsiyum + D Vitamini', 45.8, 95, '30.09.2027', 'Kemik sağlığı', 4, 2),
('Clarityne', 'Loratadin', 28.9, 115, '31.12.2026', 'Antihistaminik', 5, 10),
('Tussidril', 'Dekstrometorfan', 31.9, 70, '30.06.2026', 'Öksürük kesici', 6, 1),
('Coversyl', 'Perindopril', 72.8, 60, '31.03.2027', 'ACE inhibitörü', 7, 3),
('Blopress', 'Kandesartan', 58.9, 60, '30.06.2027', 'Tansiyon tedavisi', 8, 15),
('Victoza', 'Liraglutid', 245.5, 30, '30.06.2027', 'GLP-1 agonisti', 9, 13),
('Tamiflu', 'Oseltamivir', 129.9, 35, '31.12.2026', 'Grip tedavisi', 11, 6),
('Apranax', 'Naproksen Sodyum', 32.9, 80, '31.12.2026', 'Ağrı kesici tablet', 1, 1),
('Zinnat', 'Sefuroksim Aksetil', 68.9, 40, '30.06.2027', 'Oral antibiyotik', 2, 4),
('Talcid', 'Hidrotalsit', 26.8, 85, '31.05.2027', 'Antiasit', 3, 8),
('Vitabiotic', 'Multivitamin', 85.5, 65, '31.12.2027', 'Premium multivitamin', 4, 4),
('Xyzal', 'Levosetirizin', 44.8, 75, '30.11.2027', 'Alerji tedavisi', 5, 11),
('Vicks', 'Guaifenesin', 24.5, 125, '31.12.2026', 'Öksürük şurubu', 6, 4),
('Amlopin', 'Amlodipin', 34.9, 85, '30.06.2027', 'Kalsiyum kanal blokeri', 7, 2),
('Minoset', 'Parasetamol', 19.5, 150, '28.02.2027', 'Ateş düşürücü', 1, 2),
('İbufen', 'İbuprofen', 28.75, 110, '30.11.2026', 'Ağrı ve ateş düşürücü', 1, 2),
('Glucophage', 'Metformin', 29.9, 100, '31.12.2026', 'Diyabet ilacı', 9, 3),
('Keflor', 'Sefaklor', 58.9, 50, '30.06.2028', 'Antibiyotik', 2, 12),
('One A Day', 'Multivitamin', 82.9, 70, '30.06.2030', 'Günlük vitamin', 4, 4),
('Clarinex', 'Desloratadin', 48.9, 80, '31.10.2032', 'Alerji tedavisi', 5, 10),
('Mopral', 'Omeprazol', 39.9, 85, '31.12.2026', 'Mide koruyucu', 3, 3),
('Zaditen', 'Ketotifen', 41.9, 95, '31.05.2031', 'Alerji tedavisi', 5, 10),
('Aspirin', 'Asetilsalisilik Asit', 18.5, 140, '31.05.2026', 'Ağrı kesici ve ateş düşürücü', 1, 1),
('Prilosec', 'Omeprazol', 44.9, 85, '31.12.2032', 'Mide ilacı', 3, 8),
('Tavist', 'Klemastin', 34.9, 90, '31.08.2029', 'Antihistaminik', 5, 20),
('Doliprane', 'Parasetamol', 22.9, 125, '31.03.2027', 'Ateş düşürücü', 1, 6),
('Sumamed', 'Azitromisin', 85.5, 40, '30.11.2032', 'Antibiyotik', 2, 12),
('Centrum', 'Multivitamin', 89.9, 60, '31.12.2027', 'Multivitamin', 4, 9),
('Ciprodex', 'Siprofloksasin + Deksametazon', 56.8, 55, '31.05.2032', 'Kulak damlası', 14, 18),
('Claritin', 'Loratadin', 32.8, 105, '31.05.2028', 'Alerji ilacı', 5, 15),
('Nature Made', 'Multivitamin', 68.9, 85, '30.09.2031', 'Doğal vitamin', 4, 9),
('Klamoks', 'Amoksisilin', 45.9, 65, '30.09.2026', 'Antibiyotik', 2, 2),
('Ultram', 'Tramadol', 52.9, 65, '31.03.2032', 'Güçlü ağrı kesici', 1, 6),
('Bepanthen Plus', 'Dexpantenol + Klorheksidin', 42.5, 75, '31.12.2030', 'Antibakteriyel krem', 12, 16),
('Advil', 'İbuprofen', 29.9, 115, '31.07.2029', 'Ağrı kesici', 1, 16),
('Biaxin', 'Klaritromisin', 78.9, 50, '30.07.2031', 'Antibiyotik', 2, 7),
('Zithromax', 'Azitromisin', 72.5, 45, '30.11.2029', 'Antibiyotik', 2, 17),
('Refresh Tears', 'Karboksimetilselüloz', 28.9, 120, '30.09.2031', 'Göz damlası', 13, 17),
('Allegra', 'Feksofenadin', 36.9, 95, '30.04.2027', 'Antihistaminik', 5, 10),
('Controloc', 'Pantoprazol', 49.9, 70, '31.12.2028', 'Mide koruyucu', 3, 13),
('Relenza', 'Zanamivir', 142.9, 35, '30.11.2029', 'Antiviral', 11, 5),
('Aciphex', 'Rabeprazol', 58.9, 70, '31.12.2032', 'Mide koruyucu', 3, 13),
('Allerest', 'Loratadin', 28.5, 110, '30.06.2026', 'Alerji ilacı', 5, 5),
('Nasonex', 'Mometazon', 64.9, 65, '30.11.2030', 'Burun spreyi', 15, 19),
('Advair', 'Flutikazon + Salmeterol', 128.9, 45, '31.12.2031', 'Solunum yolu ilacı', 6, 20),
('Anaprox', 'Naproksen', 35.9, 100, '31.08.2032', 'Ağrı kesici', 1, 11),
('Airborne', 'Vitamin C + Çinko', 34.9, 95, '30.09.2032', 'Bağışıklık desteği', 4, 9),
('Lopressor', 'Metoprolol', 45.9, 85, '30.06.2029', 'Beta bloker', 7, 1),
('Motrin', 'İbuprofen', 33.5, 110, '31.03.2031', 'Ağrı kesici', 1, 6),
('Periactin', 'Siproheptadin', 44.9, 80, '31.10.2032', 'Alerji ilacı', 5, 15),
('Ceftin', 'Sefuroksim', 62.9, 55, '30.09.2030', 'Antibiyotik', 2, 2),
('Vitaminex', 'Multivitamin', 75.5, 65, '30.09.2028', 'Vitamin takviyesi', 4, 14),
('Azitro', 'Azitromisin', 68.5, 55, '30.11.2027', 'Makrolid antibiyotik', 2, 7),
('Becozyme', 'B Kompleks Vitaminleri', 52.8, 70, '28.02.2026', 'Vitamin kompleksi', 4, 4),
('Nurofen', 'İbuprofen', 31.5, 100, '31.10.2028', 'Ağrı kesici', 1, 11),
('Paxil', 'Paroksetin', 78.9, 60, '31.05.2032', 'Antidepresan', 10, 4),
('Stress tabs', 'B Kompleks', 48.8, 75, '30.12.2029', 'Vitamin takviyesi', 4, 19),
('Glucotrol', 'Glipizid', 39.9, 90, '30.09.2031', 'Şeker ilacı', 9, 3),
('Levaquin', 'Levofloksasin', 92.5, 45, '30.07.2032', 'Florokinolon antibiyotik', 2, 7),
('Razo', 'Rabeprazol', 54.9, 65, '31.03.2029', 'Mide ilacı', 3, 18),
('Protonix', 'Pantoprazol', 52.5, 75, '31.12.2031', 'Mide ilacı', 3, 8),
('Semprex', 'Akrivastin', 39.9, 85, '31.10.2030', 'Alerji ilacı', 5, 5),
('Cozaar', 'Losartan', 68.5, 70, '31.12.2030', 'Tansiyon ilacı', 8, 2),
('Prevacid', 'Lansoprazol', 46.8, 80, '31.12.2030', 'Mide koruyucu', 3, 3),
('Pantpas', 'Pantoprazol', 42.8, 75, '31.08.2027', 'Mide ilacı', 3, 8),
('Aleve', 'Naproksen', 37.5, 95, '31.05.2030', 'Antienflamatuar', 1, 1),
('Mega Men', 'Multivitamin', 95.9, 60, '30.06.2032', 'Erkek multivitamin', 4, 14);

-- Satışlar
INSERT INTO sold (ilac_id, user_id, tarih_saat, miktar, satis_fiyati, hasta_id) VALUES
(1, 1, '2025-12-22 09:15:00', 2, 24.9, 1),
(3, 1, '2025-12-22 10:30:00', 1, 89.9, 2),
(6, 1, '2025-12-22 11:45:00', 1, 79.9, 3),
(5, 1, '2025-12-22 13:20:00', 1, 36.9, 4),
(17, 1, '2025-12-22 14:10:00', 3, 15.9, 5),
(19, 1, '2025-12-21 15:30:00', 2, 32.5, 6),
(2, 1, '2025-12-21 16:15:00', 1, 46.8, 7),
(13, 1, '2025-12-20 17:05:00', 1, 65.5, 8),
(20, 1, '2025-12-19 18:40:00', 1, 85.5, 9),
(14, 1, '2025-12-15 19:25:00', 2, 62.5, 10);

-- Settings tablosu için varsayılan kayıt
INSERT INTO settings (id) VALUES (1);

-- Örnek log kayıtları
INSERT INTO log (user_id, action, details) VALUES 
(1, 'Giriş', 'Admin kullanıcısı giriş yaptı'),
(1, 'İlaç Ekleme', 'Majezik ilacı eklendi'),
(1, 'Satış', '2 adet Parol satıldı');




-- ==============================================
-- EK VIEW'LER
-- ==============================================

-- İlaç detayları view'ı
CREATE VIEW vw_ilac_detay AS
SELECT 
    i.id,
    i.ad AS ilac_adi,
    i.aktif_bilesen,
    i.fiyat,
    i.stok_miktari,
    i.son_kullanma_tarihi,
    i.aciklama,
    k.kategori_adi,
    f.firma_adi,
    CASE 
        WHEN i.stok_miktari <= (SELECT low_stock_threshold FROM settings WHERE id = 1) THEN 'KRİTİK'
        WHEN i.stok_miktari <= (SELECT low_stock_threshold FROM settings WHERE id = 1) * 2 THEN 'DÜŞÜK'
        ELSE 'NORMAL'
    END AS stok_durumu
FROM ilac i
LEFT JOIN kategori k ON i.kategori_id = k.id
LEFT JOIN firma f ON i.firma_id = f.id;

-- Satış detayları view'ı
CREATE VIEW vw_satis_detay AS
SELECT 
    s.id,
    s.tarih_saat,
    i.ad AS ilac_adi,
    h.hasta_tc,
    h.hasta_ad,
    h.hasta_soyad,
    s.miktar,
    s.satis_fiyati,
    (s.miktar * s.satis_fiyati) AS toplam_tutar,
    u.username AS satan_kullanici
FROM sold s
LEFT JOIN ilac i ON s.ilac_id = i.id
LEFT JOIN hasta h ON s.hasta_id = h.id
LEFT JOIN user u ON s.user_id = u.id;

-- Günlük satış özeti view'ı
CREATE VIEW vw_gunluk_satis AS
SELECT 
    DATE(tarih_saat) AS tarih,
    COUNT(*) AS satis_sayisi,
    SUM(miktar) AS toplam_miktar,
    SUM(miktar * satis_fiyati) AS toplam_tutar
FROM sold
GROUP BY DATE(tarih_saat)
ORDER BY tarih DESC;

-- Düşük stoklu ilaçlar view'ı
CREATE VIEW vw_dusuk_stok AS
SELECT 
    i.id,
    i.ad AS ilac_adi,
    i.stok_miktari,
    k.kategori_adi,
    f.firma_adi,
    i.son_kullanma_tarihi
FROM ilac i
LEFT JOIN kategori k ON i.kategori_id = k.id
LEFT JOIN firma f ON i.firma_id = f.id
WHERE i.stok_miktari <= (SELECT low_stock_threshold FROM settings WHERE id = 1)
ORDER BY i.stok_miktari ASC;

-- Süresi yakın ilaçlar view'ı
CREATE VIEW vw_suresi_yakin AS
SELECT 
    i.id,
    i.ad AS ilac_adi,
    i.son_kullanma_tarihi,
    i.stok_miktari,
    k.kategori_adi,
    f.firma_adi,
    CASE 
        WHEN DATE('now', '+' || (SELECT expiry_warning_days FROM settings WHERE id = 1) || ' days') >= DATE(SUBSTR(i.son_kullanma_tarihi, 7, 4) || '-' || SUBSTR(i.son_kullanma_tarihi, 4, 2) || '-' || SUBSTR(i.son_kullanma_tarihi, 1, 2))
        THEN 'YAKIN'
        ELSE 'NORMAL'
    END AS durum
FROM ilac i
LEFT JOIN kategori k ON i.kategori_id = k.id
LEFT JOIN firma f ON i.firma_id = f.id
WHERE i.son_kullanma_tarihi IS NOT NULL AND i.son_kullanma_tarihi != '';

-- Kullanıcı işlem logları view'ı
CREATE VIEW vw_kullanici_log AS
SELECT 
    l.id,
    l.timestamp,
    u.username,
    u.email,
    l.action,
    l.details
FROM log l
LEFT JOIN user u ON l.user_id = u.id
ORDER BY l.timestamp DESC;



-- ==============================================
-- TRIGGER'LAR (Kontroller)
-- ==============================================

-- Satış yapıldığında ilaç stoğunu otomatik düşüren trigger
CREATE TRIGGER update_stock_after_sale
AFTER INSERT ON sold
FOR EACH ROW
BEGIN
    UPDATE ilac 
    SET stok_miktari = stok_miktari - NEW.miktar 
    WHERE id = NEW.ilac_id;
END;

-- İlaç stok kontrolü için trigger (satış öncesi kontrol)
CREATE TRIGGER check_stock_before_sale
BEFORE INSERT ON sold
FOR EACH ROW
WHEN (SELECT stok_miktari FROM ilac WHERE id = NEW.ilac_id) < NEW.miktar
BEGIN
    SELECT RAISE(ABORT, 'Stok yetersiz');
END;

-- Settings tablosu güncellendiğinde updated_at'i otomatik güncelleyen trigger
CREATE TRIGGER update_settings_timestamp
AFTER UPDATE ON settings
BEGIN
    UPDATE settings SET updated_at = CURRENT_TIMESTAMP WHERE id = 1;
END;
