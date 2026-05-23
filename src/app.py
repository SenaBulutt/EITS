from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func, desc, inspect, text
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

# Uygulama Konfigürasyonu
app = Flask(__name__)
app.secret_key = "gizli-anahtar-degistirilmeli"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eczane.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
db = SQLAlchemy(app)



# --------------------
# Tarih Formatlama Filtresi
# --------------------
@app.template_filter('format_date')
def format_date(value):
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y")

    if "-" in value:
        try:
            y, m, d = value.split("-")
            return value.strftime("%d.%m.%Y %H:%M")
        except:
            return value
    return value

# ===============================================
# VERİTABANI MODELLERİ (SQL'E UYUMLU 7 TABLO)
# ===============================================

# 1. KULLANICI TABLOSU (USER)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    logs = db.relationship('Log', backref='user', lazy=True)
    sales = db.relationship('Sold', backref='satan_user', lazy=True)

# 2. KATEGORİ TABLOSU (KATEGORI)
class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kategori_adi = db.Column(db.String(100), unique=True, nullable=False)
    ilaclar = db.relationship('Ilac', backref='kategori', lazy=True)

# 3. FİRMA TABLOSU (FIRMA)
class Firma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firma_adi = db.Column(db.String(150), unique=True, nullable=False)
    ilaclar = db.relationship('Ilac', backref='firma', lazy=True)

# 4. HASTA TABLOSU (HASTA)
class Hasta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hasta_tc = db.Column(db.String(11), unique=True, nullable=False)
    hasta_ad = db.Column(db.String(100), nullable=False)
    hasta_soyad = db.Column(db.String(100), nullable=False)
    satislar = db.relationship('Sold', backref='hasta_kaydi', lazy=True)

# 5. İLAÇ TABLOSU (ILAC)
class Ilac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    aktif_bilesen = db.Column(db.String(100), nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    stok_miktari = db.Column(db.Integer, nullable=False)
    son_kullanma_tarihi = db.Column(db.String(20), nullable=False)
    
    # ✅ AÇIKLAMA (Dashboard Detaylar ile bağlantılı)
    aciklama = db.Column(db.Text)

    # İlişkiler (Foreign Keys)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'))
    firma_id = db.Column(db.Integer, db.ForeignKey('firma.id'))  # Firma FK
    
    # ✅ DÜZELTİLDİ: cascade="all, delete-orphan" yerine "save-update"
    sales = db.relationship('Sold', backref='ilac', lazy=True, cascade="save-update")

# 6. SATILAN İLAÇLAR TABLOSU (SOLD)
class Sold(db.Model):
    __tablename__ = 'sold'
    id = db.Column(db.Integer, primary_key=True)
    ilac_id = db.Column(db.Integer, db.ForeignKey('ilac.id'), nullable=True)  # True yap
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tarih_saat = db.Column(db.DateTime, default=datetime.utcnow)
    miktar = db.Column(db.Integer, nullable=False)
    # ⭐ YENİ: Satış anı fiyat snapshot'ı
    satis_fiyati = db.Column(db.Float, nullable=False)
    # Yarı-normalize alanlar (Metin) - BUNLAR ARTIK KALDIRILACAK
    # hasta_tc = db.Column(db.String(11), nullable=False)  # KALDIR
    # hasta_ad = db.Column(db.String(100), nullable=False) # KALDIR
    # hasta_soyad = db.Column(db.String(100), nullable=False) # KALDIR
    hasta_id = db.Column(db.Integer, db.ForeignKey('hasta.id'), nullable=False)  # ZORUNLU

# 7. LOG TABLOSU (LOG)
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(300))

# 8. SETTINGS TABLOSU (SETTINGS) - tek satır kullanacağız
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # hep 1 olsun

    # Genel
    eczane_ad = db.Column(db.String(150), default="Modern Eczanesi")
    telefon = db.Column(db.String(50), default="(0212) 123 45 67")
    vergi_no = db.Column(db.String(50), default="1234567890")
    adres = db.Column(db.Text, default="İstiklal Caddesi No:123 Beyoğlu/İstanbul")
    eposta = db.Column(db.String(150), default="info@modernezcanesi.com")
    calisma_saatleri = db.Column(db.String(150), default="08:00 - 22:00 (Her Gün)")

    # Tema
    theme_color = db.Column(db.String(30), default="75, 85, 99")  # "R, G, B"
    theme_dark = db.Column(db.String(20), default="#374151")
    theme_gradient = db.Column(db.String(120), default="linear-gradient(135deg, #9ca3af, #4b5563)")

    # Görünüm / Sistem
    kayit_sayisi = db.Column(db.Integer, default=25)
    zaman_dilimi = db.Column(db.String(50), default="İstanbul (GMT+3)")

    # Bildirim
    low_stock_notification = db.Column(db.Boolean, default=True)
    expiry_notification = db.Column(db.Boolean, default=True)
    email_notification = db.Column(db.Boolean, default=False)

    low_stock_threshold = db.Column(db.Integer, default=20)
    expiry_warning_days = db.Column(db.Integer, default=90)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 9. PASSWORD RESET TOKEN TABLOSU
