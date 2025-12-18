(function () {
    'use strict';

    window.addEventListener('load', function () {
        const detayKategori = document.querySelector('#id_detay_kategori');
        const radyoButonlari = document.querySelectorAll('input[name="ana_kategori"]');

        const tumVeriler = {
            'konut': [{ val: 'daire', text: 'Daire' }, { val: 'villa', text: 'Villa' }, { val: 'mustakil', text: 'Müstakil Ev' }],
            'isyeri': [{ val: 'dukkan', text: 'Dükkan' }, { val: 'ofis', text: 'Ofis' }, { val: 'depo', text: 'Depo' }],
            'arsa': [{ val: 'tarla', text: 'Tarla' }, { val: 'bahce', text: 'Bahçe' }],
            'diger': [{ val: 'baska', text: 'Belirtilmemiş / Başka' }]
        };

        function formAlanlariniDuzenle(secilen) {
            // Ortak Alanlar (Brüt ve Net)
            const brutAlani = document.querySelector('.field-brut');
            const netAlani = document.querySelector('.field-net');

            // İş Yerinde Gizlenecekler
            const isyeriGizlenecekler = document.querySelectorAll('.field-banyo_sayisi, .field-mutfak_tipi, .field-krediye_uygun, .field-kimden');

            // Bina/Site/Konut Alanları (Arsa seçildiğinde gizlenecek ana grup)
            const binaVeSiteAlanlari = document.querySelectorAll('.field-bina_yasi, .field-bulundugu_kat, .field-kat_sayisi, .field-isitma_tipi, .field-balkon, .field-asansor, .field-site_icerisinde, .field-site_adi, .field-esyali, .field-kullanim_durumu, .field-tapu_durumu, .field-takas, .field-oda_sayisi, .field-otopark_durumu, .field-aidat');

            // Arsa Özel Alanları (Sadece Arsa seçilince görünecekler)
            const arsaOzelAlanlari = document.querySelectorAll('.field-imar_durumu, .field-ada_no, .field-parsel_no, .field-m2, .field-m2_fiyati');

            // --- 1. BRÜT / NET GİZLEME MANTIĞI ---
            if (secilen === 'arsa') {
                if (brutAlani) brutAlani.style.display = 'none';
                if (netAlani) netAlani.style.display = 'none';
            } else if (secilen === 'isyeri') {
                if (brutAlani) brutAlani.style.display = 'none';
                if (netAlani) netAlani.style.display = 'block';
            } else {
                if (brutAlani) brutAlani.style.display = 'block';
                if (netAlani) netAlani.style.display = 'block';
            }

            // --- 2. GENEL SIFIRLAMA (Hepsini Gizle) ---
            binaVeSiteAlanlari.forEach(el => el.style.display = 'none');
            isyeriGizlenecekler.forEach(el => el.style.display = 'none');
            arsaOzelAlanlari.forEach(el => el.style.display = 'none');

            // --- 3. KATEGORİYE ÖZEL GÖSTERİM ---
            if (secilen === 'konut') {
                binaVeSiteAlanlari.forEach(el => el.style.display = 'block');
                isyeriGizlenecekler.forEach(el => el.style.display = 'block');
            }
            else if (secilen === 'isyeri') {
                binaVeSiteAlanlari.forEach(el => el.style.display = 'block');
                // İş yerinde site adı ve banyo gibi alanlar kapalı kalsın
            }
            else if (secilen === 'arsa') {
                arsaOzelAlanlari.forEach(el => el.style.display = 'block');
                // Arsa seçildiğinde binaVeSiteAlanlari grubu 'none' olarak kalır.
            }
        }

        function filtrele(secilenDeger) {
            if (!detayKategori) return;
            detayKategori.innerHTML = '<option value="">---------</option>';
            if (secilenDeger && tumVeriler[secilenDeger]) {
                tumVeriler[secilenDeger].forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.val;
                    opt.text = item.text;
                    detayKategori.appendChild(opt);
                });
            }
            formAlanlariniDuzenle(secilenDeger);
        }

        radyoButonlari.forEach(radio => {
            radio.addEventListener('change', function () {
                if (this.checked) filtrele(this.value);
            });
            if (radio.checked) filtrele(radio.value);
        });
    });
})();