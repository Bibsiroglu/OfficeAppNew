from datetime import date, timedelta
from itertools import count
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.views.generic import ListView, CreateView 
from django.urls import reverse_lazy
from numpy import convolve
from sqlalchemy import Transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from .models import Ilan, Randevu, PotansiyelMusteri # Yeni modelleri import edin
from .forms import RandevuOlusturForm
from django.utils import timezone

from ilanlar.models import Ilan 

def randevu_durum_degistir(request, pk, yeni_durum):
    """Belirtilen randevunun durumunu günceller."""
    randevu = get_object_or_404(Randevu, pk=pk)
    
    # Randevu modelindeki DURUM_SECENEKLERI'ni kullanarak geçerli durumları kontrol ederiz
    # Randevu sınıfının DURUM_SECENEKLERI'ne ulaşmak için models.py'den ilgili seçeneği alın.
    # Geçerli durumları kontrol etmek için basit bir liste oluşturulmuştur.
    gecerli_durumlar = ['PLAN', 'TAMAM', 'IPTAL'] 
    
    if yeni_durum in gecerli_durumlar:
        randevu.durum = yeni_durum
        randevu.save()
        messages.success(request, f"Randevu ({randevu.potansiyel_musteri.ad}) durumu '{randevu.get_durum_display()}' olarak güncellendi.")
    else:
        messages.error(request, "Geçersiz randevu durumu.")
        
    return redirect('randevu_listesi')

class IlanListView(ListView):
    model = Ilan
    template_name = 'ilanlar/ilan_listesi.html'
    context_object_name = 'ilanlar' # Varsayılan listeyi 'ilanlar' olarak adlandırır
    paginate_by = 10
    def get_context_data(self, **kwargs):
        # Üst sınıftan context'i alın
        context = super().get_context_data(**kwargs)
        bugun = date.today()
        yarin = bugun + timedelta(days=1)

        # Bugun kalkan ilanları sorgula
        bugun_kalkan_ilanlar_qs = self.model.objects.filter(
            yayindan_kaldirilma_tarihi=bugun
        )

        yarin_kalkan_ilanlar_qs = self.model.objects.filter(
            yayindan_kaldirilma_tarihi=yarin
        )
        # Diğer ilanları sorgula (Bugün kalkanları hariç tutarak)
        diger_ilanlar_qs = self.model.objects.exclude(
            id__in=bugun_kalkan_ilanlar_qs.values_list('id', flat=True)
        )
        
        # KRİTİK EKLEME: Değişkenleri context'e ekleyin
        context['bugun_kalkan_ilanlar'] = bugun_kalkan_ilanlar_qs
        context['yarin_kalkan_ilanlar'] = yarin_kalkan_ilanlar_qs
        context['diger_ilanlar'] = diger_ilanlar_qs
        
        # Toplam sayıyı da hesaplayalım
        context['toplam_ilan_sayisi'] = bugun_kalkan_ilanlar_qs.count() + diger_ilanlar_qs.count()
        context['uyari_ilan_toplami'] = bugun_kalkan_ilanlar_qs.count() + yarin_kalkan_ilanlar_qs.count()


        return context
    
    def get_queryset(self):
        # Varsayılan QuerySet'i alır
        queryset = super().get_queryset()

        # Her ilanın randevu sayısını (ziyaret sayısını) hesapla
        queryset = queryset.annotate(
            # 'randevular' related_name'ini kullanarak sayım yapar (Randevu modelinizdeki ilişki adı)
            ziyaret_sayisi=count('randevular') 
        )
        
        # Eğer en çok randevu alanı üste almak isterseniz:
        # queryset = queryset.order_by('-ziyaret_sayisi', '-ilan_tarihi')

        return queryset

    def get_queryset(self):
        # Varsayılan olarak tüm aktif ilanları getirir. 
        # Gelecekte buraya arama ve filtreleme mantığı eklenecektir.
        return Ilan.objects.filter(durum='Aktif').order_by('-ilan_tarihi')
    
    
