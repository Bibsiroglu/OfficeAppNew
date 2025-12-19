# ilanlar/models.py

from django.db import models
from datetime import date
from django.utils import timezone # Gerekli
from django.utils.safestring import mark_safe

# --- SABİT SEÇENEK LİSTELERİ ---
KULLANIM_DURUMLARI_SECENEKLERI = [
    ('boş', 'Boş'),
    ('oturuluyor', 'Oturuluyor'),
    ('kirada', 'Kirada'),
    ('tadilatta', 'Tadilatta'),
]

ISLEM_TIPI_SECENEKLERI = [
    ('satilik', 'Satılık'),
    ('kiralik', 'Kiralık'),
]

TAPU_DURUMU_SECENEKLERI = [
    ('kat_mulkiyeti', 'Kat Mülkiyeti'),
    ('kat_irtifaki', 'Kat İrtifakı'),
    ('hisseli', 'Hisseli Tapu'),
    ('mustakil', 'Müstakil Tapu (Arsa)'),
    ('tahsis', 'Tahsis'),
]

IMAR_DURUMU_SECENEKLERI = [
    ('konut_imari', 'Konut İmarlı'),
    ('ticari_imari', 'Ticari İmarlı'),
    ('sanayi_imari', 'Sanayi İmarlı'),
    ('tarim', 'Tarım/Ziraat Alanı'),
    ('imar_yok', 'İmar Yok'),
    ('karma', 'Karma Kullanım'),
]

OTOPARK_SECENEKLERI = [
    ('yok', 'Yok'),
    ('acik', 'Açık Otopark'),
    ('kapali', 'Kapalı Otopark'),
    ('acik_kapali', 'Açık ve Kapalı'),
]

MUTFAK_SECENEKLERI = [
    ('kapali', 'Kapalı Mutfak'),
    ('acik', 'Açık Mutfak (Amerikan)'),
    ('ayrilmis', 'Ayrılmış Mutfak'),
    ('yok', 'Mutfak Yok'),
]

ISITMA_SECENEKLERI = [
    ('kombi', 'Kombi (Doğalgaz)'),
    ('merkezi', 'Merkezi Sistem'),
    ('payolcer', 'Merkezi (Pay Ölçer)'),
    ('klima', 'Klima'),
    ('soba', 'Soba/Katı Yakıt'),
    ('yok', 'Isıtma Yok/Diğer'),
]

ODA_SAYISI_SECENEKLERI = [
    ('Stüdyo', '1+0 Stüdyo'),
    ('1+1', '1+1'),
    ('2+1', '2+1'),
    ('3+1', '3+1'),
    ('4+1', '4+1'),
    ('5+1', '5+1 ve Üzeri'),
    ('6+', '6+ ve Daha Büyük'),
    ('Acik', 'Açık Alan'),
    ('1 Bölme', '1 Bölme'),
    ('2 Bölme', '2 Bölme'), 
    ('3 Bölme', '3 Bölme'),
    ('4 Bölme', '4 Bölme'),
    ('5 Bölme', '5 Bölme ve Üzeri'),
]

ANA_KATEGORILER_SECENEKLERI = [
    ('konut','Konut'),
    ('isyeri', 'İş Yeri'),
    ('arsa', 'Arsa'),
    ('diger', 'Diğer')
]

DETAY_KATEGORI_SECENEKLERI = [
    # Konut Seçenekleri
    ('daire', 'Daire'),
    ('villa', 'Villa'),
    ('mustakil', 'Müstakil Ev'),
    
    # İş Yeri Seçenekleri
    ('dukkan', 'Dükkan'),
    ('ofis', 'Ofis'),
    ('fabrika', 'Fabrika'),
    ('depo', 'Depo'),
    
    # Arsa Seçenekleri
    ('tarla', 'Tarla'),
    ('bahce', 'Bahçe'),
    
    # Diğer
    ('baska', 'Belirtilmemiş / Başka'),
]

PASIF_NEDENLERI = [
    ('Satildi', 'Satıldı'),
    ('Kiralandi', 'Kiralandı'),
    ('Yayin_Suresi_Bitti', 'Yayın Süresi Bitti'),
    ('Kadirildi', 'Kullanıcı Tarafından Kaldırıldı')
]
class Ajanda(models.Model):

    DURUM_SECENEKLERI = [
        ('Bekliyor', 'Bekliyor'),
        ('Tamamlandi', 'Tamamlandı'),
        ('İptal Edildi', 'İptal Edildi')
    ]

    ONCELIK_SECENEKLERI = [
        ('1', 'Düşük'),
        ('2', 'Orta'),
        ('3', 'Yüksek')
    ]
    baslik = models.CharField(max_length=200, verbose_name="Görev Başlığı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    tarih = models.DateTimeField(verbose_name="Görev Tarihi ve Saati")
    oncelik = models.CharField(max_length=1, choices=ONCELIK_SECENEKLERI, default='2', verbose_name="Öncelik")
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='Bekliyor', verbose_name="Durum")

    class Meta:
        verbose_name = "Görev"
        verbose_name_plural = "Ajanda / Görevler"
        ordering = ['tarih']

    def __str__(self):
        return self.baslik
    
