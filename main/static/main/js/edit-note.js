document.addEventListener('DOMContentLoaded', function() {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const customHeaders = {"X-CSRFToken": csrftoken, "Content-Type": "application/json", "Authorization": `Bearer ${window.sessionStorage.getItem('token')}`};
    const noteid = parseInt(document.querySelector('[name=noteid]').value);

    const linkWhich = document.querySelector('#links-data #forwhich');

    const brain = document.querySelector('nav img');

    function addPending(item) {
        item.classList.add('pending')
        item.disabled = true;
    }
    function removePending(item) {
        item.classList.remove('pending')
        item.disabled = false;
    }

    function sleep() {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                resolve()
            }, 1000)
        })
    }

    async function learningAnimation() {
        if (brain.style.opacity == '0.5') {
            brain.style.opacity = '1';
        } else {
            brain.style.opacity = '0.5';
        }
        await sleep()
        learningAnimation()
    }
    learningAnimation()

    const stepOneIterationsContainer = document.querySelector('#step_one_iterations_container');
    const stepTwoIterationsContainer = document.querySelector('#step_two_iterations_container');

    ///////////////////
    // Adding 
    ///////////////////
    function addIteration(title, text, which, id) {
        /*
        <div class="table-data note-iteration">
            <h4>{{title}}</h4>
            <div class="data">
                <p>{{text}}</p>
                {{ edit button here}}
                >>> links here
            </div>
        </div>
        */

        let parentContainer = null; 
        if (which == 1) {
            parentContainer = stepOneIterationsContainer;
        } else if (which == 2) {
            parentContainer = stepTwoIterationsContainer;
        }

        // if (parentContainer.querySelector('.nomessage')) {
        //     parentContainer.removeChild(parentContainer.querySelector('.nomessage'))
        // }

        const lastIteration = parentContainer.lastElementChild.previousElementSibling;
        let count = null;

        if (lastIteration) { 
            count = parseInt(lastIteration.dataset.iteration) + 1;
        } else {
            count = 1;
        }

        // Adds an iteration to specified iteration container
        const container = document.createElement('div');
        container.dataset.id = id;
        container.dataset.iteration = count;
        container.classList.add('table-data')
        container.classList.add('note-iteration')

        const data = document.createElement('div');
        data.classList.add('data')

        const titleTag = document.createElement('h4'); 
        titleTag.innerHTML = `<span class="iteration-count">(${count})</span> <span class="iteration-title">${title}</span>`;

        const textTag = document.createElement('p');
        textTag.classList.add('iteration-text')
        textTag.innerText = text;

        let links = null;
        let nomessage = null;
        if (parentContainer == stepOneIterationsContainer) {
            links = document.createElement('div');
            links.classList.add('links')
            nomessage = document.createElement('p');
            nomessage.classList.add('nomessage')
            nomessage.innerText = 'No links.'
        }

        const editButton = document.createElement('button');
        editButton.style.marginRight = ".5em";
        editButton.setAttribute('type', 'button')
        editButton.classList.add('edit-iteration')
        editButton.addEventListener('click', ()=>{useEditForm(id)})
        editButton.innerText = 'Edit';

        const deleteButton = document.createElement('button');
        deleteButton.setAttribute('type', 'button')
        deleteButton.classList.add('delete-iteration')
        deleteButton.classList.add('dangerous')
        deleteButton.innerText = 'Delete';
        deleteButton.addEventListener('click', ()=>{deleteIteration(id, deleteButton)})


        data.appendChild(textTag)
        data.appendChild(editButton)
        data.appendChild(deleteButton)
        if (parentContainer == stepOneIterationsContainer) {
            const hr = document.createElement('hr');
            hr.classList.add('links-separator')
            data.appendChild(hr)
            links.appendChild(nomessage)
            data.appendChild(links)
        }
        container.appendChild(titleTag)
        container.appendChild(data)

        parentContainer.insertBefore(container, parentContainer.lastElementChild)

        // add a new option to select forwhich field
        const option = document.createElement('option'); 
        option.setAttribute('value', id)
        option.innerText = `Iteration: ${count}`;
        linkWhich.appendChild(option)
    }

    const iterationOneFormButton = document.querySelector('#iteration-one-form .add-button');
    const iterationTwoFormButton = document.querySelector('#iteration-two-form .add-button');
    [iterationOneFormButton, iterationTwoFormButton].forEach(item => {
        item.addEventListener('click', function(e) {
            // #iteration-one-form
            const parentForm = this.parentElement;
            const titleValue = parentForm.querySelector('input').value;
            const textValue = parentForm.querySelector('textarea').value;

            addPending(e.target)

            if (titleValue.length == 0 || textValue.length == 0) {
                return;
            }

            let which = 1;

            if (parentForm.parentElement == stepTwoIterationsContainer) {
                which = 2;
            }

            fetch('/iterations/', {
                method: "POST",
                mode: "same-origin",
                headers: new Headers(customHeaders),
                body: JSON.stringify({
                    'noteid': noteid, 'title': titleValue, 'text': textValue, 'which': which
                })
            })
            .then(async r => {
                if (r.status == 400) {
                    // invalid values were given
                    alert('Could not add iteration, invalid values were given.')
                } else {
                    return await r.json()
                }
            })
            .then(r => {
                // successfully added the iteration 
                if (r.id) {
                    // attempt to remove no message direct child from main iteration container 
                    try {
                        if (parentForm.parentElement.querySelector('.nomessage')) {
                            parentForm.parentElement.removeChild(parentForm.parentElement.querySelector('.nomessage'))
                        }
                    } catch(e) { console.log(e) }
                    addIteration(titleValue, textValue, which, r.id)
                    // clear inputs
                    parentForm.querySelector('input').value = "";
                    parentForm.querySelector('textarea').value = "";
                    console.log(e.target)
                    removePending(e.target)
                } else {alert('Error: Did not recieve id.');removePending(e.target)}
            })
            .catch(e => {
                console.log(e);
            })
        })
    })


    ///////////////////
    // Adding Links
    ///////////////////
    function addLink(title, href, which, id) {
        console.log(title, href, which, id)
        /*
        <div class="link-container">
            <div class="data">
                .. title etc here, edit buttons and what not
            </div>
            .. here is where we would append or insert the edit form
        */

       const linkContainer = document.createElement('div');
       linkContainer.dataset.linkid = id;
       linkContainer.classList.add('link-container')

       const linkData = document.createElement('div');
       linkData.classList.add('data')

       const link = document.createElement('a');
       link.setAttribute('href', href)
       link.setAttribute('target', '_blank')
       link.innerText = title;

       const editButton = document.createElement('button');
       editButton.classList.add('edit-link')
       editButton.setAttribute('type', 'button')
       editButton.innerText = 'Edit';
       editButton.style.marginLeft = '.5em';
       editButton.style.marginRight = '.5em';
       editButton.addEventListener('click', ()=>{useEditForm(id, true)})

       const deleteButton = document.createElement('button');
       deleteButton.classList.add('dangerous')
       deleteButton.classList.add('delete-link')
       deleteButton.innerText = 'Delete';
       deleteButton.addEventListener('click', () => {deleteLink(id, deleteButton)})
       deleteButton.setAttribute('type', 'button')

       linkData.appendChild(link)
       linkData.appendChild(editButton)
       linkData.appendChild(deleteButton)
       linkContainer.appendChild(linkData)

       let parentContainer = null;
       if (which == 0) {
           parentContainer = document.querySelector('#general-links').querySelector('.links');
       } else {
           parentContainer = document.querySelector(`[data-id="${which}"]`).querySelector('.links');
       }
       if (parentContainer.querySelector('.nomessage')) {
           parentContainer.removeChild(parentContainer.querySelector('.nomessage'))
       }
       parentContainer.appendChild(linkContainer)
    }


    const linksAddButton = document.querySelector('#links-data .add-button'); 
    const linkTitle = document.querySelector('#link-title');
    const linkHref = document.querySelector('#links-data textarea');
    linksAddButton.addEventListener('click', function() {
        // saving the values so if user changes them after adding and we are still processing we can use the values used when submitted
        const which = parseInt(linkWhich.value);
        const title = linkTitle.value.trim();
        const href = linkHref.value.trim();

        addPending(linksAddButton)

        if (title.length == 0 || href.length == 0) {
            return;
        }

        // clear the link form fields
        linkHref.value = "";
        linkTitle.value = "";
        fetch('/links/', {
            method: "POST",
            mode: "same-origin",
            headers: new Headers(customHeaders),
            body: JSON.stringify({
                title, href, which, 'noteid': parseInt(noteid)
            })
        })
        .then(async r => {
            if (r.status == 400) {
                alert(r.message)
                this.disabled = false;
            } else if (r.status == 200) {
                return await r.json()
            }
        })
        .then(r => {
            // ad the link to the relative iteration
            addLink(title, href, which, r.id)
            removePending(linksAddButton)
        }).catch((e) => {removePending(linksAddButton)})
    })

    ///////////////////
    // Deleting Links 
    ///////////////////
    function deleteLink(linkId, item) {
        const linkContainer = document.querySelector(`[data-linkid="${linkId}"]`);
        fetch(`/links/${parseInt(linkId)}/`, {
            method: 'DELETE',
            mode: 'same-origin',
            headers: new Headers(customHeaders)
        })
        .then(r => {
            if (r.status == 400) {
                alert('Could not delete link!')
            } else {
                // remove link container
                removePending(item)
                linkContainer.parentElement.removeChild(linkContainer)
            }
        })
    }
    document.querySelectorAll('.delete-link').forEach(item => 
        addPending(item)
        item.addEventListener('click', ()=>{deleteLink(item.parentElement.parentElement.dataset.linkid, item)})
    )

    ///////////////////
    // Editing
    ///////////////////
    const editForm = document.querySelector('#edit-iteration-container');
    const editInput = editForm.querySelector('input');
    const editText = editForm.querySelector('textarea');

    function resetEditForm() {
        // clear inputs and hide
        editInput.value = ""; 
        editText.value = "";
        // hide the form
        editForm.classList.add('display-none')
        // reveal the data form it is replacing in .table-data
        editForm.parentElement.querySelector('.data').classList.remove('display-none')
        // move to body
        document.querySelector('body').appendChild(editForm)
    }

    editForm.querySelector('.close').addEventListener('click', function() {
        resetEditForm()
    })

    editForm.querySelector('.save').addEventListener('click', function(e) {
        if (editInput.value.length == 0 || editText.value.length == 0) {
            return;
        }

        const titleValue = window.localStorage.getItem('editInputOriginal') == editInput.value.trim() ? null : editInput.value;
        const textValue = window.localStorage.getItem('editTextOriginal') == editText.value.trim() ? null : editText.value;

        // did not change anything do not make unnecessary request to server
        if (titleValue == null && textValue == null) {
            return;
        }

        let iterationId = null;
        let route = null;
        let body = {'title': titleValue, 'text': textValue};
        let dataQuery = null;

        if (this.parentElement.parentElement.classList.contains('link-container')) {
            iterationId = this.parentElement.parentElement.dataset.linkid;
            route = `/links/${iterationId}/`;
            body['which'] = linkWhich.value;
            dataQuery = `[data-linkid="${iterationId}"]`;
        } else {
            iterationId = this.parentElement.parentElement.dataset.id; 
            route = `/iterations/${iterationId}/`;
            dataQuery = `[data-id="${iterationId}"]`;
        }

        addPending(e.target)

        fetch(route, {
            method: "PATCH",
            mode: "same-origin",
            headers: new Headers(customHeaders),
            body: JSON.stringify(body)
        })
        .then(async r => {
            if (r.status == 400) {
                alert('Could not save edit!') 
            } else {
                // save updated into relative fields
                const parent = document.querySelector(dataQuery);
                try {
                    parent.querySelector('.iteration-title').innerText = editInput.value.trim();
                    parent.querySelector('.iteration-text').innerText = editText.value.trim();
                } catch(e) {
                    parent.querySelector('.data').querySelector('a').innerText = editInput.value.trim();
                    parent.querySelector('.data').querySelector('a').setAttribute('href', editText.value.trim())
                }
                resetEditForm()
                removePending(e.target)
            }
        })
    })

    function useEditForm(iterationId, islink=false) {
        resetEditForm()
        const tableData = document.querySelector(`[data-${islink?"linkid":"id"}="${iterationId}"]`)
        const data = tableData.querySelector('.data');
        // move the form to iteration to last child of .table-data
        tableData.insertBefore(editForm, tableData.lastElementChild)
        // then hide .data of .table-data
        data.classList.add('display-none')
        // fill editForm input/textarea with iteration title and text
        if (islink) {
            editInput.value = data.querySelector('a').innerText;
            editText.value = data.querySelector('a').getAttribute('href');
        } else {
            editInput.value = tableData.querySelector('.iteration-title').innerText;
            editText.value = data.querySelector('.iteration-text').innerText;
        }
        // reveal the editForm
        editForm.classList.remove('display-none')
        window.localStorage.setItem('editInputOriginal', editInput.value)
        window.localStorage.setItem('editTextOriginal', editText.value)
    }

    const editButtons = document.querySelectorAll('.note-iteration .edit-iteration');
    editButtons.forEach(item => {
        item.addEventListener('click', ()=>{
            const iterationId = item.parentElement.parentElement.dataset.id; 
            useEditForm(iterationId)
        })
    })
    const editLinkButtons = document.querySelectorAll('.edit-link');
    editLinkButtons.forEach(item => {
        item.addEventListener('click', () => {
            const iterationId = item.parentElement.parentElement.dataset.linkid; 
            useEditForm(iterationId, islink=true)
        })
    })


    ///////////////////
    // Deleting
    ///////////////////
    function removeIteration(iterationId) {
        /*
        Iterating through each .table-data in .table-data-container if id == iterationId then remove that .table-data
        Updating iteration of .table-data's whose id's are larger than iterationId, because they come after the given .table-data since id are consecutive
        */
        const parentContainer = document.querySelector(`[data-id="${iterationId}"]`).parentElement;
        for (const iteration of parentContainer.querySelectorAll('.note-iteration')) {
            if (iteration.dataset.id == iterationId) {
                iteration.parentElement.removeChild(iteration)
                continue;
            }
            if (parseInt(iteration.dataset.id) > iterationId) {
                iteration.dataset.iteration = parseInt(iteration.dataset.iteration) - 1;
                iteration.querySelector('.iteration-count').innerText = `(${iteration.dataset.iteration})`;
                // update iteration relative option value in selec field tag
                const option = linkWhich.querySelector(`[value="${iteration.dataset.id}"]`);
                option.innerText = `Iteration: ${iteration.dataset.iteration}`;
            }
        }
        // remove option for removed iteration in which select field 
        const t = document.querySelector(`[value="${iterationId}"]`);
        linkWhich.removeChild(t)
    }

    function deleteIteration(iterationId, target) {
        fetch(`/iterations/${iterationId}/`, {
            method: "DELETE",
            mode: "same-origin",
            headers: new Headers(customHeaders)
        })
        .then(r => {
            if (r.status == 400) {
                alert('Could not delete iteration!')
            } else if (r.status == 200) {
                // delete it
                removeIteration(iterationId) 
                removePending(target)
            }
        })
    }

    const deleteIterationButtons = document.querySelectorAll('.delete-iteration');
    deleteIterationButtons.forEach(item => { 
        item.addEventListener('click', function(e) {
            addPending(e.target)
            // <div class=table-data> <div class=data> <button editbutton>
            const iterationId = item.parentElement.parentElement.dataset.id; 
            deleteIteration(iterationId, e.target)
        })
    })


    //////
    // Main form submission
    /////
    const mainForm = document.querySelector('#note-edit-form');
    document.querySelector('#note-edit-button').addEventListener('click', function() {
        mainForm.submit()
    })
})