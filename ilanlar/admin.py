
import json
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Ilan, Musteri, PotansiyelMusteri, Randevu 


class IlanInline(admin.TabularInline):
    model = Ilan
    extra = 0
    fields = ('ilan_no', 'baslik', 'islem_tipi', 'fiyat', 'durum', 'durum_kontrol')
    readonly_fields = ('ilan_no', 'baslik', 'islem_tipi', 'fiyat', 'durum_kontrol')
    can_delete = False
    show_change_link = True

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
    list_display = ('ad', 'soyad', 'telefon', 'aktif_ilanlar', 'pasif_ilanlar')
    inlines = [IlanInline] 

    def aktif_ilanlar(self, obj):
        return obj.ilanlar.filter(durum='Aktif').count()
    aktif_ilanlar.short_description = "🟢 Aktif"

    def pasif_ilanlar(self, obj):
        return obj.ilanlar.filter(durum='Pasif').count()
    pasif_ilanlar.short_description = "🔴 Pasif"


@admin.register(Ilan)
class IlanAdmin(admin.ModelAdmin):
    
    list_display = (
        'ilan_no', 'baslik', fiyat_goster, 'ana_kategori', 'il', 'mahalle', 
        durum_kontrol,
        'pasif_nedeni',
        'musteri'
    )
    
    list_filter = (
        'ana_kategori', 'durum', 'pasif_nedeni', 
        'krediye_uygun', 'tapu_durumu'
    )
    
    search_fields = ('ilan_no', 'baslik', 'il', 'ilce', 'mahalle', 'site_adi')
    radio_fields = {"ana_kategori": admin.HORIZONTAL}

    fieldsets = [
        ('Temel ve Durum Bilgileri', {
            'fields': (
                'ilan_no', 'baslik', 
                'durum', 'pasif_nedeni',
                'musteri', 
                ('ilan_tarihi', 'yayindan_kaldirilma_tarihi'), 
            ), 
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
            'fields': ('oda_sayisi', 'kat_sayisi', 'bulundugu_kat', 'banyo_sayisi', 'bina_yasi', 'mutfak_tipi', 'isitma_tipi', 'esyali', 'site_icerisinde', 'site_adi', 'kullanim_durumu', 'tapu_durumu', 'krediye_uygun', 'kimden', 'takas'),
        }),
        ('Arazi İlanına Ait Ek Bilgiler', {'fields': ('imar_durumu', 'm2', 'm2_fiyati', 'ada_no', 'parsel_no')}),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj and obj.durum == 'Pasif':
            if 'pasif_nedeni' in form.base_fields:
                form.base_fields['pasif_nedeni'].required = True
        
        return form
    
    class Media:
        js = (
            'js/admin_ilan_kontrol.js',
            'js/kategori_filtrele.js'
        )
        
@admin.register(PotansiyelMusteri)
class PotansiyelMusteriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'telefon', 'ilgili_ilan')
    search_fields = ('ad', 'soyad', 'telefon', 'ilgili_ilan__ilan_no')

@admin.register(Randevu)
class RandevuAdmin(admin.ModelAdmin):
    
    list_display = ('ilan', 'potansiyel_musteri', 'tarih_saat', 'durum')
    
    fields = (
        'ilan', 
        'potansiyel_musteri',
        'tarih_saat', 
        'durum', 
        'notlar'
    )
    
    search_fields = ('potansiyel_musteri__soyad', 'potansiyel_musteri__telefon')