class Ilan(models.Model):
    DURUM_SECENEKLERI = [
        ('Aktif', 'Aktif'), 
        ('Pasif', 'Pasif')
    ]
    yayindan_kaldirilma_tarihi = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Yayından Kaldırılma Tarihi"
    )
    musteri = models.ForeignKey(
        'Musteri', # Model sınıfına işaret eder
        on_delete=models.SET_NULL, # İlan silinirse müşteri kaybolmasın
        null=True, 
        blank=True, 
        related_name='ilanlar',
        verbose_name="İlan Sahibi"
    )
    il = models.CharField(
        max_length=50, 
        verbose_name="İl (Şehir)",
        help_text="Zorunlu Alan. Örn: İstanbul, Kastamonu"
    )
    ilce = models.CharField(
        max_length=50, 
        verbose_name="İlçe",
        help_text="Zorunlu Alan. Örn: Merkez, Beşiktaş"
    )
    mahalle = models.CharField(
        max_length=100, 
        verbose_name="Mahalle/Semt",
        help_text="Örn: Saraçlar Mh."
    )
    adres = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Açık Adres Detayı",
        help_text="Detaylı adres bilgisi (site içi, blok, kat vb.)"
    )
    islem_tipi = models.CharField(
        max_length=10,
        choices=ISLEM_TIPI_SECENEKLERI,
        default='satilik', # Varsayılan olarak satılık seçilebilir
        verbose_name="İşlem Tipi"
    )
    ilan_no = models.CharField(max_length=20, unique=True, verbose_name="İlan No")
    baslik = models.CharField(max_length=150, verbose_name="İlan Başlığı")
    
    # Tarih (Sadece Gün)
    ilan_tarihi = models.DateField(
        default=date.today,
        verbose_name='İlan Kayıt Tarihi'
    )
    
    # Kategoriler (Dinamik Filtreleme için anahtarlar)
    ana_kategori = models.CharField(
        max_length=10,
        choices=ANA_KATEGORILER_SECENEKLERI,
        default='konut',
        verbose_name='Mülk Tipi'
    )
    detay_kategori = models.CharField(
        max_length=10,
        choices=DETAY_KATEGORI_SECENEKLERI,
        default='daire',
        verbose_name='Mülk Alt Tipi'
    )
    
    # Diğer Temel Alanlar (KONUT)
    fiyat = models.DecimalField(
    max_digits=15, 
    decimal_places=2, # Emlakta virgülden sonra 2 basamak (kuruş) yeterlidir
    verbose_name="Fiyat"
)
    brut = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, verbose_name="Brüt Alan (m²)")
    net = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Net Alan (m²)")
    oda_sayisi = models.CharField(
        max_length=10, 
        choices=ODA_SAYISI_SECENEKLERI, # <-- Seçenek listesi atandı
        default='2+1',
        verbose_name="Oda Sayısı"
    )
    bina_yasi = models.IntegerField(null=True, blank=True, verbose_name="Bina Yaşı")
    bulundugu_kat = models.CharField(max_length=10, null=True, blank=True, verbose_name="Bulunduğu Kat")
    kat_sayisi = models.IntegerField(null=True, blank=True, verbose_name="Kat Sayısı")
    isitma_tipi = models.CharField(
        max_length=20, 
        choices=ISITMA_SECENEKLERI,
        default='kombi',
        verbose_name="Isıtma Tipi"
    )
    banyo_sayisi = models.IntegerField(null=True, blank=True, verbose_name="Banyo Sayısı")
    mutfak_tipi = models.CharField(
        max_length=10, 
        choices=MUTFAK_SECENEKLERI,
        default='kapali',
        verbose_name="Mutfak Tipi"
    )
    balkon = models.BooleanField(default=False, verbose_name="Balkon")
    asansor = models.BooleanField(default=False, verbose_name="Asansör")
    otopark_durumu = models.CharField(
        max_length=15, 
        choices=OTOPARK_SECENEKLERI,
        default='yok',
        verbose_name="Otopark Durumu"
    )
    esyali = models.BooleanField(default=False, verbose_name="Eşyalı")
    kullanim_durumu = models.CharField(
    max_length=50, 
    choices=KULLANIM_DURUMLARI_SECENEKLERI, 
    default='Boş',
    verbose_name="Kullanım Durumu"
    )
    site_icerisinde = models.BooleanField(default=False, verbose_name="Site İçerisinde")
    site_adi = models.CharField(max_length=100, null=True, blank=True, verbose_name="Site Adı")
    aidat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Aidat")
    krediye_uygun = models.BooleanField(default=False, verbose_name="Krediye Uygun")
    tapu_durumu = models.CharField(
        max_length=20, 
        choices=TAPU_DURUMU_SECENEKLERI,
        default='kat_mulkiyeti',
        verbose_name="Tapu Durumu (Mülkiyet)"
    )
    kimden = models.CharField(max_length=50, null=True, blank=True, verbose_name="İlan Sahibi")
    takas = models.BooleanField(default=False, verbose_name="Takas")
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='Aktif', verbose_name="Durum")
    pasif_nedeni = models.CharField(
        max_length=50, 
        choices=PASIF_NEDENLERI, 
        verbose_name="Pasif Nedeni",
        null=True,
        blank=True,
    )
    # Diğer Temel Alanlar (ARAZİ)
    imar_durumu = models.CharField(
        max_length=20, 
        choices=IMAR_DURUMU_SECENEKLERI,
        default='imar_yok',
        verbose_name="İmar Durumu"
    )
    m2 =models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Alan (m²)")
    m2_fiyati = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="m² Fiyatı")
    ada_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ada No")
    parsel_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Parsel No")

    def save(self, *args, **kwargs):
        # Eğer ilan durumu AKTIF ise, pasif nedenini otomatik olarak temizle
        if self.durum == 'Aktif':
            self.pasif_nedeni = ""
        super(Ilan, self).save(*args, **kwargs)

    def net_alan_orani(self):
        """Net alanın brüt alana oranını hesaplar (Yüzde olarak)."""
        if self.brut and self.net and self.brut > 0:
            oran = (self.net / self.brut) * 100
            return f"%{oran:.1f}"
        return "N/A"

    net_alan_orani.short_description = "Net/Brüt Oranı"

    def fiyat_goster(self):
        """Fiyatı Türkçe para birimi formatında gösterir."""
        try:
            return f"{self.fiyat:,.0f} TL"
        except (ValueError, TypeError):
            return "Fiyat Belirtilmemiş"
    fiyat_goster.short_description = "Fiyat"

    def durum_kontrol(self):
        """İlan durumuna göre renkli ikon ve pasif ise nedenini döndürür."""
        if self.durum == 'Aktif':
            return mark_safe('<span style="color: green; font-weight: bold;">🟢 Aktif</span>')
        elif self.durum == 'Pasif':
            neden_label = self.get_pasif_nedeni_display()
            aciklama = f"Neden: {neden_label}" if self.pasif_nedeni else "Neden Belirtilmemiş"
                
            return mark_safe(f'<span style="color: red;">🔴 Pasif</span> - <small>{aciklama}</small>')
        return self.durum
    durum_kontrol.short_description = "Durum"
    
    def __str__(self):
        return f"{self.ilan_no} - {self.baslik}"
        
    class Meta:
        verbose_name = "İlan"
        verbose_name_plural = "İlanlar"
        ordering = ['-ilan_tarihi']
    

