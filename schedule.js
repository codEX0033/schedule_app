function initializeButtonStates() {
    const buttons = document.querySelectorAll('.schedule-button');
    
    buttons.forEach(button => {
        const buttonId = button.getAttribute('data-id');
        const isClicked = localStorage.getItem(`button_${buttonId}`) === 'true';
        
        if (isClicked) {
            button.classList.add('clicked');
        }
        
        button.addEventListener('click', function() {
            this.classList.toggle('clicked');
            
            const isNowClicked = this.classList.contains('clicked');
            localStorage.setItem(`button_${buttonId}`, isNowClicked);
        });
    });
}

function resetAllButtons() {
    localStorage.clear();
    location.reload();
}

document.addEventListener('DOMContentLoaded', initializeButtonStates); 