console.log('hello world from base dir')

document.addEventListener('DOMContentLoaded', function () {
    const bulkDateBtn = document.getElementById('bulk-delivery-date-btn');
    const bulkDateInput = document.getElementById('bulk-delivery-date');

    bulkDateBtn.addEventListener('click', function () {
        bulkDateInput.showPicker();
    });

    bulkDateInput.addEventListener('change', function () {
        const selectedDate = this.value;
        // Cập nhật tất cả các input date của shot với giá trị này
        document.querySelectorAll('input[name$="-delivery_date"]').forEach(input => {
            input.value = selectedDate;
        });

    });
});

document.addEventListener('DOMContentLoaded', function () {
    const bulkStatusSelect = document.getElementById('bulk-status');

    bulkStatusSelect.addEventListener('change', function () {
        const selectedStatus = this.value;
        if (selectedStatus) {
            document.querySelectorAll('select[name$="-status"]').forEach(select => {
                select.value = selectedStatus;
            });
        }
    });
});


document.getElementById('copyToClipboard').addEventListener('click', function () {
    // Lấy tên package từ phần tử ẩn
    var packageName = document.getElementById('packageName').value;

    // Khởi tạo mảng để lưu các cột MD có giá trị
    var mdColumns = [];
    var headerRow = "\t";

    // Lấy dữ liệu từ bảng
    var table = document.getElementById('shot-table');
    var rows = table.getElementsByTagName('tr');
    var headerCells = rows[0].getElementsByTagName('th');

    // Kiểm tra các cột MD có giá trị
    for (var i = 1; i < headerCells.length - 3; i++) { // Bỏ qua cột Shot Name và 2 cột cuối
        var hasValue = false;
        for (var j = 1; j < rows.length; j++) {
            var cell = rows[j].getElementsByTagName('td')[i];
            var input = cell.getElementsByTagName('input')[0];
            if (input && input.value && input.value !== '0') {
                hasValue = true;
                break;
            }
        }
        if (hasValue) {
            mdColumns.push(i);
            headerRow += headerCells[i].textContent.trim() + "\t";
        }
    }

    // Tạo header
    var data = packageName + "-2024-10-22" + headerRow + "\n";

    // Lấy dữ liệu từ các hàng
    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        var rowData = cells[0].getElementsByTagName('input')[0].value + "\t"; // Shot Name

        for (var j = 0; j < mdColumns.length; j++) {
            var input = cells[mdColumns[j]].getElementsByTagName('input')[0];
            rowData += (input.value || '0') + "\t";
        }

        data += rowData.trim() + "\n";
    }

    // Đặt dữ liệu vào textarea ẩn
    var copyArea = document.getElementById('copyArea');
    copyArea.value = data;

    // Chọn và sao chép text
    copyArea.select();
    document.execCommand('copy');

    // Thông báo cho người dùng
    var notification = document.getElementById('copyNotification');
    notification.textContent = 'Data copied to clipboard!';
    notification.classList.remove('hidden');
    setTimeout(function () {
        notification.classList.add('hidden');
    }, 2000);
});