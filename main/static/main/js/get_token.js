var token = window.location.href.split('#')[1].split('&')[0];
token = token.substring(13);
if (token) {
    window.sessionStorage.setItem('token', token)
}