class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='reset_tokens')

THEME_MAP = {
    '129, 140, 248': { 'dark': '#4f46e5', 'gradient': 'linear-gradient(135deg, #818cf8, #6366f1)' },
    '59, 130, 246':  { 'dark': '#2563eb', 'gradient': 'linear-gradient(135deg, #60a5fa, #3b82f6)' },
    '16, 185, 129':  { 'dark': '#059669', 'gradient': 'linear-gradient(135deg, #34d399, #10b981)' },
    '239, 68, 68':   { 'dark': '#b91c1c', 'gradient': 'linear-gradient(135deg, #f87171, #ef4444)' },
    '139, 92, 246':  { 'dark': '#7c3aed', 'gradient': 'linear-gradient(135deg, #a78bfa, #8b5cf6)' },
    '249, 115, 22':  { 'dark': '#c2410c', 'gradient': 'linear-gradient(135deg, #fb923c, #f97316)' },
    '75, 85, 99':    { 'dark': '#374151', 'gradient': 'linear-gradient(135deg, #9ca3af, #4b5563)' }  # ✅ EKLENDİ
}

def get_settings():
    s = Settings.query.get(1)
    if not s:
        s = Settings(id=1)
        db.session.add(s)
        db.session.commit()
    return s

@app.context_processor
def inject_settings():
    try:
        return dict(settings=get_settings())
    except Exception:
        return dict(settings=None)

# --------------------
# VERİTABANI MİGRASYON FONKSİYONU (2. GÖRSELE GÖRE)
# --------------------
def migrate_sold_table():
    """
    sold tablosunu 2. görsele göre güncelle
    """
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'sold' not in tables:
        print("⚠ sold tablosu henüz oluşturulmamış")
        return
    
    cols = [c['name'] for c in inspector.get_columns('sold')]
    
    # Eğer hasta_tc sütunu yoksa, tablo zaten güncel
    if 'hasta_tc' not in cols:
        print("✅ sold tablosu zaten güncel")
        return
    
    print("🔄 sold tablosu migrate ediliyor...")
    
    try:
        with db.engine.connect() as conn:
            # YENİ TABLO OLUŞTUR
            conn.execute(text("""
                CREATE TABLE sold_new (
                    id INTEGER PRIMARY KEY,
                    ilac_id INTEGER NOT NULL,
                    user_id INTEGER,
                    tarih_saat DATETIME,
                    miktar INTEGER NOT NULL,
                    satis_fiyati FLOAT NOT NULL DEFAULT 0,
                    hasta_id INTEGER NOT NULL,
                    FOREIGN KEY (ilac_id) REFERENCES ilac (id),
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (hasta_id) REFERENCES hasta (id)
                )
            """))
            
            # 1. ÖNCE hastaları hasta tablosuna ekle
            conn.execute(text("""
                INSERT OR IGNORE INTO hasta (hasta_tc, hasta_ad, hasta_soyad)
                SELECT DISTINCT s.hasta_tc, s.hasta_ad, s.hasta_soyad
                FROM sold s
                WHERE s.hasta_tc IS NOT NULL AND s.hasta_tc != ''
            """))
            
            # 2. SONRA verileri yeni tabloya taşı (TEK BİR INSERT)
            conn.execute(text("""
                INSERT INTO sold_new (id, ilac_id, user_id, tarih_saat, miktar, satis_fiyati, hasta_id)
                SELECT 
                    s.id,
                    s.ilac_id,
                    s.user_id,
                    s.tarih_saat,
                    s.miktar,
                    COALESCE((SELECT fiyat FROM ilac WHERE id = s.ilac_id), 0) as satis_fiyati,
                    COALESCE(
                        s.hasta_id,
                        (SELECT id FROM hasta WHERE hasta_tc = s.hasta_tc LIMIT 1),
                        (SELECT id FROM hasta WHERE hasta_ad = s.hasta_ad AND hasta_soyad = s.hasta_soyad LIMIT 1),
                        (SELECT id FROM hasta LIMIT 1),
                        1
                    ) as hasta_id
                FROM sold s
            """))
            
            # Eski tabloyu sil, yeni tabloyu adlandır
            conn.execute(text("DROP TABLE sold"))
            conn.execute(text("ALTER TABLE sold_new RENAME TO sold"))
            conn.commit()
            
            print("✅ sold tablosu başarıyla migrate edildi")
            
    except Exception as e:
        print(f"❌ Migrasyon hatası: {e}")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS sold_new"))
                conn.commit()
        except:
            pass
        raise

