document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
        username: document.getElementById('login').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('https://cindycate08.pythonanywhere.com/api/v1/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = '/index.html';
        } else {
            alert(data.error || 'Ошибка при входе');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при входе');
    }
}); 