console.log('js Burada!')
document.addEventListener('DOMContentLoaded', function () {
    // 1. Durum alanını seçin (Admin paneli, alan adının başına 'id_' ekler)
    const durumSelect = document.getElementById('id_durum');

    // 2. Pasif Nedeni alanının bulunduğu ana div'i bulun
    // Django Admin, her alan için bir .form-row div'i oluşturur.
    const pasifNedeniRow = document.querySelector('.field-pasif_nedeni');

    // Eğer alanlar sayfada yoksa (örneğin fieldsets içinde gizliyse) kodu çalıştırmayı durdur
    if (!durumSelect || !pasifNedeniRow) {
        return;
    }

    // 3. Görünürlüğü Kontrol Eden Fonksiyon
    function checkVisibility() {
        // Durum seçeneği 'PASIF' ise (models.py'de tanımladığınız değer)
        if (durumSelect.value === 'PASIF') {
            pasifNedeniRow.style.display = 'block'; // Göster
        } else {
            pasifNedeniRow.style.display = 'none';  // Gizle
        }
    }

    // 4. Sayfa Yüklendiğinde kontrolü hemen çalıştır
    checkVisibility();

    // 5. Durum alanı değiştiğinde kontrolü tekrar çalıştır
    durumSelect.addEventListener('change', checkVisibility);
});