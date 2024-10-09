console.log('form_package.js loaded');
let selectedCell = null; // Variable to store the selected cell

// Function to handle cell click event
function handleCellClick(event) {
    selectedCell = event.target.closest('td'); // Store the clicked cell
    console.log('Selected cell:', selectedCell); // Log the selected cell
}

// Function to attach click event listeners to table cells
function attachCellClickListeners() {
    document.querySelectorAll('#shot-table tbody td').forEach(cell => {
        cell.removeEventListener('click', handleCellClick); // Prevent duplicate listeners
        cell.addEventListener('click', handleCellClick);
    });
}

// Initially attach the cell click listeners
attachCellClickListeners();

// Function to update form indices in a row
function updateFormIndices(row, formIndex) {
    row.querySelectorAll('input, textarea, select').forEach(input => {
        // Update the name attribute
        input.name = input.name.replace(/form-(\d+|__prefix__)-/, `form-${formIndex}-`);
        // Update the id attribute
        input.id = input.id.replace(/id_form-(\d+|__prefix__)-/, `id_form-${formIndex}-`);
    });
}

// Function to parse clipboard data, preserving newlines within quotes
function parseClipboardData(clipboardData) {
    const rows = [];
    let currentRow = [];
    let currentCell = '';
    let insideQuotes = false;

    for (let i = 0; i < clipboardData.length; i++) {
        const char = clipboardData[i];

        if (char === '"') {
            insideQuotes = !insideQuotes; // Toggle the insideQuotes state
        } else if (char === '\n' && !insideQuotes) {
            currentRow.push(currentCell.trim());
            rows.push(currentRow);
            currentRow = [];
            currentCell = '';
        } else if (char === '\t' && !insideQuotes) {
            currentRow.push(currentCell.trim());
            currentCell = '';
        } else {
            currentCell += char; // Add character to the current cell
        }
    }

    // Add the last cell and row
    if (currentCell) {
        currentRow.push(currentCell.trim());
    }
    if (currentRow.length > 0) {
        rows.push(currentRow);
    }

    return rows;
}

// Function to handle paste event and add multiple rows if needed
function handlePaste(event) {
    event.preventDefault();

    if (!selectedCell) {
        console.log("No cell selected to paste into!");
        return;
    }

    const clipboardData = (event.clipboardData || window.clipboardData).getData('text');
    console.log("clipboardData: ", clipboardData);

    // Parse the clipboard data
    const rows = parseClipboardData(clipboardData);
    console.log("Parsed rows: ", rows);

    let startRowElement = selectedCell.closest('tr');
    let startRowIndex = [...startRowElement.parentNode.children].indexOf(startRowElement);
    let startColIndex = [...selectedCell.parentNode.children].indexOf(selectedCell);

    console.log('Start pasting from row:', startRowIndex, 'and column:', startColIndex);

    // Get the current total number of forms
    let totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
    let formCount = parseInt(totalFormsInput.value);

    // Save current state before pasting (if saveCurrentState function exists)
    if (typeof saveCurrentState === 'function') {
        saveCurrentState();
    }

    rows.forEach((rowData, rowOffset) => {
        let formIndex = startRowIndex + rowOffset;
        let targetRowElement = document.querySelector(`#shot-table tbody tr:nth-child(${formIndex + 1})`);

        if (!targetRowElement) {
            // Clone the template row if available, else clone the first row
            let templateRow = document.getElementById('empty-form-row') || document.querySelector('#shot-table tbody tr:first-child');
            let newRow = templateRow.cloneNode(true);

            // Clear input values
            newRow.querySelectorAll('input, textarea').forEach(input => {
                input.value = '';
            });

            // Update form indices
            updateFormIndices(newRow, formIndex);

            // Append the new row to the table
            document.querySelector('#shot-table tbody').appendChild(newRow);

            // Reattach event listeners to new cells
            attachCellClickListeners();
            attachPasteEventListeners();

            targetRowElement = newRow;

            // Update form count if necessary
            formCount = Math.max(formCount, formIndex + 1);
        }

        // Populate the row with data
        rowData.forEach((cellData, colOffset) => {
            let targetCellElement = targetRowElement.querySelector(`td:nth-child(${startColIndex + 1 + colOffset}) input, td:nth-child(${startColIndex + 1 + colOffset}) textarea`);
            if (targetCellElement) {
                targetCellElement.value = cellData.trim();
            }
        });
    });

    // Update TOTAL_FORMS
    totalFormsInput.value = formCount;
}

// Function to attach paste event listeners to inputs and textareas
function attachPasteEventListeners() {
    document.querySelectorAll('#shot-table tbody input, #shot-table tbody textarea').forEach(input => {
        input.removeEventListener('paste', handlePaste); // Prevent duplicate listeners
        input.addEventListener('paste', handlePaste);
    });
}

// Initially attach the paste event listeners
attachPasteEventListeners();

document.addEventListener('DOMContentLoaded', function () {
    const applyBulkDateBtn = document.getElementById('apply-bulk-date');
    const bulkDeliveryDateInput = document.getElementById('bulk-delivery-date');

    applyBulkDateBtn.addEventListener('click', function () {
        const selectedDate = bulkDeliveryDateInput.value;
        if (!selectedDate) {
            alert('Please select a date first.');
            return;
        }

        const deliveryDateInputs = document.querySelectorAll('#shot-table input[name$="-delivery_date"]');
        deliveryDateInputs.forEach(input => {
            input.value = selectedDate;
        });

        alert('Delivery date has been updated for all shots.');
    });
});