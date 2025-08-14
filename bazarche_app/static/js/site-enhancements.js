// Enhanced JavaScript for Bazarche App
document.addEventListener('DOMContentLoaded', function () {
    
    // Mobile menu functionality
    function toggleMobileMenu() {
        const menu = document.getElementById('mobileMenu');
        if (menu) {
            menu.classList.toggle('show');
        }
    }
    
    // City dropdown functionality
    function toggleCityDropdown() {
        const dropdown = document.getElementById('cityDropdown');
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    // User dropdown functionality
    function toggleUserDropdown() {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    // Make functions globally available
    window.toggleMobileMenu = toggleMobileMenu;
    window.toggleCityDropdown = toggleCityDropdown;
    window.toggleUserDropdown = toggleUserDropdown;
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        const cityDropdown = document.getElementById('cityDropdown');
        const userDropdown = document.getElementById('userDropdown');
        
        if (!event.target.closest('.nav-btn') && !event.target.closest('#cityDropdown')) {
            if (cityDropdown) cityDropdown.style.display = 'none';
        }
        
        if (!event.target.closest('.user-menu') && !event.target.closest('#userDropdown')) {
            if (userDropdown) userDropdown.style.display = 'none';
        }
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const mobileMenu = document.getElementById('mobileMenu');
        if (!event.target.closest('.mobile-menu-content') && !event.target.closest('.mobile-menu-toggle')) {
            if (mobileMenu) mobileMenu.classList.remove('show');
        }
    });
    
    // Product card click functionality
    const productCards = document.querySelectorAll('.product-card[data-product-url]');
    productCards.forEach(card => {
        card.addEventListener('click', function(event) {
            // Don't navigate if delete button or contact button was clicked
            if (!event.target.closest('.delete-button') && !event.target.closest('.contact-btn')) {
                const url = this.getAttribute('data-product-url');
                if (url) {
                    window.location.href = url;
                }
            }
        });
        
        // Add touch feedback
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        card.addEventListener('touchend', function() {
            this.style.transform = '';
        });
    });
    
    // Contact button functionality
    const contactButtons = document.querySelectorAll('.contact-btn');
    contactButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            // Prevent event bubbling for contact buttons
            event.stopPropagation();
        });
    });
    
    // Delete button functionality
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            if (confirm('آیا مطمئن هستید که می‌خواهید این محصول را حذف کنید؟')) {
                const url = this.getAttribute('onclick').match(/href\s*=\s*['"]([^'"]+)['"]/)[1];
                window.location.href = url;
            }
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Lazy loading images
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(image => {
        imageObserver.observe(image);
    });
    
    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('visible');
            } else {
                backToTopButton.classList.remove('visible');
            }
        });
        
        backToTopButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Dark Mode Toggle Script
    const darkModeIcon = document.getElementById('darkModeIcon');
    if (darkModeIcon) {
        darkModeIcon.addEventListener('click', function () {
            const body = document.body;
            body.classList.toggle('dark-mode');
            
            // Save the state in localStorage
            const isDarkMode = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            
            console.log('Dark mode toggled:', isDarkMode);
        });
        
        // Load Dark Mode Preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    }
    
    // اعتبارسنجی سریع و سازگار با موبایل و دسکتاپ برای فرم‌های کلیدی
    // فقط اگر فیلد ضروری خالی باشد، جلوی ارسال فرم را می‌گیرد
    // هیچ تاخیری یا انیمیشن اضافه ندارد

    document.querySelectorAll('form').forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            // These lines were causing buttons to be unresponsive. Removed to allow default click behavior.
            // submitBtn.onclick = null;
            // submitBtn.ontouchstart = null;
            // submitBtn.ontouchend = null;
        }
        form.addEventListener('submit', function(e) {
            let valid = true;
            form.querySelectorAll('[required]').forEach(field => {
                if (!field.value || !field.value.trim()) {
                    valid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('لطفاً تمام فیلدهای ضروری را پر کنید.');
            }
        }, { passive: false });
    });
    
    // Auto-hide messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('alert-dismissible')) {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }
        });
    }, 5000);
    
    // Touch-friendly improvements for mobile
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Remove hover effects on touch devices
        const touchElements = document.querySelectorAll('button, a, .category-card, .action-card');
        touchElements.forEach(element => {
            // Remove hover effects
            element.addEventListener('touchstart', function(e) {
                this.style.transform = 'scale(0.95)';
                this.style.transition = 'transform 0.1s ease';
            });
            
            element.addEventListener('touchend', function() {
                this.style.transform = '';
                this.style.transition = '';
            });
            
            // Prevent double-tap zoom: دیگر برای عناصر کلیکی هیچ preventDefault ای اعمال نمی‌کنیم
            element.addEventListener('touchend', function(e) {
                // اگر عنصر کلیک‌پذیر است، اجازه بده رفتار طبیعی اجرا شود
                if (this.tagName === 'A' || this.tagName === 'BUTTON' || this.closest('button') || this.closest('a')) {
                    return;
                }
                // برای عناصر غیرکلیک‌پذیر نیازی به کاری نیست
            }, { passive: true });
        });
        
        // Special handling for product cards to distinguish between scroll and tap
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            let startY = 0;
            let startX = 0;
            let hasMoved = false;
            
            card.addEventListener('touchstart', function(e) {
                startY = e.touches[0].clientY;
                startX = e.touches[0].clientX;
                hasMoved = false;
                
                this.style.transform = 'scale(0.95)';
                this.style.transition = 'transform 0.1s ease';
            });
            
            card.addEventListener('touchmove', function(e) {
                const currentY = e.touches[0].clientY;
                const currentX = e.touches[0].clientX;
                const deltaY = Math.abs(currentY - startY);
                const deltaX = Math.abs(currentX - startX);
                
                // If user has scrolled more than 10px, don't trigger click
                if (deltaY > 10 || deltaX > 10) {
                    hasMoved = true;
                }
            });
            
            card.addEventListener('touchend', function(e) {
                this.style.transform = '';
                this.style.transition = '';
                
                // Only trigger click if user hasn't scrolled
                if (!hasMoved) {
                    const url = this.getAttribute('data-product-url');
                    if (url && !e.target.closest('.delete-button') && !e.target.closest('.contact-btn')) {
                        window.location.href = url;
                    }
                }
            });
        });
    }
    
    // پاکسازی eventهای اضافی از دکمه submit فرم‌های کلیدی
    // حذف هرگونه event click/touch روی دکمه submit فرم ثبت‌نام
    document.querySelectorAll('form').forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            submitBtn.onclick = null;
            submitBtn.ontouchstart = null;
            submitBtn.ontouchend = null;
        }
    });
    
    console.log('Bazarche JavaScript loaded successfully!');
});
