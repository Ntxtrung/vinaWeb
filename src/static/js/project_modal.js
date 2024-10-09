// console.log('hello world from form_modal.js')

// const formModal = document.getElementById('form-project-modal')
// const openModalBtn = document.getElementById('open-modal-btn')
// const cancelBtn = document.getElementById('cancel-btn')
// const backdrop = document.getElementById('backdrop')

// if (openModalBtn && formModal) {
//     openModalBtn.addEventListener('click', () => {
//         formModal.classList.remove('hidden')
//     });
// }

// if (formModal && backdrop) {
//     formModal.addEventListener('click', (e) => {
//         if (e.target !== backdrop) return;
//         formModal.classList.add('hidden')
//     });
// }

// if (cancelBtn) {
//     cancelBtn.addEventListener('click', () => {
//         formModal.classList.add('hidden')
//     })
// }

document.addEventListener('DOMContentLoaded', () => {
    console.log('hello world from form_modal.js')

    const formModal = document.getElementById('form-project-modal')
    const openModalBtn = document.getElementById('open-modal-btn')
    const cancelBtn = document.getElementById('cancel-btn')
    const projectForm = document.getElementById('project-form')

    // Mở modal khi click nút
    if (openModalBtn && formModal) {
        openModalBtn.addEventListener('click', () => {
            formModal.classList.remove('hidden')
        });
    }

    // Đóng modal khi click vào backdrop (nền mờ)
    formModal.addEventListener('click', (e) => {
        if (e.target.classList.contains('fixed')) {
            formModal.classList.add('hidden')
        }
    });

    // Đóng modal khi click nút cancel
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            formModal.classList.add('hidden')
        })
    }

    // Gửi form qua AJAX khi người dùng nhấn "Create"
    projectForm.addEventListener('submit', (e) => {
        e.preventDefault();  // Ngăn chặn form gửi theo cách mặc định

        const formData = new FormData(projectForm);  // Lấy dữ liệu từ form
        const actionUrl = projectForm.getAttribute('action');  // Lấy URL từ thuộc tính action của form

        fetch(actionUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert("Project created successfully: " + data.project_name);
                    formModal.classList.add('hidden');  // Ẩn modal sau khi tạo thành công
                } else {
                    alert("Error: " + JSON.stringify(data.errors));  // Hiển thị lỗi
                }
            })
            .catch((error) => {
                console.error('Error:', error);  // In lỗi ra console
            });

    })
})
