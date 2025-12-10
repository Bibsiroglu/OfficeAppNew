from django.core.management.base import BaseCommand
from datetime import date
from ilanlar.models import Ilan 
from django.db import connection

class Command(BaseCommand):
    help = 'Yayından kalkma tarihi BUGÜN veya ÖNCE olan Aktif ilanları Pasif duruma getirir.'

    def handle(self, *args, **options):
        # Bugünün tarihini al (saat bilgisi olmadan)
        bugun = date.today()
        
        # Sadece durumu 'Aktif' olan ve kalkış tarihi bugünden küçük veya eşit olan ilanları filtrele
        updated_count = Ilan.objects.filter(
            durum='Aktif',
            yayindan_kaldirilma_tarihi__lte=bugun # lte: less than or equal (küçük veya eşit)
        ).update(durum='Pasif') # Tek bir veritabanı sorgusu ile güncelle

        self.stdout.write(
            self.style.SUCCESS(f'✅ Başarıyla {updated_count} adet ilanın durumu Pasif olarak güncellendi.')
        )
        
        # Opsiyonel: Veritabanı bağlantılarını kapatmak için
        connection.close()