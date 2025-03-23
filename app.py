# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from flask_babel import Babel, gettext as _
from sqlalchemy.orm import joinedload
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sotecai-gizli-anahtar')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sotecai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

# Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'tr'
app.config['BABEL_SUPPORTED_LOCALES'] = ['tr', 'en']
babel = Babel(app)
app.jinja_env.add_extension('jinja2.ext.i18n')

db = SQLAlchemy(app)

# Language selection function
def get_locale():
    # Check URL parameter
    lang = request.args.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = lang
        return lang
    # Check session
    elif 'lang' in session:
        return session['lang']
    # Default to Turkish
    return 'tr'

# Assign the function directly instead of using a decorator
babel.locale_selector_func = get_locale

import requests
import os
import json

def ai_servis_cagir(soru, dil='tr'):
    """
    AI servisi ile iletişim kurup cevap alan fonksiyon
    API anahtarı yoksa veya hata durumunda basit yanıtlarla çalışır
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    print(f"API anahtarı var mı: {'Evet' if api_key else 'Hayır'}")
    
    # Basit yanıtlar her durumda çalışır
    try:
        # API anahtarı yoksa basit yanıtlarla devam et
        if not api_key:
            print("API anahtarı olmadığı için basit yanıt döndürülüyor")
            return basit_cevap_uret(soru, dil)
        
        # Yazılım testi konusunda özel bilgi içeren prompt
        if dil == 'tr':
            sistem_mesaji = """Sen SotecAI'nin yazılım test uzmanı sanal asistanı Bilgecan'sın. 
            Yazılım testi, test otomasyonu, kalite güvence, CI/CD ve DevOps konularında uzmansın.
            İnsanlara yazılım test süreçleri, araçları ve en iyi uygulamalar hakkında yardımcı oluyorsun.
            Cevapların kısa, net ve bilgilendirici olmalı.
            Konuyla ilgili pratik öneriler ve çözümler sunmaya çalış."""
        else:
            sistem_mesaji = """You are Bilgecan, the software testing virtual assistant of SotecAI.
            You are an expert in software testing, test automation, quality assurance, CI/CD, and DevOps.
            You help people with software testing processes, tools, and best practices.
            Your answers should be concise, clear, and informative.
            Try to provide practical suggestions and solutions about the topic."""
        
        try:
            # Claude API çağrısı
            print("Claude API çağrısı yapılıyor...")
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "system": sistem_mesaji,
                    "messages": [
                        {"role": "user", "content": soru}
                    ],
                    "max_tokens": 500
                },
                timeout=15
            )
            
            print(f"API yanıt durumu: {response.status_code}")
            result = response.json()
            return result['content'][0]['text']
        
        except Exception as e:
            print(f"Claude API hatası: {str(e)}")
            return basit_cevap_uret(soru, dil)
    
    except Exception as e:
        print(f"Genel AI servis hatası: {str(e)}")
        # Herhangi bir durumda basit yanıtlar ile geri dön
        return basit_cevap_uret(soru, dil)

def basit_cevap_uret(soru, dil='tr'):
    """
    API bağlantısı olmadığında veya hata durumunda basit yanıtlar döndürür
    """
    print(f"Basit cevap üretiliyor. Soru: {soru[:30]}...")
    
    # Soru içeriğine göre anahtar kelime ve yanıtlar
    anahtar_kelimeler = {
        'selenium': {
            'tr': 'Selenium, web uygulamalarını test etmek için kullanılan popüler bir araçtır. Tarayıcı otomasyonu sağlar ve birçok programlama diliyle kullanılabilir.',
            'en': 'Selenium is a popular tool for testing web applications. It provides browser automation and can be used with many programming languages.'
        },
        'api test': {
            'tr': 'API testleri, yazılım bileşenleri arasındaki iletişimi doğrulamak için önemlidir. Postman, REST Assured gibi araçlar kullanabilirsiniz.',
            'en': 'API testing is crucial for verifying communication between software components. You can use tools like Postman, REST Assured.'
        },
        'performans': {
            'tr': 'Performans testleri için JMeter, Gatling gibi araçlar kullanabilirsiniz. Yük testi, stres testi ve dayanıklılık testi gibi farklı türleri vardır.',
            'en': 'For performance testing, you can use tools like JMeter, Gatling. There are different types such as load testing, stress testing, and endurance testing.'
        },
        'test otomasyonu': {
            'tr': 'Test otomasyonu, tekrarlayan testleri otomatikleştirerek zaman kazandırır. Framework seçimi, bakım maliyetleri ve test kapsamını dengelemelisiniz.',
            'en': 'Test automation saves time by automating repetitive tests. You should balance framework selection, maintenance costs, and test coverage.'
        },
        'merhaba': {
            'tr': 'Merhaba! Ben Bilgecan, yazılım testi konusunda sorularınızı yanıtlamak için buradayım. Size nasıl yardımcı olabilirim?',
            'en': 'Hello! I am Bilgecan, here to answer your questions about software testing. How can I help you?'
        },
        'pytest': {
            'tr': 'Pytest, Python için en popüler test frameworklerinden biridir. Basit sözdizimi, zengin eklenti ekosistemi ve test fixture\'ları ile bilinir.',
            'en': 'Pytest is one of the most popular testing frameworks for Python. It is known for its simple syntax, rich plugin ecosystem, and test fixtures.'
        },
        'ci/cd': {
            'tr': 'CI/CD (Sürekli Entegrasyon/Sürekli Dağıtım), yazılım geliştirme süreçlerini otomatikleştiren bir yaklaşımdır. Jenkins, GitLab CI, GitHub Actions gibi araçları kullanabilirsiniz.',
            'en': 'CI/CD (Continuous Integration/Continuous Delivery) is an approach that automates software development processes. You can use tools like Jenkins, GitLab CI, GitHub Actions.'
        }
    }
    
    soru_kucuk = soru.lower()
    
    # Soru içeriğine göre anahtar kelime taraması
    for kelime, cevaplar in anahtar_kelimeler.items():
        if kelime.lower() in soru_kucuk:
            return cevaplar[dil]
    
    # Eşleşme bulunamazsa genel yanıt
    genel_yanitlar = {
        'tr': [
            "Yazılım testi hakkında sorularınızı yanıtlamaktan memnuniyet duyarım. Daha spesifik bir soru sorabilir misiniz?",
            "Yazılım kalite süreçleri hakkında bilgi almak için daha açık bir soru sormanız yardımcı olabilir.",
            "Test otomasyonu, manuel test, performans testi veya güvenlik testi gibi belirli bir alan hakkında soru sorabilirsiniz.",
            "Size yardımcı olmak için buradayım. Selenium, JUnit, TestNG, Cypress gibi test araçları hakkında sorular sorabilirsiniz."
        ],
        'en': [
            "I'm happy to answer your questions about software testing. Could you ask a more specific question?",
            "For information about software quality processes, asking a more specific question would be helpful.",
            "You can ask about specific areas like test automation, manual testing, performance testing, or security testing.",
            "I'm here to help. You can ask questions about testing tools like Selenium, JUnit, TestNG, or Cypress."
        ]
    }
    
    # Rastgele bir genel yanıt seç
    import random
    return random.choice(genel_yanitlar[dil])

@app.route('/set_language/<language>')
def set_language(language):
    if language in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = language
    return redirect(request.referrer or url_for('anasayfa'))

# Database Models with optimized indexing
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    parola_hash = db.Column(db.String(200), nullable=False)
    kayit_tarihi = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def parola_ayarla(self, parola):
        self.parola_hash = generate_password_hash(parola)
        
    def parola_dogrula(self, parola):
        return check_password_hash(self.parola_hash, parola)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False, index=True)
    icerik = db.Column(db.Text, nullable=False)
    yazar_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), index=True)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ozet = db.Column(db.String(300))
    etiketler = db.Column(db.String(200), index=True)
    
    # Relationship for efficient querying
    yazar = db.relationship('Kullanici', backref='blogs')

class Yorum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), index=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), index=True)
    icerik = db.Column(db.Text, nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    blog = db.relationship('Blog', backref='yorumlar')
    kullanici = db.relationship('Kullanici', backref='yorumlar')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)  # Anonim kullanıcılar için
    soru = db.Column(db.Text, nullable=False)
    cevap = db.Column(db.Text, nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # İlişki
    kullanici = db.relationship('Kullanici', backref='chat_mesajlari')

class Arac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False, index=True)
    aciklama = db.Column(db.Text, nullable=False)
    kategori = db.Column(db.String(50), index=True)
    link = db.Column(db.String(200))

class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False, index=True)
    icerik = db.Column(db.Text, nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), index=True)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    etiketler = db.Column(db.String(200), index=True)
    
    # Relationship
    kullanici = db.relationship('Kullanici', backref='forum_postlari')

# Optimize sample data insertion with bulk operations
def ornek_veriler_ekle():
    # Add admin user if it doesn't exist
    if not Kullanici.query.filter_by(email='admin@sotecai.com').first():
        admin = Kullanici(ad='Admin', soyad='SotecAI', email='admin@sotecai.com')
        admin.parola_ayarla('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Add sample blogs if none exist
    if Blog.query.count() == 0:
        bloglar = [
            {
                'baslik': 'Test Otomasyonunda En Yeni Trendler',
                'ozet': 'Yazılım test otomasyonunda öne çıkan yeni teknolojiler ve yaklaşımlar hakkında kapsamlı bir inceleme.',
                'icerik': """
                <p>Günümüzde yazılım test otomasyonu sürekli gelişiyor ve yeni yaklaşımlar, araçlar ortaya çıkıyor. Bu yazıda, test otomasyonundaki en son trendleri ve bunların yazılım kalitesine etkilerini inceleyeceğiz.</p>
                
                <h3>Yapay Zeka ve Makine Öğrenmesi Destekli Test</h3>
                <p>Yapay zeka ve makine öğrenmesi teknolojileri, test süreçlerini daha akıllı hale getiriyor. Özellikle test senaryolarının otomatik olarak oluşturulması, test veri setlerinin optimize edilmesi ve hata tahminleme konularında büyük ilerlemeler kaydediliyor.</p>
                
                <h3>Düşük Kod/Kodsuz Test Araçları</h3>
                <p>Artık teknik olmayan ekip üyeleri bile karmaşık test senaryoları oluşturabiliyor. Düşük kod platformları, test süreçlerini demokratikleştiriyor ve tüm ekibin kalite süreçlerine dahil olmasını sağlıyor.</p>
                
                <h3>Sürekli Test ve DevOps Entegrasyonu</h3>
                <p>CI/CD (Sürekli Entegrasyon/Sürekli Dağıtım) süreçleriyle tam entegre test otomasyonu, yazılım geliştirme yaşam döngüsünün ayrılmaz bir parçası haline geldi. Bu entegrasyon, hataların erken tespit edilmesini ve daha hızlı geri bildirim döngülerini mümkün kılıyor.</p>
                
                <h3>Mikroservis Mimarisi için Test Yaklaşımları</h3>
                <p>Mikroservis mimarisinin yaygınlaşmasıyla birlikte, test stratejileri de değişiyor. Servisler arası iletişimin test edilmesi, servis virtualleştirme ve kaos mühendisliği gibi yaklaşımlar daha fazla önem kazanıyor.</p>
                
                <h3>Mobil ve IoT Test Otomasyonu</h3>
                <p>Mobil uygulamalar ve IoT cihazlarının yaygınlaşmasıyla birlikte, bu platformlar için özelleştirilmiş test araçları ve yaklaşımları da gelişiyor. Gerçek cihaz çiftlikleri ve bulut tabanlı test ortamları standart hale geliyor.</p>
                """,
                'etiketler': 'otomasyon,yapay zeka,devops,mikroservis,mobil,trend',
                'yazar_id': 1
            },
            {
                'baslik': 'Etkili API Testi Nasıl Yapılır?',
                'ozet': 'Modern yazılım mimarilerinin temel taşı olan API\'lerin test edilmesine dair kapsamlı bir rehber.',
                'icerik': """
                <p>Modern yazılım sistemlerinin çoğu API'ler üzerine kurulu ve bunların doğru çalışması kritik önem taşıyor. Bu yazıda, etkili API testi için adım adım bir yaklaşım sunacağız.</p>
                
                <h3>API Testinin Önemi</h3>
                <p>API'ler, farklı yazılım bileşenleri arasındaki iletişimi sağlar ve sisteminizin omurgasını oluşturur. Bir API hatası, tüm sistemin çökmesine yol açabilir. Etkili API testi, bu riskleri minimize etmenize yardımcı olur.</p>
                
                <h3>API Test Seviyeleri</h3>
                <ul>
                    <li><strong>Birim Testleri:</strong> Tek bir API endpoint'inin izole olarak test edilmesi</li>
                    <li><strong>Entegrasyon Testleri:</strong> Birden fazla API'nin birlikte çalışmasının test edilmesi</li>
                    <li><strong>Uçtan Uca Testler:</strong> Kullanıcı senaryolarını tam olarak simüle eden API çağrıları zinciri</li>
                </ul>
                
                <h3>API Testinde Temel Kontrol Noktaları</h3>
                <ol>
                    <li>Doğru HTTP durum kodları dönüyor mu?</li>
                    <li>Yanıt formatı ve şeması beklenen gibi mi?</li>
                    <li>Hata durumları doğru şekilde ele alınıyor mu?</li>
                    <li>Performans kriterleri karşılanıyor mu?</li>
                    <li>Güvenlik açıkları var mı?</li>
                </ol>
                
                <h3>API Test Araçları</h3>
                <p>Postman, SoapUI, REST Assured, JMeter gibi araçlar API testlerini otomatize etmenize yardımcı olabilir. Bu araçlar, test senaryolarınızı kolayca oluşturmanıza, çalıştırmanıza ve raporlamanıza olanak tanır.</p>
                
                <h3>API Test Otomasyonu İyi Uygulamaları</h3>
                <ul>
                    <li>Test verilerinizi dinamik olarak oluşturun</li>
                    <li>Bağımlılıkları mock servisler ile simüle edin</li>
                    <li>Test senaryolarınızı parametrize edin</li>
                    <li>İdempotent testler yazın (tekrar çalıştırılabilir)</li>
                    <li>CI/CD pipeline'ınıza entegre edin</li>
                </ul>
                """,
                'etiketler': 'api,rest,soap,entegrasyon,otomasyon,postman',
                'yazar_id': 1
            },
            {
                'baslik': 'Test Veri Yönetimi: Zorluklar ve Çözümler',
                'ozet': 'Etkili test için doğru verilerin yönetimi ve oluşturulması konusunda pratik ipuçları.',
                'icerik': """
                <p>Test veri yönetimi, başarılı bir test stratejisinin en kritik bileşenlerinden biridir. Doğru, çeşitli ve gerçekçi test verileri olmadan, testlerinizin etkinliği önemli ölçüde azalır.</p>
                
                <h3>Test Veri Yönetiminde Karşılaşılan Zorluklar</h3>
                <ul>
                    <li>Veri gizliliği ve KVKK/GDPR gibi düzenlemeler</li>
                    <li>Büyük veri kümeleriyle çalışma</li>
                    <li>Test ortamları arasında veri senkronizasyonu</li>
                    <li>Farklı test senaryoları için veri çeşitliliği sağlama</li>
                    <li>Test verisinin güncel tutulması</li>
                </ul>
                
                <h3>Etkili Test Veri Yönetimi Stratejileri</h3>
                
                <h4>1. Veri Maskeleme ve Anonimleştirme</h4>
                <p>Üretim verilerini test ortamlarında kullanırken, hassas bilgileri maskelemek veya anonimleştirmek için araçlar ve süreçler oluşturun.</p>
                
                <h4>2. Test Veri Oluşturma</h4>
                <p>Gerçekçi test verileri oluşturmak için özel araçlar kullanın. Bu araçlar, belirli kurallara ve sınırlamalara göre rastgele ancak anlamlı veriler üretebilir.</p>
                
                <h4>3. Veri Alt Kümesi Oluşturma</h4>
                <p>Büyük üretim veri kümeleriyle çalışırken, anlamlı bir alt küme oluşturmak test süreçlerini hızlandırabilir.</p>
                
                <h4>4. Veri-Odaklı Test Yaklaşımı</h4>
                <p>Test senaryolarınızı, farklı veri profillerine göre organize edin ve her bir profil için temsili örnekler kullanın.</p>
                
                <h3>Test Veri Yönetimi Araçları</h3>
                <p>IBM InfoSphere Optim, Delphix, Datprof gibi araçlar, test veri yönetimi süreçlerinizi otomatikleştirmenize yardımcı olabilir.</p>
                
                <h3>Sonuç</h3>
                <p>Etkili test veri yönetimi, test süreçlerinizin kalitesini ve güvenilirliğini önemli ölçüde artırır. Doğru stratejiler ve araçlarla, test veri yönetimindeki zorlukların üstesinden gelebilir ve daha kapsamlı test senaryoları oluşturabilirsiniz.</p>
                """,
                'etiketler': 'veri,maskeleme,otomasyon,gdpr,kvkk,strateji',
                'yazar_id': 1
            },
            {
                'baslik': 'Yazılım Test Otomasyonunda Python Kullanımı',
                'ozet': 'Python\'un test otomasyonundaki gücünü keşfedin ve yaygın kullanılan Python test frameworklerini öğrenin.',
                'icerik': """
                <p>Python, basit sözdizimi, zengin kütüphane ekosistemi ve çok yönlülüğü sayesinde test otomasyonu için mükemmel bir seçimdir. Bu yazıda, Python'un test otomasyonundaki kullanımını ve popüler frameworkleri inceleyeceğiz.</p>
                
                <h3>Python'un Test Otomasyonundaki Avantajları</h3>
                <ul>
                    <li>Öğrenmesi kolay, okunabilir sözdizimi</li>
                    <li>Platform bağımsız çalışma</li>
                    <li>Zengin test kütüphane ekosistemi</li>
                    <li>Hem web hem de API testleri için uygun</li>
                    <li>Veri işleme ve analizi için güçlü yetenekler</li>
                </ul>
                
                <h3>Popüler Python Test Frameworkleri</h3>
                
                <h4>1. Pytest</h4>
                <p>Pytest, Python test dünyasında en popüler frameworklerden biridir. Basit testler için minimalist bir API sunarken, karmaşık senaryolar için de genişletilebilir bir yapı sağlar.</p>
                <pre><code>
