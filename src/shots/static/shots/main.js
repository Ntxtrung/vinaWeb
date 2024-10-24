console.log('hello world from shots dir')

document.addEventListener('DOMContentLoaded', function () {
    const monthSelect = document.getElementById('month-select');
    const yearSelect = document.getElementById('year-select');

    function updateURL() {
        const selectedMonth = monthSelect.value;
        const selectedYear = yearSelect.value;
        const currentPage = new URLSearchParams(window.location.search).get('page') || '1';
        let newPath = '/shots/';

        if (selectedYear) {
            newPath += `${selectedYear}/`;
            if (selectedMonth) {
                newPath += `${selectedMonth}/`;
            }
        }

        newPath += `?page=${currentPage}`;
        window.location.href = newPath;
    }

    if (monthSelect) {
        monthSelect.addEventListener('change', updateURL);
    }
    if (yearSelect) {
        yearSelect.addEventListener('change', updateURL);
    }
})

const goBackBtn = document.getElementById('go-back-btn');
if (goBackBtn) {
    goBackBtn.addEventListener('click', () => history.back());
}

const createPackageBtn = document.getElementById('create-package-btn');
if (createPackageBtn) {
    createPackageBtn.addEventListener('click', () => {
        window.location.href = '/shots/package/create/';
    });
}

function editShot(shotId) {
    // Ensure this function is defined and does something meaningful
    console.log("Editing shot with ID:", shotId);
    // Add your logic to handle the edit action
    // For example, show a form with shot details for editing
    const editForm = document.getElementById('editShotForm');
    const editShotIdInput = document.getElementById('editShotId');
    if (editForm && editShotIdInput) {
        editShotIdInput.value = shotId;
        editForm.classList.remove('hidden');
    }
}

function cancelEdit() {
    const editForm = document.getElementById('editShotForm');
    if (editForm) {
        editForm.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const summaryStatusSelect = document.getElementById('summary-status');
    const monthSelect = document.getElementById('month-select');
    const yearSelect = document.getElementById('year-select');

    summaryStatusSelect.addEventListener('change', function () {
        const month = monthSelect.value;
        const year = yearSelect.value;
        const summaryStatus = this.value;

        // Sử dụng fetch để lấy dữ liệu mới cho summary
        fetch(`/shots/summary/?month=${month}&year=${year}&status=${summaryStatus}`)
            .then(response => response.json())
            .then(data => {
                // Cập nhật các giá trị trong bảng summary
                updateSummaryTable(data);
            });
    });

    function updateSummaryTable(data) {
        // Cập nhật Studio8FX row
        document.getElementById('studio8fx-roto').textContent = data.studio8fx_md.roto;
        document.getElementById('studio8fx-paint').textContent = data.studio8fx_md.paint;
        document.getElementById('studio8fx-track').textContent = data.studio8fx_md.track;
        document.getElementById('studio8fx-comp').textContent = data.studio8fx_md.comp;

        // Cập nhật Others row
        document.getElementById('others-roto').textContent = data.other_md.roto;
        document.getElementById('others-paint').textContent = data.other_md.paint;
        document.getElementById('others-track').textContent = data.other_md.track;
        document.getElementById('others-comp').textContent = data.other_md.comp;

        // Cập nhật Total row
        document.getElementById('total-roto').textContent = data.total_md.roto;
        document.getElementById('total-paint').textContent = data.total_md.paint;
        document.getElementById('total-track').textContent = data.total_md.track;
        document.getElementById('total-comp').textContent = data.total_md.comp;
    }
});

// Ensure these functions are available globally if needed
window.editShot = editShot;
window.cancelEdit = cancelEdit;
