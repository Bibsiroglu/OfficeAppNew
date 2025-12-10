from django.urls import path
from . import views

urlpatterns = [
    path('', views.IlanListView.as_view(), name='ilan_listesi'),
    path('ekle/', views.IlanCreateView.as_view(), name='ilan_ekle'),
    path('detay/<int:pk>/', views.ilan_detay, name='ilan_detay'),
    path('randevular/', views.RandevuListView.as_view(), name='randevu_listesi'),
    path('randevu/<int:pk>/durum-degistir/<str:yeni_durum>/', views.randevu_durum_degistir, name='randevu_durum_degistir'),
]