from datetime import date, timedelta
from itertools import count

from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.views.generic import ListView, CreateView 
from django.urls import reverse_lazy

from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from .models import Ajanda, Ilan, Randevu, PotansiyelMusteri # Yeni modelleri import edin
from .forms import RandevuOlusturForm
from django.utils import timezone
from django.db.models import Count
import google.generativeai as genai
from django.http import JsonResponse
from django.conf import settings

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
    
    # 1. Mevcut Verileri Çekme
    ilgili_randevular = ilan.randevular.all().order_by('-tarih_saat')
    leads = ilan.leads.all()
    toplam_randevu_sayisi = ilgili_randevular.count()
    ai_analiz_raporu = ""

    # 2. AI ANALİZ SİSTEMİ (Sadece Sayfa İlk Açıldığında veya GET isteğinde)
    if request.method == 'GET':
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)

            # Model ismini 1.5-flash olarak sabitledik (en stabil versiyon)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt = f"""
            Bir gayrimenkul yatırım uzmanı olarak şu ilanı analiz et:
            Başlık: {ilan.baslik}
            Konum: {ilan.il}/{ilan.ilce}/{ilan.mahalle}
            Fiyat: {ilan.fiyat} TL
            Özellikler: {ilan.net}m2, {ilan.oda_sayisi} oda, Yaş: {ilan.bina_yasi}, Kat: {ilan.bulundugu_kat}
            Ekstralar: Site: {ilan.site_icerisinde}, Otopark: {ilan.otopark_durumu}, Isınma: {ilan.get_isitma_tipi_display}

            Lütfen şu formatta profesyonel bir HTML yanıt ver:
            <h5><i class='fas fa-search-dollar'></i> Fiyat Analizi</h5><p>Analiz...</p>
            <h5><i class='fas fa-chart-line'></i> Yatırım Potansiyeli</h5><p>Analiz...</p>
            <h5><i class='fas fa-bullseye'></i> Hedef Kitle ve Strateji</h5><p>Analiz...</p>
            """
            response = model.generate_content(prompt)
            ai_analiz_raporu = response.text.replace("```html", "").replace("```", "")
        except Exception as e:
            
            ai_analiz_raporu = f"<p class='text-muted small'>Analiz şu an oluşturulamadı.</p>"

    # 3. RANDEVU FORMU İŞLEME (POST METODU)
    form = RandevuOlusturForm() # Varsayılan boş form
    if request.method == 'POST':
        form = RandevuOlusturForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                randevu = form.save(commit=False)
                randevu.ilan = ilan
                randevu.durum = 'PLAN'
                randevu.save()
                
                # Potansiyel Müşteri Güncelleme/Oluşturma
                potansiyel_musteri_objesi = randevu.potansiyel_musteri
                PotansiyelMusteri.objects.update_or_create(
                    telefon=potansiyel_musteri_objesi.telefon, 
                    defaults={
                        'ad': potansiyel_musteri_objesi.ad,
                        'soyad': potansiyel_musteri_objesi.soyad,
                        'ilgili_ilan': ilan 
                    }
                )
            messages.success(request, "Randevu başarıyla oluşturuldu.")
            return redirect('ilan_detay', pk=ilan.pk)

    # 4. TEK BİR CONTEXT VE RENDER
    context = {
        'ilan': ilan,
        'ilgili_randevular': ilgili_randevular,
        'leads': leads,
        'ai_analiz_raporu': ai_analiz_raporu,
        'toplam_randevu_sayisi': toplam_randevu_sayisi,
        'randevu_form': form,
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

        on_bes_gun_oncesi = timezone.now() - timedelta(days=15)
        populer_ilanlar = Randevu.objects.filter(
            durum='TAMAM',
            ilan__isnull=False,
            tarih_saat__gte=on_bes_gun_oncesi  # Filtreyi buraya ekledik
        ).values('ilan__baslik').annotate(
            toplam_randevu=Count('id')
                ).order_by('-toplam_randevu')[:5]

    # Listeleri hazırlayalım (JavaScript'e göndermek için)
        context['ilan_basliklari'] = [item['ilan__baslik'] for item in populer_ilanlar]
        context['ilan_randevu_sayilari'] = [item['toplam_randevu'] for item in populer_ilanlar]
        grafik_queryset = Randevu.objects.filter(tarih_saat__gte=on_bes_gun_oncesi)
        context ['planlanan_sayisi'] = queryset.filter(durum='PLAN').count()
        context ['tamamlanan_sayisi'] = queryset.filter(durum='TAMAM').count()
        context ['iptal_edilen_sayisi'] = queryset.filter(durum='IPTAL').count()

        son_iki_hafta = timezone.now() - timedelta(days=15)
        
       
        grafik_queryset = Randevu.objects.filter(tarih_saat__gte=son_iki_hafta)
        

        
        context['toplam_randevu_sayisi_7gun'] = grafik_queryset.count()
    
        context['planlanan_sayisi_7gun'] = grafik_queryset.filter(durum='PLAN').count()
        context['tamamlanan_sayisi_7gun'] = grafik_queryset.filter(durum='TAMAM').count()
        context['iptal_edilen_sayisi_7gun'] = grafik_queryset.filter(durum='IPTAL').count()

    
        
        # Toplam randevu sayısını sadece 7 günlük verilerden hesaplama (Eğer gerekirse)
        # Bu, grafik_queryset.count() ile zaten aynı sonucu verir.

        return context

    
def ajanda_sayfasi(request):
    gorevler = Ajanda.objects.all().order_by('tarih')
    return render(request, 'ajanda.html', {'gorevler': gorevler})

def gorev_tamamla(request, gorev_id):
    gorev = get_object_or_404(Ajanda, id=gorev_id)
    gorev.durum = 'Tamamlandi'
    gorev.save()
    return redirect('ajanda_sayfasi')

def ai_asistan_sayfasi(request):
    ilanlar = Ilan.objects.all()
    ai_sonuc = None
    
    if request.method == "POST":
        secilen_ilan_id = request.POST.get('ilan_id')
        icerik_turu = request.POST.get('tur')
        ilan = Ilan.objects.get(id=secilen_ilan_id)
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        try:
            # Listenin en başındaki en güncel modeli kullanıyoruz
            model = genai.GenerativeModel('models/gemini-2.5-flash')

            if icerik_turu == "instagram":
                talimat = "Bu ilan için bol emojili, merak uyandıran bir Instagram post metni ve 10 tane popüler emlak hashtag'i hazırla."
            elif icerik_turu == "whatsapp":
                talimat = "Bu ilan için potansiyel bir müşteriye WhatsApp üzerinden gönderilecek kısa, samimi ve teknik bilgileri içeren bir tanıtım mesajı yaz."
            else:
                talimat = "Bu taşınmaz için profesyonel, ciddi ve ikna edici bir web sitesi ilan açıklaması yaz."

            
            prompt = f"""
            {talimat}
            Bir gayrimenkul uzmanı gibi davran. 
            Başlık: {ilan.baslik}
            Konum: {ilan.ilce} / {ilan.il}
            Fiyat: {ilan.fiyat} TL
            Bu özelliklere sahip emlak ilanı için profesyonel bir açıklama yaz.
            """
            
            response = model.generate_content(prompt)
            ai_sonuc = response.text
            
        except Exception as e:
            print(f"Sistem Hatası: {e}")
            ai_sonuc = f"İçerik üretilirken bir hata oluştu: {e}"
            
    return render(request, 'ilanlar/ai_asistan.html', {'ilanlar': ilanlar, 'ai_sonuc': ai_sonuc})