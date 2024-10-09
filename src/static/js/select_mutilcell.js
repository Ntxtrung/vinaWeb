console.log('form_package.js loaded');
let selectedCells = []; // Mảng chứa các ô được chọn
let lastSelectedCell = null; // Lưu ô cuối cùng được chọn để hỗ trợ chức năng chọn bằng Shift

// Lắng nghe sự kiện click trên các ô của bảng
document.querySelectorAll('#shot-table tbody td').forEach(cell => {
    cell.addEventListener('click', function (event) {
        if (event.ctrlKey) {
            // Chọn nhiều ô bằng Ctrl
            toggleCellSelection(cell);
        } else if (event.shiftKey && lastSelectedCell) {
            // Chọn một dải ô bằng Shift
            selectRange(lastSelectedCell, cell);
        } else {
            // Nếu không giữ Ctrl hoặc Shift, chỉ chọn một ô (và bỏ chọn các ô khác)
            clearSelection();
            toggleCellSelection(cell);
        }

        lastSelectedCell = cell; // Cập nhật ô cuối cùng được chọn
    });
});

// Lắng nghe sự kiện click ra ngoài bảng
document.addEventListener('click', function (event) {
    if (!event.target.closest('#shot-table')) {
        clearSelection();
    }
});

// Hàm để chọn/bỏ chọn một ô
function toggleCellSelection(cell) {
    if (cell.classList.contains('selected')) {
        cell.classList.remove('selected');
        selectedCells = selectedCells.filter(c => c !== cell);
    } else {
        cell.classList.add('selected');
        selectedCells.push(cell);
    }
    console.log('Selected cells:', selectedCells);
}

// Hàm để chọn một dải các ô từ ô bắt đầu đến ô kết thúc
function selectRange(startCell, endCell) {
    const startRowIndex = [...startCell.closest('tr').parentNode.children].indexOf(startCell.closest('tr'));
    const endRowIndex = [...endCell.closest('tr').parentNode.children].indexOf(endCell.closest('tr'));
    const startColIndex = [...startCell.parentNode.children].indexOf(startCell);
    const endColIndex = [...endCell.parentNode.children].indexOf(endCell);

    const minRowIndex = Math.min(startRowIndex, endRowIndex);
    const maxRowIndex = Math.max(startRowIndex, endRowIndex);
    const minColIndex = Math.min(startColIndex, endColIndex);
    const maxColIndex = Math.max(startColIndex, endColIndex);

    clearSelection(); // Xóa các ô đã chọn trước đó

    for (let i = minRowIndex; i <= maxRowIndex; i++) {
        for (let j = minColIndex; j <= maxColIndex; j++) {
            let cell = document.querySelector(`#shot-table tbody tr:nth-child(${i + 1}) td:nth-child(${j + 1})`);
            if (cell) {
                cell.classList.add('selected');
                selectedCells.push(cell);
            }
        }
    }

    console.log('Selected cells:', selectedCells);
}

// Thêm hàm mới để chọn range của các ô
function selectRange(start, end) {
    const startRow = start.parentElement;
    const endRow = end.parentElement;
    const startIndex = Array.from(startRow.children).indexOf(start);
    const endIndex = Array.from(endRow.children).indexOf(end);

    const rows = Array.from(document.querySelectorAll('#shot-table tbody tr'));
    const startRowIndex = rows.indexOf(startRow);
    const endRowIndex = rows.indexOf(endRow);

    for (let i = Math.min(startRowIndex, endRowIndex); i <= Math.max(startRowIndex, endRowIndex); i++) {
        const row = rows[i];
        for (let j = Math.min(startIndex, endIndex); j <= Math.max(startIndex, endIndex); j++) {
            const cell = row.children[j];
            if (!cell.classList.contains('selected')) {
                cell.classList.add('selected');
                selectedCells.push(cell);
            }
        }
    }
}

// Thêm hàm để xóa tất cả các lựa chọn
function clearSelection() {
    selectedCells.forEach(cell => cell.classList.remove('selected'));
    selectedCells = [];
    lastSelectedCell = null;
}

// Lắng nghe sự kiện copy (Ctrl + C)
document.addEventListener('copy', function (event) {
    if (selectedCells.length > 0) {
        event.preventDefault(); // Ngăn hành động copy mặc định

        let copiedData = '';
        let rows = {};

        selectedCells.forEach(cell => {
            const rowIndex = [...cell.closest('tr').parentNode.children].indexOf(cell.closest('tr'));
            const colIndex = [...cell.parentNode.children].indexOf(cell);

            if (!rows[rowIndex]) {
                rows[rowIndex] = [];
            }

            rows[rowIndex][colIndex] = cell.querySelector('input, textarea, select').value || '';
        });

        Object.keys(rows).forEach((rowIndex, i) => {
            copiedData += rows[rowIndex].join('\t');
            if (i < Object.keys(rows).length - 1) {
                copiedData += '\n';
            }
        });

        event.clipboardData.setData('text/plain', copiedData);
        console.log('Copied data: ', copiedData);
    }
});
