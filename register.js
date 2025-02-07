document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
        org_key: document.getElementById('orgKey').value,
        fio: document.getElementById('fio').value,
        class: document.getElementById('class').value,
        login: document.getElementById('login').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('https://cindycate08.pythonanywhere.com/api/v1/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            alert('Заявка на регистрацию отправлена успешно!');
            window.location.href = '/login.html';
        } else {
            alert(data.error || 'Ошибка при регистрации');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке данных');
    }
});

document.querySelector('.login-link a').addEventListener('click', function(e) {
    e.preventDefault();
    window.location.href = '/login.html';
}); 