class IlanCreateView(CreateView):
    # Hangi model ile çalışacağımızı belirtir
    model = Ilan
    
    # Kullanılacak şablonun yolunu belirtir
    template_name = 'ilanlar/ilan_ekle.html' 
    
    # Formda hangi alanların görünmesini istediğimizi belirtir
    # Tüm alanları otomatik almak yerine, güvenlik için tek tek belirtmek önerilir.
    fields = [
        'ilan_no', 'baslik', 'ana_kategori', 'detay_kategori', 
        'fiyat', 'brut', 'net', 'oda_sayisi', 'bina_yasi', 'bulundugu_kat', 
        'kat_sayisi', 'isitma_tipi', 'banyo_sayisi', 'mutfak_tipi', 
        'balkon', 'asansor', 'otopark_durumu', 'esyali', 'kullanim_durumu', 
        'site_icerisinde', 'site_adi', 'aidat', 'krediye_uygun', 'tapu_durumu', 
        'kimden', 'takas', 'durum', 'imar_durumu', 'm2', 'm2_fiyati', 
        'ada_no', 'parsel_no','il', 'ilce', 'mahalle', 'adres'
    ]
    
    # Form başarılı şekilde kaydedildikten sonra kullanıcıyı yönlendireceği URL
    # reverse_lazy kullanmak, URL'nin kod yüklendiğinde değil, gerektiğinde aranmasını sağlar.
    success_url = reverse_lazy('ilan_listesi')

    
def ilan_detay(request, pk):
    ilan = get_object_or_404(Ilan, pk=pk)
    
    # 1. Randevuların tamamını çekme (tercihen sıralı)
    # Varsayım: Randevu modelinde ilan Foreign Key'inin related_name'i 'randevular'dır.
    ilgili_randevular = ilan.randevular.all().order_by('-tarih_saat')
    
    # 2. Sayıyı hesaplama
    toplam_randevu_sayisi = ilgili_randevular.count()

    if request.method == 'POST':
        form = RandevuOlusturForm(request.POST)
            
        if form.is_valid():
            with Transaction.atomic():
                
                # --- 1. RANDEVUYU KAYDET ---
                randevu = form.save(commit=False)
                randevu.ilan = ilan
                randevu.durum = 'PLAN'
                randevu.save()
                
                potansiyel_musteri_objesi = randevu.potansiyel_musteri

                PotansiyelMusteri.objects.update_or_create(
                    telefon=potansiyel_musteri_objesi.telefon, 
                    defaults={
                    'ad': potansiyel_musteri_objesi.ad,
                    'soyad': potansiyel_musteri_objesi.soyad,
                    'ilgili_ilan': ilan 
                    }
                )
                
            # Başarılı kayıttan sonra ilan detayına geri yönlendir
            return redirect('ilan_detay', pk=ilan.pk) 
    else:
        form = RandevuOlusturForm()
    
    context = {
        'ilan': ilan,
        'ilgili_randevular': ilgili_randevular, # Liste
        'randevu_form': form,
        'toplam_randevu_sayisi': toplam_randevu_sayisi, # Sayı
    }
    
    return render(request, 'ilanlar/ilan_detay.html', context)

class RandevuListView(ListView):
    model = Randevu
    template_name = 'randevular/randevu_listesi.html'
    context_object_name = 'randevular'
    paginate_by = 20 # Sayfa başına 20 randevu göster

    def get_queryset(self):
        # Varsayılan sıralama: En yeni randevular en üstte
        queryset = Randevu.objects.all().order_by('-tarih_saat')
        
        # Filtreleme mantığı buraya eklenebilir (örneğin GET parametreleri ile durum filtresi)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        toplam_sayi = self.get_queryset().count()
        context['toplam_randevu_sayisi'] = toplam_sayi

        queryset = self.get_queryset()
        context ['planlanan_sayisi'] = queryset.filter(durum='PLAN').count()
        context ['tamamlanan_sayisi'] = queryset.filter(durum='TAMAM').count()
        context ['iptal_edilen_sayisi'] = queryset.filter(durum='IPTAL').count()

        # 2. Son 7 Gün Filtresi Tanımlama
        yedi_gun_oncesi = timezone.now() - timedelta(days=7)
        
        # Yalnızca son 7 güne ait randevuları içeren QuerySet
        # 'tarih_saat__gte': tarih_saat alanı, 7 gün öncesinden büyük veya eşit olmalı.
        grafik_queryset = Randevu.objects.filter(tarih_saat__gte=yedi_gun_oncesi)
        
        # 3. Son 7 Günlük Sayımlar (Grafik için)
        # Değişken isimlerine '_7gun' eki ekleyerek genel sayımlarla karışmasını önledik.
        
        context['toplam_randevu_sayisi_7gun'] = grafik_queryset.count()
        
        context['planlanan_sayisi_7gun'] = grafik_queryset.filter(durum='PLAN').count()
        context['tamamlanan_sayisi_7gun'] = grafik_queryset.filter(durum='TAMAM').count()
        context['iptal_edilen_sayisi_7gun'] = grafik_queryset.filter(durum='IPTAL').count()
        
        # Toplam randevu sayısını sadece 7 günlük verilerden hesaplama (Eğer gerekirse)
        # Bu, grafik_queryset.count() ile zaten aynı sonucu verir.

        return context

    
