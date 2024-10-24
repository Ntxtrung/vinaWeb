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
    console.log(`Updating form indices for formIndex ${formIndex}`);
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
        console.log(`Processing row ${rowOffset + 1}`);
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

            // Log the cloned form for inspection
            console.log(`Cloned form for formIndex ${formIndex}:`, newRow);

            // Append the new row to the table
            document.querySelector('#shot-table tbody').appendChild(newRow);

            // Reattach event listeners to new cells
            attachCellClickListeners();
            attachPasteEventListeners();

            targetRowElement = newRow;

            // Update form count if necessary
            formCount = Math.max(formCount, formIndex + 1);

            console.log("New row added:", newRow);
        }

        // Populate the row with data
        rowData.forEach((cellData, colOffset) => {
            let targetCellElement = targetRowElement.querySelector(`td:nth-child(${startColIndex + 1 + colOffset}) input, td:nth-child(${startColIndex + 1 + colOffset}) textarea`);
            if (targetCellElement) {
                targetCellElement.value = cellData.trim();
            } else {
                console.log(`No target cell found for column index: ${startColIndex + 1 + colOffset}`);
            }
        });

        console.log(`Form ${formIndex} populated with data:`, rowData);
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
    const clientSelect = document.querySelector('#client-select');
    const projectSelect = document.querySelector('#project-select');
    const clientForm = document.querySelector('#client-form');
    const projectForm = document.querySelector('#project-form');
    const openProjectModalBtn = document.querySelector('#open-project-modal-btn');
    const closeProjectModalBtn = document.querySelector('#close-project-modal-btn');
    const projectModal = document.querySelector('#project-modal');

    // Hàm để cập nhật trạng thái của projectSelect
    function updateProjectSelectState() {
        if (clientSelect.value !== "") {
            fetch(`/api/projects/?client_id=${clientSelect.value}`)
                .then(response => response.json())
                .then(data => {
                    projectSelect.innerHTML = '<option value="">Chọn Project</option>';
                    data.forEach(project => {
                        const option = new Option(project.project_name, project.id);
                        projectSelect.add(option);
                    });
                    // Vô hiệu hóa projectSelect nếu không có project nào
                    projectSelect.disabled = data.length === 0;
                })
                .catch(error => {
                    console.error('Error fetching projects:', error);
                    projectSelect.innerHTML = '<option value="">Error loading projects</option>';
                    projectSelect.disabled = true;
                });
        } else {
            projectSelect.innerHTML = '<option value="">Chọn Project</option>';
            projectSelect.disabled = true;
        }
    }

    // Cập nhật trạng thái ban đầu
    updateProjectSelectState();

    if (projectForm) {
        projectForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(projectForm);

            // Đảm bảo client_id được thêm vào formData
            const clientId = clientSelect.value;
            // if (!clientId) {
            //     alert('Vui lòng chọn một client trước khi tạo project.');
            //     return;
            // }
            formData.append('client', clientId);

            console.log('FormData being sent:', Object.fromEntries(formData));  // Log để kiểm tra

            fetch('/api/create-project/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Server response:', data);  // Log response từ server
                    if (data.success) {
                        console.log('Server response:', data);
                        alert('Project created successfully!');
                        const option = new Option(data.project_name, data.project_id);
                        projectSelect.add(option);
                        projectSelect.value = data.project_id;
                        document.getElementById('form-project-modal').classList.add('hidden');
                        projectForm.reset();
                    } else {
                        console.error('Error creating project:', data.errors);
                        alert('Error creating project: ' + JSON.stringify(data.errors));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while creating the project.');
                });
        });
    }

    // Xử lý form tạo client bằng AJAX
    if (clientForm) {
        clientForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(clientForm);

            fetch('/api/create-client/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Client created successfully!');
                        const option = new Option(data.client_name, data.client_id);
                        clientSelect.add(option);
                        clientSelect.value = data.client_id;
                        document.getElementById('form-client-modal').classList.add('hidden');
                        updateProjectSelectState();
                    } else {
                        console.error('Error creating client:', data.errors);
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // Load project theo client được chọn
    clientSelect.addEventListener('change', function () {
        const clientId = this.value;
        if (clientId) {
            fetch(`/api/projects/?client_id=${clientId}`)
                .then(response => response.json())
                .then(data => {
                    projectSelect.innerHTML = '<option value="">Chọn Project</option>';
                    data.forEach(project => {
                        const option = new Option(project.project_name, project.id);
                        projectSelect.add(option);
                    });
                    // projectSelect.disabled = false;
                    updateProjectSelectState();
                })
                .catch(error => console.error('Error fetching projects:', error));
        } else {
            projectSelect.innerHTML = '<option value="">Chọn Project</option>';
            projectSelect.disabled = true;
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const packageNameInput = document.querySelector('input[name="package_name"]');
    const errorDiv = document.getElementById('package-name-error');
    const submitButton = document.querySelector('button[type="submit"]');

    function validatePackageName() {
        if (!packageNameInput.value.trim()) {
            packageNameInput.classList.add('border-red-500');
            errorDiv.textContent = 'Package name is required';
            submitButton.disabled = true;
        } else {
            packageNameInput.classList.remove('border-red-500');
            errorDiv.textContent = '';
            submitButton.disabled = false;
        }
    }

    if (packageNameInput) {
        packageNameInput.addEventListener('input', validatePackageName);
        packageNameInput.addEventListener('blur', validatePackageName);
    }

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (event) {
            if (!packageNameInput.value.trim()) {
                event.preventDefault();
                validatePackageName();
            }
        });
    }
});

