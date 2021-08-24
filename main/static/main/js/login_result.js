document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#login-result-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault()

        // create inputs to store jwt information
        let token = window.location.href.split('#')[1].split('&')[0];

        token = token.substring(13); 

        window.sessionStorage.setItem('token', token)

        const tokenInput = document.createElement('input');
        tokenInput.setAttribute('name', 'token')
        tokenInput.value = token;
        tokenInput.style.display = 'none';
        tokenInput.style.height = '0px';
        tokenInput.style.width = '0px';
        tokenInput.style.position = 'absolute';
        tokenInput.style.zIndex = '-100';

        form.appendChild(tokenInput)

        form.submit()
    })
})