import pytest

def test_ekleme():
    assert 1 + 1 == 2
    
def test_cikarma():
    assert 3 - 1 == 2
                </code></pre>
                
                <h4>2. Robot Framework</h4>
                <p>Robot Framework, kabul testleri ve test odaklı geliştirme için kullanılan anahtar kelime tabanlı bir test otomasyon frameworküdür. Python ile yazılmış olsa da, test senaryoları düz metin formatında yazılır ve teknik olmayan ekip üyeleri tarafından da anlaşılabilir.</p>
                <pre><code>
*** Test Cases ***
Toplama İşlemi
    ${sonuc}=    Topla    1    2
    Should Be Equal    ${sonuc}    3

*** Keywords ***
Topla
    [Arguments]    ${a}    ${b}
    ${sonuc}=    Evaluate    ${a} + ${b}
    [Return]    ${sonuc}
                </code></pre>
                
                <h4>3. Behave (BDD)</h4>
                <p>Behave, Cucumber'a benzer şekilde Davranış Odaklı Geliştirme (BDD) yaklaşımını benimseyen bir test frameworküdür. Gherkin sözdizimini kullanarak doğal dil senaryoları yazmanıza olanak tanır.</p>
                <pre><code>
# hesap.feature
Feature: Hesap İşlemleri
  Scenario: İki sayının toplanması
    Given İlk sayı 5
    And İkinci sayı 7
    When Bu sayılar toplandığında
    Then Sonuç 12 olmalıdır
                </code></pre>
                
                <h4>4. Selenium ve Python</h4>
                <p>Selenium WebDriver, Python ile web uygulamalarının otomatize edilmesi için popüler bir araçtır. Selenium'un Python API'si, web elementlerini bulma, tıklama, form doldurma gibi temel web etkileşimlerini otomatize etmenizi sağlar.</p>
                <pre><code>
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.example.com")

