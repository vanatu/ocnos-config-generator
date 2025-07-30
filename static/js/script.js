document.addEventListener('DOMContentLoaded', function () {
    // Инициализация
    updVendor();

    // Обработчики событий
    const vendorSelect = document.getElementById('select-vendors');
    vendorSelect.addEventListener('change', updVendor);
    document.querySelector('.btn-clear').addEventListener('click', clearForm);
});

function updVendor() {
    const select = document.getElementById('select-vendors');
    const lo = document.getElementById('inp-lo');

    // Удаляем предыдущие классы
    select.classList.remove('ocnos', 'junos');

    // Добавляем соответствующий класс
    if (select.value === 'Junos') {
        select.classList.add('junos');
        lo.placeholder = 'lo0';
    } else if (select.value === 'OcNOS') {
        select.classList.add('ocnos');
        lo.placeholder = 'lo';
    }
}

function clearForm() {
    const clearBtn = document.querySelector('.btn-clear');
    const form = document.getElementById('configForm');

    // Анимация нажатия
    clearBtn.classList.add('active');
    setTimeout(() => {
        clearBtn.classList.remove('active');
    }, 200);

    // Сброс формы
    form.reset();

    // Очистка текстовых полей
    document.querySelectorAll('input[type="text"]').forEach(input => {
        input.value = '';
    });

    // Сброс чекбоксов
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });

    // Фокус на первый элемент
    form.querySelector('input').focus();
}