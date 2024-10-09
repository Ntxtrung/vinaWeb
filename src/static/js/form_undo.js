console.log('form_undo.js loaded');
let undoStack = [];

// Hàm lưu trạng thái hiện tại
function saveCurrentState() {
    let formData = {
        totalForms: document.getElementById('id_form-TOTAL_FORMS').value,
        rowCount: document.querySelectorAll('#shot-table tbody tr').length,
        changedFields: {} // Chỉ lưu các trường thay đổi
    };

    // Lấy tất cả các giá trị của các trường trong form và bảng
    document.querySelectorAll('input, textarea, select').forEach(input => {
        let key = input.id || input.name;
        if (key) {
            formData.changedFields[key] = {
                value: input.value,
                type: input.type === "checkbox" || input.type === "radio" ? input.checked : input.value
            };
        }
    });

    undoStack.push(formData);

    // In ra console để kiểm tra
    console.log("Saved state with rowCount:", formData.rowCount);
    console.log("Current undo stack:", undoStack);
}

// Khôi phục trạng thái trước đó khi người dùng nhấn Ctrl+Z
function undoLastAction() {
    if (undoStack.length > 0) {
        let previousState = undoStack.pop();

        // Khôi phục tổng số form
        if (previousState.totalForms) {
            document.getElementById('id_form-TOTAL_FORMS').value = previousState.totalForms;
        }

        // Khôi phục số lượng hàng
        let currentRowCount = document.querySelectorAll('#shot-table tbody tr').length;
        let tbody = document.querySelector('#shot-table tbody');

        if (previousState.rowCount > currentRowCount) {
            let lastRow = tbody.querySelector('tr:last-child');
            for (let i = currentRowCount; i < previousState.rowCount; i++) {
                let newRow = lastRow.cloneNode(true);
                newRow.querySelectorAll('input, textarea').forEach(input => {
                    input.value = ''; // Khởi tạo các giá trị rỗng cho hàng mới
                });
                tbody.appendChild(newRow);
            }
        } else if (previousState.rowCount < currentRowCount) {
            for (let i = currentRowCount; i > previousState.rowCount; i--) {
                tbody.removeChild(tbody.lastChild);
            }
        }

        // Khôi phục các giá trị đã thay đổi
        for (let [key, state] of Object.entries(previousState.changedFields)) {
            let input = document.querySelector(`#${key}, [name="${key}"]`);
            if (input) {
                if (input.type === "checkbox" || input.type === "radio") {
                    input.checked = state.type;
                } else {
                    input.value = state.value;
                }
            }
        }
    }

    // In ra console để kiểm tra sau khi undo
    console.log("Current undo stack after undo:", undoStack);
}

// Lắng nghe sự kiện nhấn phím
document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'z') {
        undoLastAction();
    }
});
