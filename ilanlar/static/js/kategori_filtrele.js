(function () {
    'use strict';

    window.addEventListener('load', function () {
        const detayKategori = document.querySelector('#id_detay_kategori');
        const radyoButonlari = document.querySelectorAll('input[name="ana_kategori"]');

        if (!detayKategori) return;

        // Kategori haritası
        const harita = {
            'konut': ['daire', 'villa', 'mustakil'],
            'isyeri': ['dukkan', 'ofis', 'fabrika', 'depo'],
            'arsa': ['tarla', 'bahce'],
            'diger': ['baska']
        };

        function formAlanlariniDuzenle(secilen) {
            const brut = document.querySelector('.field-brut');
            const net = document.querySelector('.field-net');
            const isyeriGizle = document.querySelectorAll('.field-banyo_sayisi, .field-mutfak_tipi, .field-krediye_uygun, .field-kimden');
            const binaAlanlari = document.querySelectorAll('.field-bina_yasi, .field-bulundugu_kat, .field-kat_sayisi, .field-isitma_tipi, .field-balkon, .field-asansor, .field-site_icerisinde, .field-site_adi, .field-esyali, .field-kullanim_durumu, .field-tapu_durumu, .field-takas, .field-oda_sayisi, .field-otopark_durumu, .field-aidat');
            const arsaAlanlari = document.querySelectorAll('.field-imar_durumu, .field-ada_no, .field-parsel_no, .field-m2, .field-m2_fiyati');

            // Arsa/İşyeri Brüt-Net Mantığı
            if (brut) brut.style.display = (secilen === 'arsa' || secilen === 'isyeri') ? 'none' : 'block';
            if (net) net.style.display = (secilen === 'arsa') ? 'none' : 'block';

            // Grupları Temizle
            binaAlanlari.forEach(el => el.style.display = 'none');
            isyeriGizle.forEach(el => el.style.display = 'none');
            arsaAlanlari.forEach(el => el.style.display = 'none');

            // Kategoriye Göre Göster
            if (secilen === 'konut') {
                binaAlanlari.forEach(el => el.style.display = 'block');
                isyeriGizle.forEach(el => el.style.display = 'block');
            } else if (secilen === 'isyeri') {
                binaAlanlari.forEach(el => el.style.display = 'block');
            } else if (secilen === 'arsa') {
                arsaAlanlari.forEach(el => el.style.display = 'block');
            }
        }

        function filtrele(secilenAna) {
            const izinliler = harita[secilenAna] || [];

            // KRİTİK: innerHTML kullanmıyoruz, sadece gizliyoruz
            Array.from(detayKategori.options).forEach(opt => {
                if (opt.value === "" || izinliler.includes(opt.value)) {
                    opt.hidden = false;
                    opt.disabled = false;
                    opt.style.display = "block";
                } else {
                    opt.hidden = true;
                    opt.disabled = true;
                    opt.style.display = "none";
                }
            });

            // Seçili olan yasaklıysa sıfırla
            if (detayKategori.selectedOptions[0] && detayKategori.selectedOptions[0].disabled) {
                detayKategori.value = "";
            }

            formAlanlariniDuzenle(secilenAna);
        }

        radyoButonlari.forEach(radio => {
            radio.addEventListener('change', function () {
                if (this.checked) filtrele(this.value);
            });
            if (radio.checked) filtrele(radio.value);
        });
    });
})();