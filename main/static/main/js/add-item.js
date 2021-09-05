var addNote = null;
document.addEventListener('DOMContentLoaded', function() {
    const notesContainer = document.querySelector('#items-flex-container');
    const newNoteTitle = document.querySelector('#id_title');
    const newNoteButton = document.querySelector('.new-item-form button');

    addNote = (id, title, route) => {
        try {
            const p = notesContainer.querySelector('p');
            notesContainer.removeChild(p)
        } catch(Exception) {
            // continue
        }

        const container = document.createElement('a'); 
        container.classList.add('item', 'item-animate')
        container.setAttribute('href', route)
        const shader = document.createElement('div');
        shader.classList.add('item-shader', 'hidden')
        const understandBar = document.createElement('div');
        understandBar.classList.add('understand-bar')
        const h5 = document.createElement('h5'); 
        h5.innerText = title;
        container.appendChild(shader)
        container.appendChild(understandBar)
        container.appendChild(h5)
        // notesContainer.appendChild(container)
        notesContainer.insertBefore(container, notesContainer.lastElementChild)
        newNoteTitle.value = "";

    }

    try {

        document.querySelector('.new-item-form').addEventListener('submit', function(e) {
            e.preventDefault()
            newNoteButton.disabled = true;
            fetch(this.getAttribute('action'), {
                method: 'POST', 
                mode: 'same-origin',
                headers: new Headers({
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                }), 
                body: JSON.stringify({
                    'title': newNoteTitle.value
                })
            })
            .then(async r => {
                const data = await r.json(); 
                if (r.status == 200) {
                    addNote(data.id, data.title, data.route)
                    addFlash()
                    // after adding, revert back to original stage in animation
                    itemAddClicked()
                    newNoteButton.disabled = false;
                } else if (r.status == 400) {
                    for (const error_key in data.errors) {
                        const error = document.createElement('p');
                        error.innerText = data.errors[error_key];
                        const row = document.createElement('tr');
                        const th = document.createElement('th');
                        const td = document.createElement('td');
                        td.appendChild(error)
                        row.appendChild(th)
                        row.appendChild(td)
                        newNoteBody.appendChild(row)
                    }
                }
            })
            .catch(e => {console.log(e)})
        })
    } catch(e) {}

})