arama_kutusu = driver.find_element(By.ID, "search")
arama_kutusu.send_keys("test otomasyon")
arama_kutusu.submit()

assert "test otomasyon" in driver.title
driver.quit()
                </code></pre>
                
                <h3>Python Test Otomasyonu İyi Uygulamaları</h3>
                <ul>
                    <li>Page Object Model (POM) kullanarak UI testlerinizi yapılandırın</li>
                    <li>Test verilerinizi test kodundan ayırın</li>
                    <li>Pytest fixtures ile test kurulumunu ve temizliğini yönetin</li>
                    <li>Paralel test çalıştırma için pytest-xdist kullanın</li>
                    <li>Düzenli CI/CD pipeline entegrasyonu sağlayın</li>
                </ul>
                """,
                'etiketler': 'python,selenium,pytest,bdd,otomasyon,robot framework',
                'yazar_id': 1
            }
        ]
        
        # Bulk insert blogs
        db.session.bulk_insert_mappings(Blog, bloglar)
        db.session.commit()
    
    # Add sample tools if none exist
    if Arac.query.count() == 0:
        araclar = [
            {
                'ad': 'Selenium',
                'aciklama': 'Web uygulamalarının otomatize edilmesi için açık kaynaklı bir araçtır. Çeşitli programlama dilleriyle birlikte kullanılabilir.',
                'kategori': 'Web Otomasyon',
                'link': 'https://www.selenium.dev/'
            },
            {
                'ad': 'JMeter',
                'aciklama': 'Apache JMeter, web uygulamalarının yük ve performans testleri için kullanılan açık kaynaklı bir Java uygulamasıdır.',
                'kategori': 'Performans Testi',
                'link': 'https://jmeter.apache.org/'
            },
            {
                'ad': 'Postman',
                'aciklama': 'API geliştirme ve test etme için kullanılan popüler bir araçtır. API istekleri oluşturma, otomatize etme ve paylaşma imkanı sunar.',
                'kategori': 'API Testi',
                'link': 'https://www.postman.com/'
            },
            {
                'ad': 'Appium',
                'aciklama': 'Mobil uygulamaların (iOS, Android) test otomasyonu için açık kaynaklı bir araçtır.',
                'kategori': 'Mobil Test',
                'link': 'https://appium.io/'
            },
            {
                'ad': 'PyTest',
                'aciklama': 'Python için basit ve ölçeklenebilir bir test frameworküdür. Birim testlerinden fonksiyonel testlere kadar geniş bir yelpazede kullanılabilir.',
                'kategori': 'Test Framework',
                'link': 'https://docs.pytest.org/'
            },
            {
                'ad': 'TestNG',
                'aciklama': 'Java için tasarlanmış, JUnit\'in gelişmiş bir versiyonu olarak kabul edilen bir test frameworküdür.',
                'kategori': 'Test Framework',
                'link': 'https://testng.org/'
            },
            {
                'ad': 'SonarQube',
                'aciklama': 'Kod kalitesi ve güvenlik kontrolü için kullanılan bir platformdur. Kodunuzdaki hataları, güvenlik açıklarını ve kötü pratikleri tespit eder.',
                'kategori': 'Kod Kalitesi',
                'link': 'https://www.sonarqube.org/'
            },
            {
                'ad': 'Cucumber',
                'aciklama': 'Davranış Odaklı Geliştirme (BDD) yaklaşımını destekleyen, doğal dil senaryolarını otomatize testlere dönüştüren bir araçtır.',
                'kategori': 'BDD',
                'link': 'https://cucumber.io/'
            }
        ]
        
        # Bulk insert tools
        db.session.bulk_insert_mappings(Arac, araclar)
        db.session.commit()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'kullanici_id' not in session:
            flash(_('Bu sayfayı görüntülemek için giriş yapmalısınız.'), 'warning')
            return redirect(url_for('giris', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Before request handler to load current user
@app.before_request
def load_user():
    if 'kullanici_id' in session:
        g.user = Kullanici.query.get(session['kullanici_id'])
    else:
        g.user = None

# Routes with optimization for database queries
@app.route('/')
def anasayfa():
    # Efficient eager loading with joinedload
    son_bloglar = Blog.query.options(
        joinedload(Blog.yazar)
    ).order_by(Blog.tarih.desc()).limit(3).all()
    
    # Use subquery for distinct categories to improve performance
    kategoriler = db.session.query(Arac.kategori).distinct().all()
    kategoriler = [k[0] for k in kategoriler]
    
    return render_template('index.html', son_bloglar=son_bloglar, kategoriler=kategoriler)

@app.route('/hakkimizda')
def hakkimizda():
    return render_template('hakkimizda.html')

@app.route('/blog')
def blog_listesi():
    # Efficient eager loading
    bloglar = Blog.query.options(
        joinedload(Blog.yazar)
    ).order_by(Blog.tarih.desc()).all()
    
    return render_template('blog_listesi.html', bloglar=bloglar)

@app.route('/blog/<int:blog_id>')
def blog_detay(blog_id):
    # Get blog with author and comments in a single query
    blog = Blog.query.options(
        joinedload(Blog.yazar),
        joinedload(Blog.yorumlar).joinedload(Yorum.kullanici)
    ).get_or_404(blog_id)
    
    return render_template('blog_detay.html', blog=blog)

@app.route('/araclar')
def araclar():
    tum_araclar = Arac.query.all()
    kategoriler = db.session.query(Arac.kategori).distinct().all()
    kategoriler = [k[0] for k in kategoriler]
    
    return render_template('araclar.html', araclar=tum_araclar, kategoriler=kategoriler)

@app.route('/egitimler')
def egitimler():
    return render_template('egitimler.html')

@app.route('/iletisim', methods=['GET', 'POST'])
def iletisim():
    if request.method == 'POST':
        ad = request.form.get('ad')
        email = request.form.get('email')
        mesaj = request.form.get('mesaj')
        
        # Here you can implement email sending
        # For example with Flask-Mail
        
        flash(_('Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.'), 'success')
        return redirect(url_for('iletisim'))
        
    return render_template('iletisim.html')

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    # Redirect if already logged in
    if 'kullanici_id' in session:
        return redirect(url_for('anasayfa'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        parola = request.form.get('parola')
        
        kullanici = Kullanici.query.filter_by(email=email).first()
        if kullanici and kullanici.parola_dogrula(parola):
            session['kullanici_id'] = kullanici.id
            # Get next parameter or default to homepage
            next_page = request.args.get('next', url_for('anasayfa'))
            flash(_('Başarıyla giriş yaptınız!'), 'success')
            return redirect(next_page)
        else:
            flash(_('Geçersiz e-posta veya parola!'), 'danger')
    
    return render_template('giris.html')

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    # Redirect if already logged in
    if 'kullanici_id' in session:
        return redirect(url_for('anasayfa'))
        
    if request.method == 'POST':
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        email = request.form.get('email')
        parola = request.form.get('parola')
        parola_tekrar = request.form.get('parola_tekrar')
        
        if parola != parola_tekrar:
            flash(_('Parolalar eşleşmiyor!'), 'danger')
            return redirect(url_for('kayit'))
        
        # Check if email already exists
        if Kullanici.query.filter_by(email=email).first():
            flash(_('Bu e-posta adresi zaten kullanılıyor!'), 'danger')
            return redirect(url_for('kayit'))
        
        # Create new user
        yeni_kullanici = Kullanici(ad=ad, soyad=soyad, email=email)
        yeni_kullanici.parola_ayarla(parola)
        
        db.session.add(yeni_kullanici)
        db.session.commit()
        
        flash(_('Başarıyla kayıt oldunuz! Şimdi giriş yapabilirsiniz.'), 'success')
        return redirect(url_for('giris'))
    
    return render_template('kayit.html')

@app.route('/cikis')
def cikis():
    session.pop('kullanici_id', None)
    flash(_('Başarıyla çıkış yaptınız!'), 'success')
    return redirect(url_for('anasayfa'))

@app.route('/bilgecan')
def bilgecan_chat():
    return render_template('bilgecan.html')

@app.route('/api/bilgecan/mesaj', methods=['POST'])
def bilgecan_mesaj():
    """
    Basit test API'si - herhangi bir harici servise bağlı değil
    """
    print("API endpoint çağrıldı!")
    try:
        # Gelen veriyi al
        data = request.get_json()
        print("Gelen veri:", data)
        
        if not data:
            print("JSON verileri alınamadı")
            return jsonify({'cevap': 'Veri alınamadı. Lütfen geçerli bir JSON gönderiniz.'}), 400
        
        soru = data.get('soru', '')
        session_id = data.get('session_id', '')
        
        if not soru:
            return jsonify({'cevap': 'Lütfen bir soru sorun.'}), 400
        
        print(f"Soru alındı: {soru}, Session ID: {session_id}")
        
        # Basit yanıt oluştur - servis çağrılarıyla uğraşma
        basit_yanitlar = {
            'selam': 'Merhaba! Size nasıl yardımcı olabilirim?',
            'merhaba': 'Merhaba! Yazılım testi konusunda sorularınızı yanıtlamaya hazırım.',
            'test': 'Test otomasyonu, süreçlerinizi hızlandırmanın en iyi yollarından biridir. Selenium, Cypress, JUnit gibi araçlar kullanabilirsiniz.',
            'selenium': 'Selenium, web uygulamalarını test etmek için en popüler açık kaynak araçlarından biridir.',
            'python': 'Python, test otomasyonu için harika bir dildir. Pytest, Robot Framework gibi güçlü test frameworkleri sunar.',
            'api': 'API testleri için Postman, REST Assured veya Python\'da requests kütüphanesi kullanabilirsiniz.'
        }
        
        # Basit kelime eşleştirme yaparak yanıt oluştur
        yanit = "Sorunuzu aldım. İlgili konuda size şunları söyleyebilirim: "
        
        for anahtar, deger in basit_yanitlar.items():
            if anahtar.lower() in soru.lower():
                yanit = deger
                break
        else:
            yanit = "Yazılım testi hakkında nasıl yardımcı olabilirim? Örneğin, test otomasyonu, API testleri veya Selenium hakkında sorular sorabilirsiniz."
        
        # Veritabanına kaydedebiliriz - ancak bu isteğe bağlı
        try:
            kullanici_id = session.get('kullanici_id')
            yeni_mesaj = ChatMessage(
                kullanici_id=kullanici_id,
                session_id=session_id,
                soru=soru,
                cevap=yanit
            )
            db.session.add(yeni_mesaj)
            db.session.commit()
            print("Mesaj veritabanına kaydedildi")
        except Exception as e:
            print(f"Veritabanı hatası: {str(e)}")
            # Hata durumunda işlemi geri al ama yanıt vermeye devam et
            db.session.rollback()
        
        # API yanıtı
        return jsonify({'cevap': yanit})
        
    except Exception as e:
        print(f"API genel hatası: {str(e)}")
        return jsonify({'cevap': 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.'}), 500
# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Template context processor
@app.context_processor
def ortak_veriler():
    def kullanici_giris_yapti_mi():
        return 'kullanici_id' in session
    
    def mevcut_kullanici():
        if hasattr(g, 'user'):
            return g.user
        return None
    
    from datetime import datetime
    now = datetime.now()
    
    return {
        'kullanici_giris_yapti_mi': kullanici_giris_yapti_mi,
        'mevcut_kullanici': mevcut_kullanici(),
        'now': now,
        # Add translations for common phrases
        'tr_en': {
            'tr': {
                'anasayfa': 'Ana Sayfa',
                'hakkimizda': 'Hakkımızda',
                'blog': 'Blog',
                'araclar': 'Araçlar',
                'egitimler': 'Eğitimler',
                'iletisim': 'İletişim',
                'giris': 'Giriş',
                'cikis': 'Çıkış',
                'kayit': 'Üye Ol',
                'bilgecan': 'Bilgecan',
                'bilgecan_slogan': 'SotecAI\'nin yazılım test uzmanı sanal asistanı',
                'soru_sor': 'Bir soru sorun...',
                'gonder': 'Gönder',
                'dusunuyor': 'Bilgecan düşünüyor...',
                'hata': 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.'
            },
            'en': {
                'anasayfa': 'Home',
                'hakkimizda': 'About Us',
                'blog': 'Blog',
                'araclar': 'Tools',
                'egitimler': 'Training',
                'iletisim': 'Contact',
                'giris': 'Login',
                'cikis': 'Logout',
                'kayit': 'Sign Up',
                'bilgecan': 'Bilgecan',
                'bilgecan_slogan': 'SotecAI\'s software testing virtual assistant',
                'soru_sor': 'Ask a question...',
                'gonder': 'Send',
                'dusunuyor': 'Bilgecan is thinking...',
                'hata': 'Sorry, an error occurred. Please try again.'
            }
        }
    }

# Setup database and sample data
with app.app_context():
    db.create_all()
    ornek_veriler_ekle()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)  # Debug modunu zorla açık yapın