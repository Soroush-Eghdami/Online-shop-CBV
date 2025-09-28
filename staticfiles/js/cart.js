document.addEventListener('DOMContentLoaded', function() {
    // Auto-update cart when quantity changes
    const quantityInputs = document.querySelectorAll('.auto-update-form input[type="number"]');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Validate input
            if (this.value < 1) {
                this.value = 1;
            } else if (this.value > 20) {
                this.value = 20;
            }
            
            // Submit the form
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
        
        // Also handle input event for real-time updates
        input.addEventListener('input', function() {
            // Debounce the input to avoid too many requests
            clearTimeout(this.updateTimeout);
            this.updateTimeout = setTimeout(() => {
                if (this.value >= 1 && this.value <= 20) {
                    const form = this.closest('form');
                    if (form) {
                        form.submit();
                    }
                }
            }, 500); // Wait 500ms after user stops typing
        });
    });
    
    // Add smooth animations for cart updates
    const cartTable = document.querySelector('.cart-table');
    if (cartTable) {
        cartTable.style.transition = 'opacity 0.3s ease';
    }
    
    // Show loading indicator during updates
    const forms = document.querySelectorAll('.auto-update-form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Add loading class to the table
            if (cartTable) {
                cartTable.style.opacity = '0.7';
            }
        });
    });
});

