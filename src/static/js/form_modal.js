console.log('hello world from form_modal.js')

const formClientModal = document.getElementById('form-client-modal')
const formProjectModal = document.getElementById('form-project-modal')
const openClientModalBtn = document.getElementById('open-client-modal-btn')
const openProjectModalBtn = document.getElementById('open-project-modal-btn')
const cancelProjectBtn = document.getElementById('cancel-project-btn')
const canceClientBtn = document.getElementById('cancel-client-btn')
const backdropProject = document.getElementById('backdrop-project')
const backdropClient = document.getElementById('backdrop-client')
const clientSelect = document.querySelector('#client-select');

if (openClientModalBtn && formClientModal) {
    openClientModalBtn.addEventListener('click', () => {
        formClientModal.classList.remove('hidden')
    });
}

if (formClientModal && backdropClient) {
    formClientModal.addEventListener('click', (e) => {
        if (e.target !== backdropClient) return;
        formClientModal.classList.add('hidden')
    });
}

if (canceClientBtn) {
    canceClientBtn.addEventListener('click', () => {
        formClientModal.classList.add('hidden')
    })
}


if (openProjectModalBtn && formProjectModal) {
    openProjectModalBtn.addEventListener('click', function () {
        const clientId = clientSelect.value;
        if (!clientId) {
            alert('Vui lòng chọn một client trước khi tạo project.');
            return;
        }
        // Nếu đã chọn client, mở modal và set giá trị client_id
        document.querySelector('#project_client_id').value = clientId;
        formProjectModal.classList.remove('hidden');
    });
}

// Đóng modal khi click vào backdrop (nền mờ)
if (formProjectModal && backdropProject) {
    formProjectModal.addEventListener('click', (e) => {
        if (e.target !== backdropProject) return;
        formProjectModal.classList.add('hidden')
    });
}


// Đóng modal khi click nút cancel
if (cancelProjectBtn) {
    cancelProjectBtn.addEventListener('click', () => {
        formProjectModal.classList.add('hidden')
    })
}