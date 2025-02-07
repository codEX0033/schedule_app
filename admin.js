document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const adminPanel = document.getElementById('adminPanel');
    
    document.getElementById('adminLoginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            username: document.getElementById('adminLogin').value,
            password: document.getElementById('adminPassword').value
        };

        try {
            const response = await fetch('https://cindycate08.pythonanywhere.com/api/v1/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                loginForm.style.display = 'none';
                adminPanel.style.display = 'block';
                loadRequests();
            } else {
                const data = await response.json();
                alert(data.error || 'Неверный логин или пароль');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Ошибка при входе');
        }
    });
});

async function loadRequests() {
    try {
        const response = await fetch('https://cindycate08.pythonanywhere.com/api/v1/admin/requests', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load requests');
        }

        const requests = await response.json();
        displayRequests(requests);
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при загрузке заявок');
    }
}

function displayRequests(requests) {
    const requestsList = document.getElementById('requestsList');
    requestsList.innerHTML = '';

    requests.forEach(request => {
        const requestElement = document.createElement('div');
        requestElement.className = 'request-item';
        requestElement.innerHTML = `
            <div class="request-info">
                <p><strong>ФИО:</strong> ${request.fio}</p>
                <p><strong>Класс:</strong> ${request.class}</p>
                <p><strong>Логин:</strong> ${request.login}</p>
                <p><strong>Код учреждения:</strong> ${request.org_key}</p>
            </div>
            <div class="request-actions">
                <button class="approve-btn" onclick="handleRequest(${request.id}, true)">Подтвердить</button>
                <button class="reject-btn" onclick="handleRequest(${request.id}, false)">Отклонить</button>
            </div>
        `;
        requestsList.appendChild(requestElement);
    });
}

async function handleRequest(requestId, approve) {
    try {
        const response = await fetch('https://cindycate08.pythonanywhere.com/api/v1/admin/handle_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request_id: requestId,
                approve: approve
            })
        });

        if (!response.ok) {
            throw new Error('Failed to handle request');
        }

        loadRequests();
        alert(approve ? 'Заявка подтверждена' : 'Заявка отклонена');
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при обработке заявки');
    }
}

async function uploadSchedule() {
    const daySelect = document.getElementById('daySelect');
    const fileInput = document.getElementById('scheduleFile');
    
    if (!daySelect.value || !fileInput.files[0]) {
        alert('Пожалуйста, выберите день недели и файл расписания');
        return;
    }

    const formData = new FormData();
    formData.append('day', daySelect.value);
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('https://cindycate08.pythonanywhere.com/api/v1/admin/upload_schedule', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            alert('Расписание успешно загружено!');
            daySelect.value = '';
            fileInput.value = '';
        } else {
            throw new Error(data.error || 'Ошибка при загрузке расписания');
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
} 