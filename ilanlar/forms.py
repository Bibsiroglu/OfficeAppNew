from django import forms
from .models import Randevu 
# Eğer PotansiyelMusteri modeliniz varsa onu da import etmeniz gerekebilir.

class RandevuOlusturForm(forms.ModelForm):
    # Formdaki tarih ve saat alanının daha modern ve kullanıcı dostu görünmesi için
    tarih_saat = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Randevu Tarih ve Saati"
    )

    class Meta:
        model = Randevu
        # KRİTİK DÜZELTME: Artık 'ad', 'soyad', 'telefon' yerine 
        # sadece 'potansiyel_musteri' Foreign Key'ini kullanmalıyız.
        fields = [
            'potansiyel_musteri', # <-- YENİ FOREIGN KEY EKLENDİ
            'tarih_saat', 
            'notlar'
        ]
        
        # Eğer bu formu ilan detay sayfasında (frontend) kullanıyorsanız:
        labels = {
            'potansiyel_musteri': 'Randevu Alan Kişi',
            'tarih_saat': 'Randevu Tarihi ve Saati',
            'notlar': 'Ek Notlar (Opsiyonel)',
        }
        
        # widgets'ı da yeni alanlara göre güncelleyin.
        widgets = {
            'notlar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            # PotansiyelMusteri alanı için widget ayarlanmaz (Çünkü bu bir Select kutusudur)
        }