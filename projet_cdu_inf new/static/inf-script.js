// Global variables
let currentINFSubtype = 'SUPPORT';

// Department-specific intervention types for INF
const infInterventions = {
    SUPPORT: [
        'USER_ASSISTANCE',
        'TECHNICAL_SUPPORT',
        'SOFTWARE_ISSUES',
        'HARDWARE_TROUBLESHOOTING',
        'SYSTEM_CONFIGURATION'
    ],
    BDD: [
        'DATABASE_MAINTENANCE',
        'DATA_BACKUP',
        'QUERY_OPTIMIZATION',
        'DATABASE_MIGRATION',
        'DATA_INTEGRITY_CHECK'
    ],
    NETWORK: [
        'NETWORK_CONFIGURATION',
        'CONNECTIVITY_ISSUES',
        'BANDWIDTH_OPTIMIZATION',
        'SECURITY_SETUP',
        'INFRASTRUCTURE_UPGRADE'
    ],
    TELECOM: [
        'PHONE_SYSTEM_MAINTENANCE',
        'COMMUNICATION_SETUP',
        'LINE_CONFIGURATION',
        'EQUIPMENT_INSTALLATION',
        'SIGNAL_OPTIMIZATION'
    ]
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeINFApplication();
});

function initializeINFApplication() {
    // Initialize INF form
    switchINFSubtype('SUPPORT');
    updateINFInterventions();
}

// Navigation function
function navigateTo(page) {
    window.location.href = page;
}

// INF Department Functions
function switchINFSubtype(subtype) {
    currentINFSubtype = subtype;
    
    // Update active tab
    document.querySelectorAll('.inf-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-subtype="${subtype}"]`).classList.add('active');
    
    // Update the subtype input field
    document.getElementById('inf-subtype').value = subtype;
    
    // Update interventions for the selected subtype
    updateINFInterventions();
}

function updateINFInterventions() {
    const interventionSelect = document.getElementById('inf-intervention');
    const selectedSubtype = currentINFSubtype;
    
    // Clear existing options
    interventionSelect.innerHTML = '<option value="">Select intervention type</option>';
    
    if (selectedSubtype && infInterventions[selectedSubtype]) {
        infInterventions[selectedSubtype].forEach(intervention => {
            const option = document.createElement('option');
            option.value = intervention;
            option.textContent = intervention.replace(/_/g, ' ').toLowerCase()
                .replace(/\b\w/g, l => l.toUpperCase());
            interventionSelect.appendChild(option);
        });
    }
}

function handleINFSubmit(event) {
    event.preventDefault();
    
    // Validate period format
    const periode = document.getElementById('inf-periode').value;
    const periodePattern = /^\d{6}$/;
    
    if (!periodePattern.test(periode)) {
        alert('Period must be in YYYYMM format (e.g., 202401)');
        return false;
    }
    
    // Validate year and month
    const year = parseInt(periode.substring(0, 4));
    const month = parseInt(periode.substring(4, 6));
    
    if (year < 2020 || year > 2030) {
        alert('Year must be between 2020 and 2030');
        return false;
    }
    
    if (month < 1 || month > 12) {
        alert('Month must be between 01 and 12');
        return false;
    }
    
    // Collect form data
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Add department and timestamp
    data.department = 'INF';
    data.subtype = currentINFSubtype;
    data.timestamp = new Date().toISOString();
    
    // Simulate data submission
    console.log('INF Department Data Submitted:', data);
    
    // Show success message
    showSuccessMessage(`INF ${currentINFSubtype} data submitted successfully!`);
    
    // Clear form
    event.target.reset();
    document.getElementById('inf-subtype').value = currentINFSubtype;
    updateINFInterventions();
    
    return false;
}

// Utility Functions
function clearForm() {
    const form = document.querySelector('.data-form');
    if (form) {
        form.reset();
        document.getElementById('inf-subtype').value = currentINFSubtype;
        updateINFInterventions();
        showSuccessMessage('Form cleared successfully!');
    }
}

function showSuccessMessage(message) {
    const successMessage = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    
    successText.textContent = message;
    successMessage.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        hideSuccessMessage();
    }, 3000);
}

function hideSuccessMessage() {
    const successMessage = document.getElementById('successMessage');
    successMessage.classList.remove('show');
}

// Form validation utilities
function validatePeriodFormat(period) {
    const periodePattern = /^\d{6}$/;
    if (!periodePattern.test(period)) {
        return { valid: false, message: 'Period must be in YYYYMM format (e.g., 202401)' };
    }
    
    const year = parseInt(period.substring(0, 4));
    const month = parseInt(period.substring(4, 6));
    
    if (year < 2020 || year > 2030) {
        return { valid: false, message: 'Year must be between 2020 and 2030' };
    }
    
    if (month < 1 || month > 12) {
        return { valid: false, message: 'Month must be between 01 and 12' };
    }
    
    return { valid: true, message: '' };
}

// Enhanced error handling
function handleError(error, context) {
    console.error(`Error in ${context}:`, error);
    
    let userMessage = 'An unexpected error occurred. Please try again.';
    
    if (error.message.includes('network')) {
        userMessage = 'Network error. Please check your connection and try again.';
    } else if (error.message.includes('validation')) {
        userMessage = 'Data validation failed. Please check your input and try again.';
    }
    
    alert(userMessage);
}