class Musteri(models.Model):
    ad = models.CharField(max_length=50, verbose_name="Ad")
    soyad = models.CharField(max_length=50, verbose_name="Soyad")
    telefon = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    
    def __str__(self):
        return f"{self.ad} {self.soyad} {self.telefon}"
    
    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"

class PotansiyelMusteri(models.Model):
    # Bu modelin içeriğini sabit tutuyoruz
    ad = models.CharField(max_length=50, verbose_name="Ad")
    soyad = models.CharField(max_length=50, verbose_name="Soyad")
    telefon = models.CharField(max_length=20, verbose_name="Telefon Numarası", unique=True)
    ilgili_ilan = models.ForeignKey(
        'Ilan', on_delete=models.SET_NULL, null=True, blank=True, related_name='leads', verbose_name="İlgili İlan"
    )
    
    def __str__(self):
        return f"{self.ad} {self.soyad} ({self.telefon})"
    
    class Meta:
        verbose_name = "Potansiyel Müşteri"
        verbose_name_plural = "Potansiyel Müşteriler"


class Randevu(models.Model):
    DURUM_SECENEKLERI = [ ('PLAN', 'Planlandı'), ('TAMAM', 'Tamamlandı'), ('IPTAL', 'İptal Edildi') ]
    
    # --- KRİTİK DEĞİŞİKLİK: Foreign Key eklendi, iletişim alanları kaldırıldı ---
    
    # Randevuyu PotansiyelMusteri'ye bağlar
    potansiyel_musteri = models.ForeignKey( 
        PotansiyelMusteri, 
        on_delete=models.CASCADE, 
        related_name='randevular', 
        verbose_name="Randevu Alan Kişi"
    )
    
    # Randevunun hangi ilanla ilgili olduğunu tutar
    ilan = models.ForeignKey(
        'Ilan', on_delete=models.CASCADE, related_name='randevular', verbose_name="İlgili İlan"
    )

    tarih_saat = models.DateTimeField(default=timezone.now, verbose_name="Randevu Tarihi ve Saati")
    durum = models.CharField(max_length=5, choices=DURUM_SECENEKLERI, default='PLAN', verbose_name="Durum")
    notlar = models.TextField(blank=True, null=True, verbose_name="Ek Notlar/Detaylar")

    class Meta:
        verbose_name = "Randevu"
        verbose_name_plural = "Randevular"

    def __str__(self):
        # Randevu alan müşterinin adını gösterir
        return f"{self.potansiyel_musteri.ad} - {self.ilan.ilan_no} Randevusu"