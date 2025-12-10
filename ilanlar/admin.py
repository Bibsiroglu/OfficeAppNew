
import json
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Ilan, Musteri, PotansiyelMusteri, Randevu 


def fiyat_goster(obj):
    """Fiyatı Türkçe para birimi formatında gösterir."""
    try:
        return f"{obj.fiyat:,.0f} TL"
    except (TypeError, ValueError):
        return "N/A"
fiyat_goster.short_description = "Fiyat"


def durum_kontrol(obj):
    """İlan durumuna göre renkli ikon döndürür."""
    if obj.durum == 'Aktif':
        return mark_safe('<span style="color: green;">Aktif</span>')
    return mark_safe('<span style="color: red;">Pasif</span>')
durum_kontrol.short_description = "Durum"

@admin.register(Musteri)

class MusteriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'telefon')
    search_fields = ('ad', 'soyad', 'telefon')

class IlanAdmin(admin.ModelAdmin):
    list_display = (
        'ilan_no', 'baslik', 'fiyat_goster', 'ana_kategori', 'il', 'mahalle', 'durum_kontrol', 'musteri' # 'musteri' alanı artık düzgün çalışmalı
    )
    list_filter = ('ana_kategori', 'durum', 'krediye_uygun', 'tapu_durumu')
    search_fields = ('ilan_no', 'baslik', 'il', 'ilce', 'mahalle', 'site_adi')
    radio_fields = {"ana_kategori": admin.HORIZONTAL}

    fieldsets = [
        ('Temel ve İlan Bilgileri', {
            # 'musteri' alanı buraya eklendi
            'fields': ('ilan_no', 'baslik', 'durum', 'musteri', 'ilan_tarihi', 'yayindan_kaldirilma_tarihi'), 
        }),
        ('Kategori ve İşlem Tipi', {
            'fields': ('ana_kategori', 'detay_kategori', 'islem_tipi'),
        }),
        ('Fiyat ve Alan Ölçüleri (Tüm İlanlar Ortak)', {
            'fields': ('fiyat', 'brut', 'net', 'otopark_durumu', 'asansor'), 
        }),
        ('Konum Bilgisi', {
            'fields': ('il', 'ilce', 'mahalle', 'adres'), 
        }),
        ('Konut İlanına Ait Ek Bilgiler', {
            'fields': ('kat_sayisi', 'bulundugu_kat', 'banyo_sayisi', 'bina_yasi', 'mutfak_tipi', 'isitma_tipi', 'esyali', 'site_icerisinde', 'site_adi', 'kullanim_durumu', 'tapu_durumu', 'krediye_uygun', 'kimden', 'takas'),
        }),
        ('Arazi İlanına Ait Ek Bilgiler', {'fields': ('imar_durumu', 'm2', 'm2_fiyati', 'ada_no', 'parsel_no')}),
    ]
@admin.register(PotansiyelMusteri)
class PotansiyelMusteriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'telefon', 'ilgili_ilan')
    search_fields = ('ad', 'soyad', 'telefon', 'ilgili_ilan__ilan_no')

@admin.register(Randevu)
class RandevuAdmin(admin.ModelAdmin):
    # list_display, search_fields ve fields/fieldsets'i düzeltin
    
    list_display = ('ilan', 'potansiyel_musteri', 'tarih_saat', 'durum')
    
    fields = (
        'ilan', 
        'potansiyel_musteri', # <-- Sadece Foreign Key'i kullanın
        'tarih_saat', 
        'durum', 
        'notlar'
    )
    
    # search_fields de PotansiyelMusteri'ye yönlendirilmelidir:
    search_fields = ('potansiyel_musteri__soyad', 'potansiyel_musteri__telefon')

admin.site.register(Ilan, IlanAdmin)