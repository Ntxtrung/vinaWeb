console.log('hello world from form_modal.js')

const formModal = document.getElementById('form-project-modal')
const openModalBtn = document.getElementById('open-modal-btn')
const cancelBtn = document.getElementById('cancel-btn')
const backdrop = document.getElementById('backdrop')

if (openModalBtn && formModal) {
    openModalBtn.addEventListener('click', () => {
        formModal.classList.remove('hidden')
    });
}

if (formModal && backdrop) {
    formModal.addEventListener('click', (e) => {
        if (e.target !== backdrop) return;
        formModal.classList.add('hidden')
    });
}

if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
        formModal.classList.add('hidden')
    })
}

