// Mobile Enhancements for Bazarche App

document.addEventListener('DOMContentLoaded', function() {
    
    // Optimize touch interactions
    optimizeTouchInteractions();
    
    // Improve scrolling performance
    optimizeScrolling();
    
    // Add loading states
    addLoadingStates();
    
    // Improve accessibility
    improveAccessibility();
    
    // Optimize images
    optimizeImages();
    
    // Add smooth transitions
    addSmoothTransitions();

    // این کد باعث غیرفعال شدن دکمه‌های فرم می‌شد. برای رفع مشکل کامنت شد
    // document.querySelectorAll('form').forEach(form => {
    //     const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
    //     if (submitBtn) {
    //         submitBtn.onclick = null;
    //         submitBtn.ontouchstart = null;
    //         submitBtn.ontouchend = null;
    //     }
    // });
});

// Optimize touch interactions for mobile
function optimizeTouchInteractions() {
    // فقط روی دکمه‌های نوار (navbar) و دکمه‌هایی که نیاز به تمایز اسکرول و کلیک دارند تاچ سریع اجرا شود
    // دکمه‌های دسته‌بندی (.category-card)، ثبت محصول و استخدام (.action-card) فقط click داشته باشند
    const touchElements = document.querySelectorAll('.nav-btn, .user-btn');
    
    touchElements.forEach(element => {
        let touchStartY = 0;
        let touchStartX = 0;
        let moved = false;

        element.addEventListener('touchstart', function(e) {
            touchStartY = e.touches[0].clientY;
            touchStartX = e.touches[0].clientX;
            moved = false;
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
        });

        element.addEventListener('touchmove', function(e) {
            const deltaY = Math.abs(e.touches[0].clientY - touchStartY);
            const deltaX = Math.abs(e.touches[0].clientX - touchStartX);
            if (deltaY > 10 || deltaX > 10) {
                moved = true;
            }
        });

        element.addEventListener('touchend', function(e) {
            this.style.transform = '';
            this.style.transition = '';
            if (!moved) {
                // لمس سریع و بدون اسکرول = کلیک
                if (this.tagName === 'A' && this.href) {
                    window.location = this.href;
                } else {
                    this.click();
                }
            }
        }, { passive: false });
    });
    // دکمه‌های دسته‌بندی و اکشن فقط click داشته باشند و هیچ touch هندل نشود
    // اگر لازم است می‌توانید این خط را اضافه کنید:
    // document.querySelectorAll('.category-card, .action-card').forEach(el => { el.onclick = null; });
}

// Optimize scrolling performance
function optimizeScrolling() {
    let ticking = false;
    
    function updateScroll() {
        // Add scroll-based animations or optimizations here
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScroll);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick, { passive: true });
}

// Add loading states for better UX
function addLoadingStates() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const image = card.querySelector('.product-image');
        
        if (image) {
            // Add loading state
            card.classList.add('loading');
            
            image.addEventListener('load', function() {
                card.classList.remove('loading');
            });
            
            image.addEventListener('error', function() {
                card.classList.remove('loading');
                // Add fallback image
                this.src = '/static/images/placeholder.jpg';
            });
        }
    });
}

// Improve accessibility for mobile
function improveAccessibility() {
    // Add better focus management
    const focusableElements = document.querySelectorAll('button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #667eea';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
    
    // Add keyboard navigation for mobile menu
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleMobileMenu();
            }
        });
    }
}

// Optimize images for mobile
function optimizeImages() {
    const images = document.querySelectorAll('.product-image');
    
    images.forEach(image => {
        // Add lazy loading
        image.loading = 'lazy';
        
        // Add responsive image sizes
        if (window.innerWidth <= 480) {
            // For mobile, we can use smaller images
            const originalSrc = image.src;
            // You can implement responsive image logic here
        }
    });
}

// Add smooth transitions
function addSmoothTransitions() {
    // Add intersection observer for smooth animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe product cards and category cards
    const animatedElements = document.querySelectorAll('.product-card, .category-card, .action-card');
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Mobile-specific optimizations
function mobileOptimizations() {
    // Disable hover effects on touch devices
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }
    
    // Optimize for mobile performance
    if (window.innerWidth <= 768) {
        // Reduce animations on mobile for better performance
        document.body.style.setProperty('--animation-duration', '0.2s');
    }
}

// Add pull-to-refresh functionality (optional)
function addPullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let pullDistance = 0;
    const threshold = 80;
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
        }
    });
    
    document.addEventListener('touchmove', function(e) {
        if (window.scrollY === 0 && startY > 0) {
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 0) {
                e.preventDefault();
                // Add pull-to-refresh visual feedback here
            }
        }
    });
    
    document.addEventListener('touchend', function() {
        if (pullDistance > threshold) {
            // Trigger refresh
            window.location.reload();
        }
        startY = 0;
        pullDistance = 0;
    });
}

// Initialize mobile optimizations
mobileOptimizations();

// Add CSS custom properties for better theming
document.documentElement.style.setProperty('--primary-color', '#667eea');
document.documentElement.style.setProperty('--secondary-color', '#764ba2');
document.documentElement.style.setProperty('--success-color', '#4CAF50');
document.documentElement.style.setProperty('--danger-color', '#e74c3c');
document.documentElement.style.setProperty('--border-radius', '8px');
document.documentElement.style.setProperty('--transition-duration', '0.2s');

// Performance monitoring
function monitorPerformance() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
    });
    
    // Monitor scroll performance
    let scrollCount = 0;
    window.addEventListener('scroll', function() {
        scrollCount++;
        if (scrollCount % 100 === 0) {
            console.log(`Scrolled ${scrollCount} times`);
        }
    }, { passive: true });
}

// Initialize performance monitoring
monitorPerformance();

// Add error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Add unhandled promise rejection handling
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});