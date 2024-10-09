console.log('form_package.js loaded');
let selectedCell = null; // Biến lưu trữ ô được chọn

// Lắng nghe sự kiện click trên các ô của bảng
document.querySelectorAll('#shot-table tbody td').forEach(cell => {
    cell.addEventListener('click', function (event) {
        selectedCell = event.target.closest('td'); // Lưu trữ ô được nhấn
        console.log('Selected cell:', selectedCell); // Hiển thị ô được chọn trong console
    });
});

function updateFormIndices(row, formIndex) {
    row.querySelectorAll('input, textarea, select').forEach(input => {
        // Update the name attribute
        input.name = input.name.replace(/form-\d+-/, `form-${formIndex}-`);
        // Update the id attribute
        input.id = input.id.replace(/id_form-\d+-/, `id_form-${formIndex}-`);
    });
}

// Hàm để xử lý chuỗi clipboard và giữ lại \n trong dấu ""
function parseClipboardData(clipboardData) {
    const rows = [];
    let currentRow = [];
    let currentCell = '';
    let insideQuotes = false;

    for (let i = 0; i < clipboardData.length; i++) {
        const char = clipboardData[i];

        if (char === '"') {
            insideQuotes = !insideQuotes; // Chuyển trạng thái khi gặp dấu "
        } else if (char === '\n' && !insideQuotes) {
            currentRow.push(currentCell.trim());
            rows.push(currentRow);
            currentRow = [];
            currentCell = '';
        } else if (char === '\t' && !insideQuotes) {
            currentRow.push(currentCell.trim());
            currentCell = '';
        } else {
            currentCell += char; // Thêm ký tự vào ô hiện tại
        }
    }

    // Thêm ô cuối cùng và hàng cuối cùng
    if (currentCell) {
        currentRow.push(currentCell.trim());
    }
    if (currentRow.length > 0) {
        rows.push(currentRow);
    }

    return rows;
}

// Lắng nghe sự kiện dán và thêm nhiều dòng nếu cần
function handlePaste(event) {
    event.preventDefault();

    if (!selectedCell) {
        console.log("No cell selected to paste into!");
        return;
    }

    const clipboardData = (event.clipboardData || window.clipboardData).getData('text');
    console.log("clipboardData: ", clipboardData);

    // Gọi hàm để phân tích dữ liệu clipboard
    const rows = parseClipboardData(clipboardData);
    console.log("Parsed rows: ", rows);

    let startRowIndex = [...selectedCell.closest('tr').parentNode.children].indexOf(selectedCell.closest('tr'));
    let startColIndex = [...selectedCell.parentNode.children].indexOf(selectedCell);

    console.log('Start pasting from row:', startRowIndex, 'and column:', startColIndex);

    // let formCount = document.querySelectorAll('#shot-table tbody tr').length;
    let formCount = parseInt(document.getElementById('id_form-TOTAL_FORMS').value);

    // Lưu trạng thái trước khi dán
    saveCurrentState();

    // rows.forEach((rowData, rowOffset) => {
    //     let targetRowElement = document.querySelector(`#shot-table tbody tr:nth-child(${startRowIndex + 1 + rowOffset})`);
    //     if (!targetRowElement) {
    //         let newRow = selectedCell.closest('tr').cloneNode(true); // Clone dòng nếu cần thêm
    //         newRow.querySelectorAll('input, textarea').forEach(input => {
    //             input.value = '';
    //         });
    //         document.querySelector('#shot-table tbody').appendChild(newRow);
    //         targetRowElement = newRow;
    //     }
    //     rowData.forEach((cellData, colOffset) => {
    //         let targetCellElement = document.querySelector(`#shot-table tbody tr:nth-child(${startRowIndex + 1 + rowOffset}) td:nth-child(${startColIndex + 1 + colOffset}) input, #shot-table tbody tr:nth-child(${startRowIndex + 1 + rowOffset}) td:nth-child(${startColIndex + 1 + colOffset}) textarea`);
    //         if (targetCellElement) {
    //             targetCellElement.value = cellData.trim(); // Dán giá trị vào ô tương ứng
    //         }
    //     });


    // });

    rows.forEach((rowData, rowOffset) => {
        let formIndex = formCount + rowOffset;
        let newRow = selectedCell.closest('tr').cloneNode(true);

        // Clear input values
        newRow.querySelectorAll('input, textarea').forEach(input => {
            input.value = '';
        });

        // Update form indices
        updateFormIndices(newRow, formIndex);

        // Append the new row to the table
        document.querySelector('#shot-table tbody').appendChild(newRow);

        // Populate the new row with data
        rowData.forEach((cellData, colOffset) => {
            let targetCellElement = newRow.querySelector(`td:nth-child(${startColIndex + 1 + colOffset}) input, td:nth-child(${startColIndex + 1 + colOffset}) textarea`);
            if (targetCellElement) {
                targetCellElement.value = cellData.trim();
            }
        });
    });

    document.getElementById('id_form-TOTAL_FORMS').value = formCount + rows.length - 1;


}


// Áp dụng hàm dán cho tất cả các cột trong bảng
document.querySelectorAll('#shot-table tbody input, #shot-table tbody textarea').forEach(input => {
    input.addEventListener('paste', handlePaste);
});