// document.addEventListener('DOMContentLoaded', function () {
//     const bulkDateInput = document.getElementById('bulk-delivery-date');

//     if (bulkDateInput) {
//         bulkDateInput.addEventListener('change', function () {
//             const selectedDate = this.value;
//             const shotDateInputs = document.querySelectorAll('input[name$="-delivery_date"]');

//             console.log('Number of shot date inputs found:', shotDateInputs.length);

//             shotDateInputs.forEach((input, index) => {
//                 input.value = selectedDate;
//                 console.log(`Updated shot ${index + 1} with date:`, selectedDate);
//                 // Kích hoạt sự kiện 'change' để cập nhật bất kỳ logic nào khác dựa trên ngày
//                 input.dispatchEvent(new Event('change'));
//             });
//         });
//     } else {
//         console.error('Bulk date input not found');
//     }
// });

// document.addEventListener('DOMContentLoaded', function () {
//     const bulkDateBtn = document.getElementById('bulk-delivery-date-btn');
//     const bulkDateInput = document.getElementById('bulk-delivery-date');

//     bulkDateBtn.addEventListener('click', function () {
//         bulkDateInput.showPicker();
//     });

//     bulkDateInput.addEventListener('change', function () {
//         const selectedDate = this.value;
//         // Cập nhật tất cả các input date của shot với giá trị này
//         document.querySelectorAll('input[name$="-delivery_date"]').forEach(input => {
//             input.value = selectedDate;
//         });

//     });
// });

// document.addEventListener('DOMContentLoaded', function () {
//     const bulkStatusSelect = document.getElementById('bulk-status');

//     bulkStatusSelect.addEventListener('change', function () {
//         const selectedStatus = this.value;
//         if (selectedStatus) {
//             document.querySelectorAll('select[name$="-status"]').forEach(select => {
//                 select.value = selectedStatus;
//             });
//         }
//     });
// });

// document.addEventListener('DOMContentLoaded', function () {
//     const statusDropdownButton = document.getElementById('status-dropdown-button');
//     const statusDropdown = document.getElementById('status-dropdown');

//     // Mở/đóng dropdown
//     statusDropdownButton.addEventListener('click', function (event) {
//         event.stopPropagation();
//         statusDropdown.classList.toggle('hidden');
//     });

//     // Đóng dropdown khi click bên ngoài
//     document.addEventListener('click', function () {
//         statusDropdown.classList.add('hidden');
//     });

//     // Ngăn chặn việc đóng dropdown khi click vào nó
//     statusDropdown.addEventListener('click', function (event) {
//         event.stopPropagation();
//     });

//     // Xử lý việc chọn status
//     statusDropdown.querySelectorAll('a').forEach(item => {
//         item.addEventListener('click', function (event) {
//             event.preventDefault();
//             const selectedStatus = this.getAttribute('data-value');
//             document.querySelectorAll('select[name$="-status"]').forEach(select => {
//                 select.value = selectedStatus;
//             });
//             statusDropdown.classList.add('hidden');
//         });
//     });
// });
// document.addEventListener('DOMContentLoaded', function () {
//     // Lấy phần tử dropdown button và kiểm tra xem nó có tồn tại không
//     const statusDropdownButton = document.getElementById('status-dropdown-button');
//     if (statusDropdownButton) {
//         const statusDropdown = document.getElementById('status-dropdown');

//         if (statusDropdown) {
//             // Mở/đóng dropdown
//             statusDropdownButton.addEventListener('click', function (event) {
//                 event.stopPropagation();
//                 statusDropdown.classList.toggle('hidden');
//             });

//             // Đóng dropdown khi click bên ngoài
//             document.addEventListener('click', function () {
//                 statusDropdown.classList.add('hidden');
//             });

//             // Ngăn chặn việc đóng dropdown khi click vào nó
//             statusDropdown.addEventListener('click', function (event) {
//                 event.stopPropagation();
//             });

//             // Xử lý việc chọn status
//             statusDropdown.querySelectorAll('a').forEach(item => {
//                 item.addEventListener('click', function (event) {
//                     event.preventDefault();
//                     const selectedStatus = this.getAttribute('data-value');
//                     document.querySelectorAll('select[name$="-status"]').forEach(select => {
//                         select.value = selectedStatus;
//                     });
//                     statusDropdown.classList.add('hidden');
//                 });
//             });
//         } else {
//             console.error("Element with ID 'status-dropdown' not found");
//         }
//     } else {
//         console.error("Element with ID 'status-dropdown-button' not found");
//     }
// });
