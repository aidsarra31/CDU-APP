// Main JavaScript file for Sonatrach Portal

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Form validation for department forms
    const departmentForm = document.querySelector('.data-form');
    if (departmentForm) {
        departmentForm.addEventListener('submit', function(e) {
            const periode = document.getElementById('periode');
            if (periode) {
                const periodeValue = periode.value;
                const periodePattern = /^\d{6}$/; // YYYYMM format
                
                if (!periodePattern.test(periodeValue)) {
                    e.preventDefault();
                    showAlert('Period must be in YYYYMM format (e.g., 202401)', 'error');
                    periode.focus();
                    return false;
                }
                
                // Validate year (should be reasonable)
                const year = parseInt(periodeValue.substring(0, 4));
                const month = parseInt(periodeValue.substring(4, 6));
                
                if (year < 2020 || year > 2030) {
                    e.preventDefault();
                    showAlert('Year must be between 2020 and 2030', 'error');
                    periode.focus();
                    return false;
                }
                
                if (month < 1 || month > 12) {
                    e.preventDefault();
                    showAlert('Month must be between 01 and 12', 'error');
                    periode.focus();
                    return false;
                }
            }
            
            // Validate valeur field (should be positive)
            const valeur = document.getElementById('valeur');
            if (valeur && parseInt(valeur.value) < 0) {
                e.preventDefault();
                showAlert('Value must be a positive number', 'error');
                valeur.focus();
                return false;
            }
        });
    }

    // Add loading state to export buttons
    const exportButtons = document.querySelectorAll('.export-btn, .global-export-btn');
    exportButtons.forEach(function(button) {
        if (!button.classList.contains('disabled')) {
            button.addEventListener('click', function() {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
                button.style.pointerEvents = 'none';
                
                // Reset button after 10 seconds (in case of error)
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.style.pointerEvents = 'auto';
                }, 10000);
            });
        }
    });

    // Sidebar navigation highlighting
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    
    sidebarLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
            link.style.borderLeftColor = 'white';
        }
    });

    // Auto-refresh director dashboard status every 30 seconds
    if (document.querySelector('.director-dashboard')) {
        setInterval(function() {
            const statusIndicators = document.querySelectorAll('.status-indicator');
            // Add a subtle animation to indicate refresh
            statusIndicators.forEach(function(indicator) {
                indicator.style.transform = 'scale(1.1)';
                setTimeout(function() {
                    indicator.style.transform = 'scale(1)';
                }, 200);
            });
        }, 30000);
    }

    // Department card hover effects
    const departmentCards = document.querySelectorAll('.department-card');
    departmentCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 8px 25px rgba(255, 102, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 4px 6px hsla(210, 40%, 8%, 0.05)';
        });
    });

    // Form input enhancements
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
        });
    });
});

// Utility function to show custom alerts
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    messagesContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateY(-20px)';
        setTimeout(function() {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// Create messages container if it doesn't exist
function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(container, mainContent.firstChild);
    return container;
}

// Confirmation dialog for logout
function confirmLogout() {
    return confirm('Are you sure you want to logout?');
}

// Add logout confirmation to logout link
document.addEventListener('DOMContentLoaded', function() {
    const logoutLink = document.querySelector('a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            if (!confirmLogout()) {
                e.preventDefault();
            }
        });
    }
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