# --------------------
# İLAÇ TABLOSU MİGRASYON FONKSİYONU (uretici -> firma_id)
# --------------------
def migrate_ilac_table():
    """
    ilac tablosunu 2. görsele göre güncelle:
    1. uretici sütununu kaldır
    2. firma_id'yi NOT NULL yap ve mevcut verileri taşı
    """
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'ilac' not in tables:
        print("⚠ ilac tablosu henüz oluşturulmamış, migrasyon gerekli değil")
        return
    
    cols = [c['name'] for c in inspector.get_columns('ilac')]
    
    # Eğer uretici sütunu yoksa, zaten güncel
    if 'uretici' not in cols:
        print("✅ ilac tablosu zaten güncel (uretici sütunu yok)")
        return
    
    print("🔄 ilac tablosu migrate ediliyor...")
    
    try:
        with db.engine.connect() as conn:
            # 1. Önce tüm mevcut üreticileri firma tablosuna ekle
            conn.execute(text("""
                INSERT OR IGNORE INTO firma (firma_adi)
                SELECT DISTINCT uretici 
                FROM ilac 
                WHERE uretici IS NOT NULL AND uretici != ''
            """))
            
            # 2. Firma tablosundaki kayıtlarla eşleştir
            conn.execute(text("""
                UPDATE ilac 
                SET firma_id = (SELECT id FROM firma WHERE firma_adi = ilac.uretici LIMIT 1)
                WHERE firma_id IS NULL AND uretici IS NOT NULL AND uretici != ''
            """))
            
            # 3. Eğer hala firma_id NULL ise, varsayılan bir firma ata
            conn.execute(text("""
                UPDATE ilac 
                SET firma_id = (SELECT id FROM firma LIMIT 1)
                WHERE firma_id IS NULL
            """))
            
            # 4. Yeni tablo oluştur (uretici sütunu olmadan)
            conn.execute(text("""
                CREATE TABLE ilac_new (
                    id INTEGER PRIMARY KEY,
                    ad TEXT NOT NULL,
                    aktif_bilesen TEXT NOT NULL,
                    fiyat REAL NOT NULL,
                    stok_miktari INTEGER NOT NULL,
                    son_kullanma_tarihi TEXT NOT NULL,
                    aciklama TEXT,
                    kategori_id INTEGER NOT NULL,
                    firma_id INTEGER NOT NULL,
                    FOREIGN KEY (kategori_id) REFERENCES kategori(id),
                    FOREIGN KEY (firma_id) REFERENCES firma(id)
                )
            """))
            
            # 5. Verileri yeni tabloya kopyala
            conn.execute(text("""
                INSERT INTO ilac_new (id, ad, aktif_bilesen, fiyat, stok_miktari, 
                                     son_kullanma_tarihi, aciklama, kategori_id, firma_id)
                SELECT id, ad, aktif_bilesen, fiyat, stok_miktari, 
                       son_kullanma_tarihi, aciklama, kategori_id, 
                       COALESCE(firma_id, (SELECT id FROM firma LIMIT 1))
                FROM ilac
            """))
            
            # 6. Eski tabloyu sil, yeni tabloyu adlandır
            conn.execute(text("DROP TABLE ilac"))
            conn.execute(text("ALTER TABLE ilac_new RENAME TO ilac"))
            
            conn.commit()
            print("✅ ilac tablosu başarıyla migrate edildi")
            
    except Exception as e:
        print(f"❌ ilac migrasyon hatası: {e}")
        raise

# --------------------
# LOG EKLEME FONKSİYONU
# --------------------
def add_log(action, details=""):
    user_id = session.get("user_id")

    yeni_log = Log(
        user_id=user_id,
        action=action,
        timestamp=datetime.now(),
        details=details
    )
    db.session.add(yeni_log)
    db.session.commit()

