// ============================================================
// Лоскутная мастерская — основной JavaScript
// ============================================================

document.addEventListener('DOMContentLoaded', function() {

    // ===== Автоматическое скрытие уведомлений =====
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // ===== Активация тултипов Bootstrap =====
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ===== Активация поповеров Bootstrap =====
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // ===== Кнопка "Наверх" =====
    const scrollBtn = document.querySelector('.scroll-top-btn');
    if (scrollBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        });

        scrollBtn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ===== Обновление количества в корзине через AJAX =====
    function updateCartCount() {
        const cartBadge = document.getElementById('cart-badge');
        if (!cartBadge) return;

        fetch('/cart/count/')
            .then(response => response.json())
            .then(data => {
                if (data.total_items > 0) {
                    cartBadge.textContent = data.total_items;
                    cartBadge.style.display = 'block';
                } else {
                    cartBadge.style.display = 'none';
                }
            })
            .catch(error => console.error('Ошибка обновления корзины:', error));
    }

    // Обновляем при загрузке и каждые 30 секунд
    updateCartCount();
    setInterval(updateCartCount, 30000);

});