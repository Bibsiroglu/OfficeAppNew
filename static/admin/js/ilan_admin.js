// static/admin/js/ilan_admin.js

(function ($) {
    $(document).ready(function () {
        var $kategoriSelector = $('input[name="ana_kategori"]');

        // Hangi fieldset gruplarını kontrol edeceğimizi tanımlıyoruz (CSS class'ları)
        var $konutFields = $('.konut-fields');
        var $arsaFields = $('.arsa-fields');
        var $isyeriFields = $('.isyeri-fields');

        // Fonksiyon: Alanları seçime göre göster/gizle
        function toggleCategoryFields(selectedCategory) {
            // Önce tüm özel alanları gizle
            $konutFields.hide();
            $arsaFields.hide();
            $isyeriFields.hide();

            // Seçilen kategoriye göre doğru grupları göster
            if (selectedCategory === 'konut') {
                $konutFields.show();
            } else if (selectedCategory === 'arsa') {
                $arsaFields.show();
            } else if (selectedCategory === 'isyeri') {
                $isyeriFields.show();
            }
        }

        // 1. Sayfa Yüklendiğinde Başlangıç Durumunu Ayarla
        var initialCategory = $kategoriSelector.filter(':checked').val();
        toggleCategoryFields(initialCategory);

        // 2. Değişiklik Olduğunda Alanları Ayarla
        $kategoriSelector.on('change', function () {
            var selectedCategory = $(this).val();
            toggleCategoryFields(selectedCategory);
        });
    });
})(django.jQuery);