document.addEventListener('DOMContentLoaded', function() {
    const isUsedSelect = document.getElementById('is_used');
    
    // Обработчик изменения фильтра
    isUsedSelect.addEventListener('change', function() {
        const limit = document.getElementById('overtime-table-container').getAttribute('data-limit');
        const offset = document.getElementById('overtime-table-container').getAttribute('data-offset');
        const isUsedFilter = isUsedSelect.value;

        // Формируем новый URL с параметрами
        let url = `/overtime/?limit=${limit}&offset=${offset}`;

        // Добавляем фильтр is_used, если он выбран
        if (isUsedFilter !== "") {
            url += `&is_used=${isUsedFilter}`;
        }

        // Перезагружаем страницу с новыми параметрами
        window.location.href = url;
    });
});


