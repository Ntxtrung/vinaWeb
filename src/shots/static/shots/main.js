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

// Ensure these functions are available globally if needed
window.editShot = editShot;
window.cancelEdit = cancelEdit;
