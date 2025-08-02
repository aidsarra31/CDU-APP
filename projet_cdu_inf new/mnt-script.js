// Global variables
let installationRowCount = 0;
const currentDepartment = 'MNT';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMntApplication();
});

function initializeMntApplication() {
    initializeInstallationTable();
}

// Navigation function
function navigateTo(page) {
    window.location.href = page;
}

// Installation Table Functions
function initializeInstallationTable() {
    const tableBody = document.getElementById('installation-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    // Add 6 initial rows similar to the image
    const initialTrains = ['T100', 'T200', 'T300', 'T400', 'T500', 'T600'];
    initialTrains.forEach(train => {
        addInstallationRow(train);
    });
}

function addInstallationRow(trainName = '') {
    const tableBody = document.getElementById('installation-table-body');
    const rowIndex = installationRowCount++;
    const train = trainName || `T${100 + rowIndex}`;
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>
            <input type="text" id="train_${rowIndex}" name="train" value="${train}" maxlength="10">
        </td>
        <td>
            <select id="situation_${rowIndex}" name="situation">
                <option value="">Select</option>
                <option value="PROD/TEC">PROD/TEC</option>
                <option value="PROD">PROD</option>
                <option value="TEC">TEC</option>
                <option value="MNT">MNT</option>
            </select>
        </td>
        <td>
            <input type="number" id="jours_arret_${rowIndex}" name="jours_arret" min="0" placeholder="Days" disabled>
        </td>
        <td>
            <input type="number" id="jours_arret_tdd_${rowIndex}" name="jours_arret_tdd" min="0" placeholder="TDD Days" class="mnt-field">
        </td>
        <td>
            <input type="number" id="nbr_declenchement_${rowIndex}" name="nbr_declenchement" min="0" placeholder="Count" class="mnt-field">
        </td>
        <td>
            <select id="tdd_${rowIndex}" name="tdd_situation" class="mnt-field">
                <option value="">-</option>
                <option value="MNT">MNT</option>
            </select>
        </td>
        <td>
            <select id="tp_${rowIndex}" name="tp_situation" disabled>
                <option value="">-</option>
                <option value="PROD">PROD</option>
            </select>
        </td>
        <td>
            <select id="ac_${rowIndex}" name="ac_situation" disabled>
                <option value="">-</option>
                <option value="PROD">PROD</option>
            </select>
        </td>
        <td>
            <select id="gt_${rowIndex}" name="gt_situation" disabled>
                <option value="">-</option>
                <option value="TEC">TEC</option>
            </select>
        </td>
        <td>
            <input type="text" id="observation_${rowIndex}" name="observation" placeholder="Quelques explications ou observations MNT" maxlength="150" class="mnt-field">
        </td>
    `;
    
    tableBody.appendChild(row);
}

function saveInstallationData() {
    const rows = document.querySelectorAll('#installation-table-body tr');
    const tableData = [];
    
    rows.forEach((row, index) => {
        const rowData = {};
        const inputs = row.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            if (input.value.trim() !== '') {
                rowData[input.name] = input.value;
            }
        });
        
        if (Object.keys(rowData).length > 0) {
            rowData.rowIndex = index;
            rowData.department = currentDepartment;
            rowData.timestamp = new Date().toISOString();
            tableData.push(rowData);
        }
    });
    
    if (tableData.length === 0) {
        alert('No data to save. Please fill in at least one row.');
        return;
    }
    
    console.log(`${currentDepartment} Installation Data Saved:`, tableData);
    showSuccessMessage(`${currentDepartment} installation data saved successfully! ${tableData.length} rows processed.`);
}

function clearInstallationTable() {
    if (confirm('Are you sure you want to clear all installation data?')) {
        const rows = document.querySelectorAll('#installation-table-body tr');
        rows.forEach(row => {
            const inputs = row.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.name === 'train') {
                    // Keep train names but clear values for other fields
                    return;
                }
                input.value = '';
            });
        });
        
        showSuccessMessage('Installation table cleared successfully!');
    }
}

function exportInstallationData() {
    const rows = document.querySelectorAll('#installation-table-body tr');
    const data = [];
    
    // Get headers
    const headers = ['Train', 'Situation', 'Jours d\'arrêt', 'Jours d\'arrêt TDD', 'Nombre de Déclenchements', 'TDD', 'TP', 'AC', 'GT', 'Observations'];
    data.push(headers);
    
    // Get row data
    rows.forEach(row => {
        const rowData = [];
        const inputs = row.querySelectorAll('input, select');
        inputs.forEach(input => {
            rowData.push(input.value || '');
        });
        data.push(rowData);
    });
    
    // Convert to CSV
    const csv = data.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentDepartment}_installation_status_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Utility Functions
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