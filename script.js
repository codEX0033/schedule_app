let selectedClass = '';
let selectedLetter = '';
let selectedDay = '';

document.querySelectorAll('.class button').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.class button').forEach(btn => btn.style.opacity = '1');
        this.style.opacity = '0.7';
        selectedClass = this.textContent;
    });
});

document.querySelectorAll('.litera button').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.litera button').forEach(btn => btn.style.opacity = '1');
        this.style.opacity = '0.7';
        selectedLetter = this.textContent;
    });
});

document.querySelectorAll('.day button').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.day button').forEach(btn => btn.style.opacity = '1');
        this.style.opacity = '0.7';
        selectedDay = this.textContent;
    });
});

const dayMapping = {
    'Пн': 'monday',
    'Вт': 'tuesday',
    'Ср': 'wednesday',
    'Чт': 'thursday',
    'Пт': 'friday'
};

document.querySelector('.button-blue-outline').addEventListener('click', async function() {
    if (!selectedClass || !selectedLetter || !selectedDay) {
        alert('Пожалуйста, выберите класс, букву и день недели');
        return;
    }

    const className = `${selectedClass}${selectedLetter}`;
    const day = dayMapping[selectedDay];

    try {
        const response = await fetch(`https://cindycate08.pythonanywhere.com/api/v1/get_schedule?class=${className}&day=${day}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        const tableBody = document.getElementById('scheduleBody');
        tableBody.innerHTML = '';
        
        data.forEach(lesson => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${lesson[0]}</td>
                <td>${lesson[2]}</td>
                <td>${lesson[1]}</td>
                <td>${lesson[3]}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при загрузке расписания');
    }
}); 