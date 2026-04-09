// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Чек-лист AJAX
    document.querySelectorAll('.checklist-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const itemDiv = this.closest('.checklist-item');
            const itemId = itemDiv.dataset.id;
            const span = itemDiv.querySelector('span');
            const originalState = this.checked;

            // Если чекбокс disabled, ничего не делаем
            if (this.disabled) return;

            fetch(`/orders/toggle-checklist/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    if (data.is_completed) {
                        span.style.textDecoration = 'line-through';
                        span.style.color = '#A7D0CD';
                    } else {
                        span.style.textDecoration = 'none';
                        span.style.color = '';
                    }
                } else {
                    // Возвращаем чекбокс в исходное состояние при ошибке
                    this.checked = originalState;
                    alert(data.message || 'Ошибка при сохранении');
                }
            })
            .catch(error => {
                // Возвращаем чекбокс в исходное состояние при ошибке
                this.checked = originalState;
                console.error('Error:', error);
                alert('Ошибка при сохранении');
            });
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}