(function () {
    'use strict';

    window.addEventListener('load', function () {
        console.log("CRM Radyo Buton Kontrolü Başladı");

        // Radyo butonlarını ve hedef dropdown'ı seçiyoruz
        // Django radyo butonlarına isim olarak 'ana_kategori' verir
        const detayKategori = document.querySelector('#id_detay_kategori');

        const tumVeriler = {
            'konut': [
                { val: 'daire', text: 'Daire' },
                { val: 'villa', text: 'Villa' },
                { val: 'mustakil', text: 'Müstakil Ev' }
            ],
            'isyeri': [
                { val: 'dukkan', text: 'Dükkan' },
                { val: 'ofis', text: 'Ofis' },
                { val: 'depo', text: 'Depo' }
            ],
            'arsa': [
                { val: 'tarla', text: 'Tarla' },
                { val: 'bahce', text: 'Bahçe' }
            ],
            'diger': [
                { val: 'baska', text: 'Belirtilmemiş / Başka' }
            ]
        };

        function filtrele(secilenDeger) {
            console.log("Filtreleniyor: " + secilenDeger);

            if (!detayKategori) return;

            // Listeyi temizle
            detayKategori.innerHTML = '<option value="">---------</option>';

            if (secilenDeger && tumVeriler[secilenDeger]) {
                tumVeriler[secilenDeger].forEach(function (item) {
                    const opt = document.createElement('option');
                    opt.value = item.val;
                    opt.text = item.text;
                    detayKategori.appendChild(opt);
                });
            }
        }

        // Sayfadaki tüm 'ana_kategori' isimli radyo butonlarını bul ve dinle
        const radyoButonlari = document.querySelectorAll('input[name="ana_kategori"]');

        radyoButonlari.forEach(radio => {
            // Tıklandığında filtrele
            radio.addEventListener('change', function () {
                if (this.checked) {
                    filtrele(this.value);
                }
            });

            // Sayfa yüklendiğinde hangisi seçiliyse onu çalıştır
            if (radio.checked) {
                filtrele(radio.value);
            }
        });
    });
})();