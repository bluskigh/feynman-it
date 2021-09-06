var addFlash = null;
document.addEventListener('DOMContentLoaded', function() {

    const flashContainer = document.querySelector('#messages');
    function removeFlash(button) {
        // button.parentElement = div.message
        flashContainer.removeChild(button.parentElement)
    }

    document.querySelectorAll('.message button').forEach(item => {item.addEventListener('click', ()=>{removeFlash(item)})})

    addFlash = () => {
        const flash = document.createElement('div');
        flash.classList.add('message')
        flash.classList.add('success')
        const header = document.createElement('h5');
        header.innerText = 'Successfully created note';
        flash.appendChild(header)
        const remove = document.createElement('button');
        remove.innerHTML = '<strong>x</strong>';
        remove.addEventListener('click', () => {removeFlash(remove)})
        flash.appendChild(remove)
        flashContainer.appendChild(flash)
    }

    if (document.body.clientWidth <= 500) {
        const navButton = document.querySelector('#responsive-nav-button');
        navButton.addEventListener('click', function() {
            const ul = navButton.nextElementSibling;
            ul.style.display = ul.style.display == 'none' ? 'initial' : 'none';
        })
    }

})