# --------------------
# E-POSTA FONKSİYONU
# --------------------
# E-posta gönderme fonksiyonunu güncelle
def send_reset_email(to_email, username, reset_code):
    """Basit e-posta gönderme (Gmail için) - KOD versiyonu"""
    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USERNAME = "KENDI_GMAIL_ADRESINIZ@gmail.com"  # DEĞİŞTİR
        SMTP_PASSWORD = "KENDI_GMAIL_APP_SIFRENIZ"      # DEĞİŞTİR (Google App Password)
        
        msg = MIMEMultipart()
        msg['From'] = f"EİTS <{SMTP_USERNAME}>"
        msg['To'] = to_email
        msg['Subject'] = "EİTS - Şifre Sıfırlama Kodu"
        
        body = f"""
        <h3>Merhaba {username},</h3>
        <p>Şifrenizi sıfırlamak için aşağıdaki kodu kullanın:</p>
        <div style="background:#f3f4f6; padding:20px; border-radius:10px; text-align:center; font-size:32px; font-weight:bold; letter-spacing:5px; margin:20px 0;">
            {reset_code}
        </div>
        <p>Bu kod 10 dakika geçerlidir.</p>
        <p>Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelin.</p>
        <hr>
        <p><small>Eczane İlaç Takip Sistemi</small></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"E-posta hatası: {e}")
        return False




# Şifre sıfırlama route'larını güncelle
@app.route('/reset_request', methods=['POST'])
def reset_request():
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    
    user = User.query.filter_by(username=username, email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'})
    
    # 6 haneli kod oluştur
    reset_code = str(secrets.randbelow(900000) + 100000)  # 100000-999999 arası
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 dakika
    
    # Eski token'ları temizle
    PasswordResetToken.query.filter_by(user_id=user.id).delete()
    
    # Yeni token
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=reset_code,  # Artık token yerine kod
        expires_at=expires_at
    )
    db.session.add(reset_token)
    db.session.commit()
    
    if send_reset_email(user.email, user.username, reset_code):
        return jsonify({'success': True, 'message': 'Şifre sıfırlama kodu e-postanıza gönderildi!'})
    else:
        return jsonify({'success': False, 'error': 'E-posta gönderilemedi'})

@app.route('/reset_password_page_final')
def reset_password_page_final():
    """Yeni şifre sayfası"""
    if not session.get('reset_user_id') or not session.get('reset_token'):
        return redirect(url_for('reset_page'))
    
    return render_template('reset_password_page_final.html')



# ===============================================
# FLASK ROUTE'LARI
# ===============================================
@app.route('/get_hasta_by_tc', methods=['POST'])
def get_hasta_by_tc():
    """TC'ye göre hasta bilgilerini getir"""
    hasta_tc = request.form.get('hasta_tc', '').strip()
    
    if not hasta_tc or len(hasta_tc) != 11 or not hasta_tc.isdigit():
        return jsonify({'success': False, 'error': 'Geçersiz TC No'})
    
    hasta = Hasta.query.filter_by(hasta_tc=hasta_tc).first()
    
    if hasta:
        return jsonify({
            'success': True,
            'hasta_ad': hasta.hasta_ad,
            'hasta_soyad': hasta.hasta_soyad
        })
    else:
        return jsonify({'success': False, 'message': 'Yeni hasta'})

# --------------------
# Login, Logout, Register, Reset
# --------------------
@app.route('/')
def index():
    if session.get("user_id"):
        return redirect(url_for('menu'))

    remembered_username = request.cookies.get("remember_username", "")
    return render_template('login.html', remembered_username=remembered_username)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    remember = request.form.get('remember')  # "on" veya None

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session.permanent = bool(remember)  # ✅ kalıcı oturum

        add_log("Giriş", f"Kullanıcı giriş yaptı: {username}")

        resp = make_response(redirect(url_for('menu')))

        if remember:
            resp.set_cookie(
                "remember_username",
                username,
                max_age=30*24*60*60,
                httponly=True,
                samesite="Lax"
            )
        else:
            resp.delete_cookie("remember_username")

        return resp

    return render_template('login.html', error="Kullanıcı adı veya şifre hatalı", remembered_username=username)

@app.route("/logout")
def logout():
    add_log("Çıkış", "Kullanıcı çıkış yaptı")
    session.clear()
    return redirect(url_for('index'))

@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/reset_page')
def reset_page():
    return render_template('reset.html')


# ⬇⬇⬇ BURAYA EKLE ⬇⬇⬇
@app.route('/reset_password_page')
def reset_password_page():
    """Kod doğrulama sayfası"""
    return render_template('reset_verify.html')
# ⬆⬆⬆ BURAYA EKLE ⬆⬆⬆
# ⬇⬇⬇ HEMEN ALTINA EKLE ⬇⬇⬇
# 1. KOD DOĞRULAMA ROUTE'U (zaten var, güncelleyin)
@app.route('/verify_reset_code', methods=['POST'])
def verify_reset_code():
    """6 haneli kodu doğrula - DÜZELTİLMİŞ"""
    reset_code = request.form.get('reset_code', '').strip()
    
    if len(reset_code) != 6 or not reset_code.isdigit():
        return jsonify({'success': False, 'error': 'Geçersiz kod formatı'})
    
    reset_token = PasswordResetToken.query.filter_by(
        token=reset_code, 
        used=False
    ).first()
    
    if not reset_token:
        return jsonify({'success': False, 'error': 'Geçersiz veya kullanılmış kod'})
    
    if reset_token.expires_at < datetime.utcnow():
        db.session.delete(reset_token)
        db.session.commit()
        return jsonify({'success': False, 'error': 'Kodun süresi dolmuş'})
    
    # Session'a kaydet
    session['reset_user_id'] = reset_token.user_id
    session['reset_token'] = reset_code
    
    return jsonify({'success': True, 'message': 'Kod doğrulandı!'})

# 2. YENİ ŞİFRE SAYFASI ROUTE'U (TEK BİR TANE OLSUN)


