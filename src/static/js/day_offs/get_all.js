document.addEventListener('DOMContentLoaded', function() {
    const isUsedSelect = document.getElementById('filter');
    
    // Обработчик изменения фильтра
    isUsedSelect.addEventListener('change', function() {
        const limit = document.getElementById('day_off-table-container').getAttribute('data-limit');
        const isApprovedFilter = isUsedSelect.value;

        // Формируем новый URL с параметрами
        let url = `/day_off/?limit=${limit}&offset=0`; // Сбрасываем offset на 0

        // Добавляем фильтр filter, если он выбран
        if (isApprovedFilter !== "") {
            url += `&filter=${isApprovedFilter}`;
        }

        // Перезагружаем страницу с новыми параметрами
        window.location.href = url;
    });
});
