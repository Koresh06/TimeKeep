document.addEventListener('DOMContentLoaded', function() {
    const isUsedSelect = document.getElementById('filter');
    
    // Обработчик изменения фильтра
    isUsedSelect.addEventListener('change', function() {
        const limit = document.getElementById('overtime-table-container').getAttribute('data-limit');
        const isUsedFilter = isUsedSelect.value;

        // Формируем новый URL с параметрами
        let url = `/overtime/?limit=${limit}&offset=0`; // Сбрасываем offset на 0

        // Добавляем фильтр filter, если он выбран
        if (isUsedFilter !== "") {
            url += `&filter=${isUsedFilter}`;
        }

        // Перезагружаем страницу с новыми параметрами
        window.location.href = url;
    });
});