# 3. YENİ ŞİFRE KAYDETME ROUTE'U
@app.route('/reset_password_final', methods=['POST'])
def reset_password_final():
    """Yeni şifre kaydet"""
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    user_id = session.get('reset_user_id')
    reset_code = session.get('reset_token')
    
    if not user_id or not reset_code:
        return render_template('reset_password_page_final.html', 
                             error="Oturum süresi doldu. Lütfen baştan başlayın.")
    
    if new_password != confirm_password:
        return render_template('reset_password_page_final.html', 
                             error="Şifreler uyuşmuyor!")
    
    if len(new_password) < 6:
        return render_template('reset_password_page_final.html', 
                             error="Şifre en az 6 karakter olmalı!")
    
    reset_token = PasswordResetToken.query.filter_by(
        user_id=user_id, 
        token=reset_code, 
        used=False
    ).first()
    
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        session.pop('reset_user_id', None)
        session.pop('reset_token', None)
        return render_template('reset_password_page_final.html', 
                             error="Geçersiz veya süresi dolmuş kod.")
    
    # Şifreyi güncelle
    user = User.query.get(user_id)
    user.password = generate_password_hash(new_password)
    reset_token.used = True
    
    db.session.commit()
    
    # Session'ı temizle
    session.pop('reset_user_id', None)
    session.pop('reset_token', None)
    
    add_log("Şifre Sıfırlama", f"{user.username} şifresini sıfırladı")
    
    return redirect(url_for('index', success="Şifreniz başarıyla güncellendi! Giriş yapabilirsiniz."))
@app.route('/register', methods=['POST'])
def register():
    new_username = request.form['new_username'].strip()
    email = request.form['email'].strip()
    new_password = request.form['new_password']

    if not new_username or not email:
        return render_template('register.html', error="Tüm alanlar zorunludur.")

    if len(new_password) < 6:
        return render_template('register.html', error="Şifre en az 6 karakter olmalıdır.")

    if User.query.filter_by(username=new_username).first():
        return render_template('register.html', error="Bu kullanıcı zaten var!")

    if User.query.filter_by(email=email).first():
        return render_template('register.html', error="Bu e-posta zaten kayıtlı!")

    hashed_password = generate_password_hash(new_password)
    new_user = User(
        username=new_username,
        email=email,
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    add_log("Kayıt Olma", f"{new_username} ({email})")
    return redirect(url_for('index'))

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.form['username_reset'].strip()
    new_password = request.form['new_password_reset']

    if len(new_password) < 6:
        return render_template('reset.html', error="Yeni şifre en az 6 karakter olmalıdır.")

    user = User.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        add_log("Şifre Sıfırlama", f"Kullanıcı şifresi değişti: {username}")
        return redirect(url_for('index'))
    else:
        return render_template('reset.html', error="Kullanıcı bulunamadı!")





# --------------------
# Anasayfa (Menu) - GÜNCELLENDİ
# --------------------
@app.route('/menu')
def menu():
    user_id = session.get("user_id")

    current_user = User.query.get(user_id)
    if not current_user:
        return redirect(url_for('logout'))

    last_login_log = Log.query.filter_by(user_id=user_id, action="Giriş") \
                              .order_by(desc(Log.timestamp)).first()

    user_info = {
        'username': current_user.username,
        'initial': current_user.username[0].upper() if current_user.username else 'A',
        'last_login': last_login_log.timestamp.strftime("%d.%m.%Y %H:%M:%S") if last_login_log else 'N/A'
    }

    total_drugs = Ilac.query.count()
    s = get_settings()
    low_threshold = s.low_stock_threshold if s else 20
    low_stock_count = Ilac.query.filter(Ilac.stok_miktari <= low_threshold).count()

    # ✅ EKSİK OLAN: expiring_soon_count HESAPLA
    today = datetime.now().date()
    expiry_days = s.expiry_warning_days if s else 90
    ninety_days_later = today + timedelta(days=expiry_days)
    
    all_drugs = Ilac.query.all()
    expiring_soon_count = 0
    for drug in all_drugs:
        if drug.son_kullanma_tarihi:
            try:
                day, month, year = map(int, drug.son_kullanma_tarihi.split('.'))
                expiry_date = datetime(year, month, day).date()
                if today <= expiry_date <= ninety_days_later:
                    expiring_soon_count += 1
            except:
                continue

    # 90 GÜN İÇİNDE BİTECEK İLAÇLARI HESAPLA
    today = datetime.now().date()
    expiry_days = s.expiry_warning_days if s else 90
    ninety_days_later = today + timedelta(days=expiry_days)
  
    
    all_drugs = Ilac.query.all()
    expiring_soon_count = 0
    for drug in all_drugs:
        if drug.son_kullanma_tarihi:
            try:
                day, month, year = map(int, drug.son_kullanma_tarihi.split('.'))
                expiry_date = datetime(year, month, day).date()
                
                if today <= expiry_date <= ninety_days_later:
                    expiring_soon_count += 1
            except:
                continue

    # BUGÜNKÜ SATIŞLARI HESAPLA (Türkiye saati ile UTC+3)
    # UTC+3 saat farkını hesaba kat
    turkey_time_now = datetime.utcnow() + timedelta(hours=3)
    today_turkey = turkey_time_now.date()
    
    # Bugünkü satışlar
    sales_today = Sold.query.filter(
        func.date(Sold.tarih_saat) == today_turkey
    ).all()
    
    total_sales_today = 0
    for s in sales_today:
        total_sales_today += s.miktar * s.satis_fiyati  # ← 4 BOŞLUK İÇERDE!

    # DÜNKÜ SATIŞLARI HESAPLA
    yesterday_turkey = today_turkey - timedelta(days=1)
    
    sales_yesterday = Sold.query.filter(
        func.date(Sold.tarih_saat) == yesterday_turkey
    ).all()
    
    total_sales_yesterday = 0
    for s in sales_yesterday:
        total_sales_yesterday += s.miktar * s.satis_fiyati  # ← 4 BOŞLUK İÇERDE!
        
    # YÜZDELİK DEĞİŞİMİ HESAPLA
    if total_sales_yesterday > 0:
        sales_change_percentage = ((total_sales_today - total_sales_yesterday) / total_sales_yesterday) * 100
    else:
        sales_change_percentage = 0

    # EN ÇOK SATAN İLAÇLAR
    top_selling = (
        db.session.query(Ilac.ad, func.sum(Sold.miktar).label('total_miktar'))
        .join(Sold)
        .group_by(Ilac.ad)
        .order_by(desc('total_miktar'))
        .limit(5)
        .all()
    )

    context = {
        'user_info': user_info,
        'summary': {
            'total_drugs': total_drugs,
            'expiring_soon': expiring_soon_count,
            'low_stock': low_stock_count,
            'today_sales': f"{total_sales_today:.2f}",  # Format: "55.00"
            'sales_change_percentage': sales_change_percentage,  # Yüzdelik değişim
        },
        'top_selling': [{'name': item.ad, 'count': item.total_miktar} for item in top_selling]
    }

    return render_template('menu.html', **context)

# --------------------
# Dashboard
# --------------------
@app.route('/dashboard')
def dashboard():
    tab = request.args.get('tab', 'list')
    
    drugs_query = Ilac.query.options(
        db.joinedload(Ilac.kategori), 
        db.joinedload(Ilac.firma)
    )
    drugs = drugs_query.all()
     # Fiyatları formatla (virgülü noktaya çevir)
    for drug in drugs:
        if isinstance(drug.fiyat, str):
            drug.fiyat = drug.fiyat.replace(',', '.')
        # Float'a çevir
        try:
            drug.fiyat = float(drug.fiyat)
        except:
            drug.fiyat = 0.0
    
    logs = []
    logs_paginated = None
    
    if tab == 'users':
        # PAGINATION DÜZGÜN KAPATILMIŞ HALİ
        s = get_settings()
        per_page = s.kayit_sayisi if s else 25
        page = request.args.get('page', 1, type=int)
        
        logs_query = db.session.query(Log, User.username, User.email) \
                               .join(User, Log.user_id == User.id) \
                               .order_by(desc(Log.timestamp))
        
        logs_paginated = logs_query.paginate(page=page, per_page=per_page, error_out=False)
        
        logs = [{
            'user_name': log[1],
            'email': log[2],
            'action': log[0].action,
            'details': log[0].details,
            'timestamp': log[0].timestamp.strftime("%d.%m.%Y %H:%M")
        } for log in logs_paginated.items]
    
    s = get_settings()
    low_threshold = s.low_stock_threshold if s else 20
    low_stock = [d for d in drugs if d.stok_miktari <= low_threshold]

    return render_template(
        'dashboard.html',
        active_tab=tab,
        drugs=drugs,
        low_stock=low_stock,
        logs=logs,
        logs_paginated=logs_paginated if tab == 'users' else None,
        settings=s 
    )

# --------------------
# İlaç Ekle / Güncelle (✅ aciklama dahil)
# --------------------
@app.route('/add_update', methods=['POST'])
def add_update():
    ilac_id = request.form.get('ilac_id')
    ad = request.form['ad']
    aktif_bilesen = request.form['aktif_bilesen']
    fiyat = float(request.form['fiyat'])
    stok_miktari = int(request.form['stok_miktari'])
    son_kullanma_tarihi = request.form['son_kullanma_tarihi']

    firma_adi = request.form['firma'].strip()
    kategori_adi = request.form['kategori'].strip()

    # ✅ Dashboard Detaylar'daki açıklama buradan geliyor:
    aciklama = request.form.get('aciklama', '').strip()

    kategori = Kategori.query.filter(func.lower(Kategori.kategori_adi) == func.lower(kategori_adi)).first()
    if not kategori:
        kategori = Kategori(kategori_adi=kategori_adi)
        db.session.add(kategori)
        db.session.commit()

    firma = Firma.query.filter(func.lower(Firma.firma_adi) == func.lower(firma_adi)).first()
    if not firma:
        firma = Firma(firma_adi=firma_adi)
        db.session.add(firma)
        db.session.commit()

    if ilac_id:
        ilac = Ilac.query.get(int(ilac_id))
        if ilac:
            ilac.ad = ad
            ilac.aktif_bilesen = aktif_bilesen
            ilac.fiyat = fiyat
            ilac.stok_miktari = stok_miktari
            ilac.son_kullanma_tarihi = son_kullanma_tarihi
            ilac.firma_id = firma.id
            ilac.kategori_id = kategori.id

            # ✅ AÇIKLAMA GÜNCELLE
            ilac.aciklama = aciklama

            add_log("İlaç Güncelleme", f"Güncellenen ilaç: {ad}")
    else:
        ilac = Ilac(
            ad=ad,
            aktif_bilesen=aktif_bilesen,
            fiyat=fiyat,
            stok_miktari=stok_miktari,
            son_kullanma_tarihi=son_kullanma_tarihi,
            firma_id=firma.id,
            kategori_id=kategori.id,

            # ✅ AÇIKLAMA KAYDET
            aciklama=aciklama
        )
        db.session.add(ilac)
        add_log("İlaç Ekleme", f"Yeni ilaç eklendi: {ad}")

    db.session.commit()
    return redirect(url_for('dashboard', tab='list'))

# --------------------
# İlaç Silme
# --------------------
@app.route('/delete_dropdown', methods=['POST'])
def delete_dropdown():
    ilac_id = request.form.get('ilac_id')
    if ilac_id:
        ilac = Ilac.query.get(int(ilac_id))
        if ilac:
            try:
                # ÖNCE: Bu ilaca ait satışların ilac_id'sini NULL yap
                satislar = Sold.query.filter_by(ilac_id=ilac_id).all()
                for satis in satislar:
                    satis.ilac_id = None  # NULL yap
                
                # SONRA: İlacı sil
                add_log("İlaç Silme", f"Silinen ilaç: {ilac.ad}")
                db.session.delete(ilac)
                db.session.commit()
                
                return redirect(url_for('dashboard', tab='delete', 
                                       success=f"{ilac.ad} başarıyla silindi. Satış kayıtları korundu."))
                
            except Exception as e:
                db.session.rollback()
                return redirect(url_for('dashboard', tab='delete', error=f"Silme hatası: {str(e)}"))
    
    return redirect(url_for('dashboard', tab='delete'))

# --------------------
# İlaç Satma
# --------------------
@app.route('/sell_dropdown', methods=['POST'])
def sell_dropdown():
    ilac_id = int(request.form['ilac_id'])

    hasta_tc = request.form['hasta_tc'].strip()
    hasta_ad = request.form['hasta_ad'].strip()
    hasta_soyad = request.form['hasta_soyad'].strip()

    miktar = int(request.form['miktar'])

    ilac = Ilac.query.get(ilac_id)

    if ilac.stok_miktari < miktar:
        error_msg = f"Stok yetersiz! {ilac.ad} için mevcut stok: {ilac.stok_miktari}."
        return redirect(url_for('dashboard', tab='sell', error=error_msg))

    hasta_kaydi = Hasta.query.filter_by(hasta_tc=hasta_tc).first()
    if not hasta_kaydi:
        hasta_kaydi = Hasta(hasta_tc=hasta_tc, hasta_ad=hasta_ad, hasta_soyad=hasta_soyad)
        db.session.add(hasta_kaydi)
        db.session.commit()

    ilac.stok_miktari -= miktar

    from datetime import datetime, timedelta
    
    turkey_time = datetime.utcnow() + timedelta(hours=3)

    sold_item = Sold(
        ilac_id=ilac.id,
        user_id=session.get('user_id'),
        miktar=miktar,
        satis_fiyati=ilac.fiyat,  # ⭐ YENİ: Snapshot fiyat
        hasta_id=hasta_kaydi.id,  # Sadece hasta_id
        tarih_saat=turkey_time
    )

    db.session.add(sold_item)
    add_log("İlaç Satış", f"{miktar} adet {ilac.ad} satıldı ({hasta_tc})")
    db.session.commit()

    return redirect(url_for('dashboard', tab='sell'))

# --------------------
# Satılan İlaçları Sil
# --------------------
@app.route('/delete_sold/<int:id>', methods=['POST'])
def delete_sold(id):
    sold_item = Sold.query.get(id)
    if sold_item:
        add_log("Satış Silme", f"Satış kaydı silindi: {sold_item.id}")
        db.session.delete(sold_item)
        db.session.commit()
    return redirect(url_for('sold_list'))

# --------------------
# Satılan İlaçlar Listesi
# --------------------
@app.route('/sold')
def sold_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Satılan ilaçları getir
    sold_drugs = Sold.query.order_by(Sold.tarih_saat.desc()).all()
    
    # Tarih formatını düzenle
    for sold in sold_drugs:
        if sold.tarih_saat:
            # Datetime objesini string'e çevir
            sold.formatted_date = sold.tarih_saat.strftime("%d.%m.%Y")  # 21.12.2025
            sold.formatted_time = sold.tarih_saat.strftime("%H:%M")  # 22:31
        else:
            sold.formatted_date = ""
            sold.formatted_time = ""
    
    return render_template('sold.html', sold_drugs=sold_drugs)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    s = get_settings()

    # Genel
    s.eczane_ad = request.form.get('eczane_ad', s.eczane_ad).strip()
    s.telefon = request.form.get('telefon', s.telefon).strip()
    s.vergi_no = request.form.get('vergi_no', s.vergi_no).strip()
    s.adres = request.form.get('adres', s.adres).strip()
    s.eposta = request.form.get('eposta', s.eposta).strip()
    s.calisma_saatleri = request.form.get('calisma_saatleri', s.calisma_saatleri).strip()

    # Tema
    theme_color = request.form.get('theme_color', s.theme_color).strip()
    s.theme_color = theme_color
    colors = THEME_MAP.get(theme_color)
    if colors:
        s.theme_dark = colors['dark']
        s.theme_gradient = colors['gradient']

    # Görünüm
    ks = request.form.get('kayit_sayisi', str(s.kayit_sayisi))
    # String'den integer'a çevir (sadece sayıları al)
    s.kayit_sayisi = int(ks) if ks.isdigit() else s.kayit_sayisi
    
    s.zaman_dilimi = request.form.get('zaman_dilimi', s.zaman_dilimi)

    # Bildirimler (checkbox'lar "on" döner yoksa None)
    s.low_stock_notification = request.form.get('low_stock_notification') == 'on'
    s.expiry_notification = request.form.get('expiry_notification') == 'on'
    s.email_notification = request.form.get('email_notification') == 'on'

    # Eşikler
    low_threshold = request.form.get('low_stock_threshold', s.low_stock_threshold)
    expiry_days = request.form.get('expiry_warning_days', s.expiry_warning_days)
    
    s.low_stock_threshold = int(low_threshold) if low_threshold and low_threshold.isdigit() else s.low_stock_threshold
    s.expiry_warning_days = int(expiry_days) if expiry_days and expiry_days.isdigit() else s.expiry_warning_days

    db.session.commit()
    return redirect(url_for('dashboard', tab='settings', success="Ayarlar kaydedildi"))

# --------------------
# Uygulama Başlatma
# --------------------
def ensure_aciklama_column():
    """
    SQLite için mini migrasyon:
    ilac tablosunda aciklama sütunu yoksa ekler.
    """
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'ilac' not in tables:
        return

    cols = [c['name'] for c in inspector.get_columns('ilac')]
    if 'aciklama' not in cols:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE ilac ADD COLUMN aciklama TEXT"))
            conn.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # ✅ CRITICAL: Settings tablosu oluştur
        if not Settings.query.first():
            default_settings = Settings(id=1)
            db.session.add(default_settings)
            db.session.commit()
            print("✅ Varsayılan ayarlar eklendi")

        # ✅ Eğer eski db varsa aciklama sütununu otomatik ekle
        ensure_aciklama_column()

        # ✅ 2. görsele göre sold tablosunu migrate et
        try:
            migrate_sold_table()
        except Exception as e:
            print(f"⚠ Migrasyon hatası (tablo zaten güncel olabilir): {e}")
            
        # ✅ ilac tablosunu 2. görsele göre migrate et (uretici -> firma_id)
        try:
            migrate_ilac_table()
        except Exception as e:
            print(f"⚠ ilac migrasyon hatası: {e}")

        # ✅ YENİ: PasswordResetToken tablosunu kontrol et
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'password_reset_token' not in tables:
                PasswordResetToken.__table__.create(db.engine)
                print("✅ PasswordResetToken tablosu oluşturuldu")
            else:
                print("✅ PasswordResetToken tablosu zaten var")
        except Exception as e:
            print(f"⚠ Token tablosu hatası: {e}")

        # Admin ve Örnek Veri Ekleme (ilk çalıştırmada)
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('123456')
            admin_user = User(
                username='admin',
                email='admin@gmail.com',
                password=hashed_password
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin kullanıcısı oluşturuldu")

        print("="*50)
        print("📧 E-POSTA ŞİFRE SIFIRLAMA SİSTEMİ AKTİF!")
        print("E-posta gönderimi için:")
        print("1. send_reset_email() fonksiyonundaki e-posta bilgilerini kontrol edin")
        print("2. Gmail App Password doğru mu kontrol edin")
        print("="*50)

    app.run(host='0.0.0.0', port=5005, debug=False, threaded=True)
