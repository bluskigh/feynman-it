let iterations = null;
document.addEventListener('DOMContentLoaded', function() {
    const brain = document.querySelector('nav img');

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

    // main form that encapsulates all the inputs
    const form = document.querySelector('#note-edit-form');

    // add buttons that appear next to iterations and links sections. 
    const addButtons = document.querySelectorAll('.add-button');

    // 'form' section that contains all the inputs needed to edit iteration sections (and links).
    const editIterationContainer = document.querySelector('#edit-iteration-container');

    // 1 = iterations_one
    // 0 = links
    // 2 = iterations_two
    // 3 = general 
    // this object will be queried when the main form is submitted to retrieve information regarding (added, deleted, edited) iterations. 
    iterations = {1: {}, 0: {}, 2:{}, 3: {}}; 

    // this function is run as an event funciton therefore, is passed e
    function addItem(object) {
        // using e (object) to access what was clicked aka the 'target'
        const target = object.target;
        // since we are adding an item we are going to increase the length dataset value of the button indicating that total iterations in the buttons section has increased by 1
        target.dataset.length = parseInt(target.dataset.length) + 1;

        const container = document.createElement('div');
        let dataContainer = null;
        if (target.dataset.which == 0) {
            // this will store all the information of an item
            // purpose for separation is because the editIterationContainer is appended to each div.table-data giving the illusion of converting each row into its relative input.
            // in order to perform the illusion, we need to reveal the appended form and hide the data in table-data which is why I encapsulated the item data into a div of its own.
            container.classList.add('data')
        } else {
            dataContainer = document.createElement('div');
            dataContainer.classList.add('data')
            // table-data which will store each iteration (not used for links because each link is stored inside a container.table-data, each link is a div.data in a div.table-data)
            container.classList.add('table-data')
        }

        container.dataset.which = target.dataset.which;
        // settings the iteration dataset value to be the current buttons parents parent total length of .table-data divs plus one (plus one because we are adding this item)
        container.dataset.iteration = parseInt(target.dataset.length);

        // each div.table-data contains an h4 that lets the user know what a current iteration is
        // for normal iterations it would display what iteration a text is in example: Iteration X, followed by text
        // for links if there is not a link section for a certain step 1 section then this iterationHeader is used to display the following in the .table-data: "Links for iteration: x"
        const iterationHeader = document.createElement('h4');

        // add item button always succeeds a textarea field, grab that field as the values we want are going to be stored there
        const textarea = target.previousElementSibling;

        // edit button that is used for all type of items (link, iteration)
        const editButton = document.createElement('button');
        editButton.setAttribute('type', 'button')
        editButton.classList.add('edit-iteration')
        editButton.addEventListener('click', editButtonFunctionality)
        editButton.innerText = 'Edit';
        editButton.dataset.added = true;

        // when we add a value we store all the added values in a map {'added': [list of added items]} in the server we check if added is in the available keys if so add the values
        if (target.dataset.added == null) {
            // assign an empty list to added key in the object
            iterations[target.dataset.which]["added"] = [];
            // update buttons dataset added value 
            target.dataset.added = true;
        }

        // if add item button of links was clicked
        if (target.dataset.which == 0) {
            // stores the value of which iteration section was selected to add this link too (links are grouped into specific sections, aka the iteration a certian link belongs too) 
            const iterationChoosen = parseInt(document.querySelector('#forwhich').value);
            let linkTitle = document.querySelector('#link-title');

            // each link contains the following format: [iteration of step 1 choosen, link title to be displayed when rendering, link href to be used]
            iterations[target.dataset.which].added.push([iterationChoosen, linkTitle.value.trim(), textarea.value.trim()]);

            // creating the a tag to store the newly added link
            const a = document.createElement('a');
            a.setAttribute('href', textarea.value.trim())
            a.setAttribute('target', '_blank')
            a.innerText = linkTitle.value.trim();

            container.dataset.forwhich = iterationChoosen;

            // adding link to dataContainer
            container.appendChild(a)
            container.appendChild(editButton)

            // clearing link form fields (link title, link href (textarea))
            linkTitle.value = "";
            textarea.value = "";

            // garbage collect
            linkTitle = null;
        } else {
            let emptyIterationP = target.parentElement.parentElement.querySelector('p');
            if (emptyIterationP && emptyIterationP.innerText.startsWith('No')) {
                // remove since a new item is being added therefore no longer being empty 
                target.parentElement.parentElement.removeChild(emptyIterationP)
            }
            // garbage collect object
            emptyIterationP = null;

            // format here is different than the format for links because this is simply adding text unlike links which contains iteration choosen, title, and text therefore we can simply concat a value with existing array in added
            iterations[target.dataset.which].added = iterations[target.dataset.which].added.concat(textarea.value.trim());

            // since links is mainly meant for step 1 (solve after acquiring gaps in explanation) each time this newItem function is run on 1 (1 = new step 1 iteration) then add an option to store links
            // in the newly added iteration for step 1
            if (target.dataset.which == 1) {
                // add new option to links
                const option = document.createElement('option');
                // recall in the beginning of this newItem function we incremented the length value by 1 (self explanatory) therefore no need to querySelectorAll(.table-data).length to recieve the index of newly added iteration 
                option.value = target.dataset.length;
                option.innerText = `Iteration ${target.dataset.length}`;
                document.querySelector('#forwhich').appendChild(option)
            }

            const p = document.createElement('p');
            p.innerText = textarea.value;
            dataContainer.appendChild(p)
            dataContainer.appendChild(editButton)
        }
        
        // if button clicked to add new item is not links section
        if (target.dataset.which != 0) { 
            iterationHeader.innerText = `Iteration: ${target.dataset.length}`;
            container.classList.add('note-iteration')
            container.appendChild(iterationHeader)
            container.appendChild(dataContainer)
            // insert newly added container before the add form of the iteration container
            target.parentElement.parentElement.insertBefore(container, target.parentElement)
        }else if (target.dataset.which == 0) {
            const linksData = document.querySelector('#links-data');
            const tableData = linksData.querySelectorAll('.table-data');
            const forwhich = document.querySelector('#forwhich').value;
            if (tableData.length > parseInt(forwhich.value)) {
                // ^ if button was in links section and links section td contains table data whose index is relative to the forwhich value selected then append link to thus container
                const forwhichcontainer = tableData[parseInt(forwhich)];
                forwhichcontainer.appendChild(dataContainer)
                // dataContainer.dataset.iteration = forwhichcontainer.querySelector('.data').length+1;
            } else if (tableData.length <= parseInt(forwhich)) {
                // ^ otherwise if button in links section and links section td does not contain a table data of index equal to selected forwhich value
                iterationHeader.innerText = `Links for iteration: ${document.querySelector('#forwhich').value}`;
                // append the container that encapsulates dataContainer (<div.table-data>__space for edit form___<div.data>__space for actual information such as p, a)
                container.insertBefore(iterationHeader, container.firstChild)
                target.parentElement.parentElement.insertBefore(container, target.parentElement)
                // just created so the length is goign to be 1
                // dataContainer.dataset.iteration = 1;
            }
        }
        textarea.value = "";
    }

    addButtons.forEach(item => {
        item.addEventListener('click', function(object) {
            // check textarea length
            if (item.previousElementSibling.value.length > 0) {
                if (item.dataset.which == 0 && item.parentElement.querySelector('input').value.length <= 0) { 
                    return;
                }
                addItem(object)
            }
        })
    })

    document.querySelector('.submit').addEventListener('click', function() {
        addButtons.forEach(item => {
            item.previousElementSibling.value = JSON.stringify(iterations[item.dataset.which]);
        })
        form.submit()
    })

    function editButtonFunctionality(object) {
        if (editIterationContainer.classList.contains('busy')) {
            // editIterationContainer.querySelector('textarea').value = '';
            // editIterationContainer.parentElement.querySelector('.data').classList.remove('display-none')
            toggleEditIterationContainer(object)
        }

        // const data = target.parentElement.parentElement.querySelector('.data');
        const target = object.target;
        const parent = target.parentElement;
        parent.classList.add('display-none')

        target.parentElement.parentElement.insertBefore(editIterationContainer, parent)

        editIterationContainer.classList.remove('display-none')
        editIterationContainer.classList.add('busy')

        editIterationContainer.dataset.which = parent.dataset.which;

        let inputTitle = editIterationContainer.querySelector('input');

        // if edit button of a link was clicked display the titl einput in the edit form 
        if (parent.dataset.which == 0) {
            inputTitle.value = target.previousElementSibling.innerText;
            editIterationContainer.querySelector('textarea').value = target.previousElementSibling.getAttribute('href')
            inputTitle.classList.remove('display-none');
        } else {
            editIterationContainer.querySelector('textarea').value = target.parentElement.querySelector('p').innerText.trim();
            editIterationContainer.querySelector('input').classList.add('display-none')
        }
    }

    document.querySelectorAll('.edit-iteration').forEach(item => {
        item.addEventListener('click', editButtonFunctionality)
    })

    function toggleEditIterationContainer() {
        // can either be close or save edit button on the edit form

        editIterationContainer.classList.add('display-none')
        editIterationContainer.classList.remove('busy')
        // parent of form which is table-data
        let parent = editIterationContainer.parentElement;
        if (parent.dataset.length == null) {
            parent = editIterationContainer.nextElementSibling;
        }
        const value = parent.dataset.iteration;
        if (parent.dataset.which == '0') {
            parent.classList.remove('display-none')
        } else {
            editIterationContainer.nextElementSibling.classList.remove('display-none')
        }
        editIterationContainer.querySelector('textarea').value = '';
        editIterationContainer.querySelector('input').value = '';
        editIterationContainer.querySelector('input').classList.add('display-none')
        document.querySelector('body').appendChild(editIterationContainer)
    }

    // send back to body and hide
    editIterationContainer.querySelector('.close').addEventListener('click', toggleEditIterationContainer)

    editIterationContainer.querySelector('.save-edit').addEventListener('click', function(object) {
        // save response 
        let parent = editIterationContainer.parentElement;
        if (parent.dataset.which == null) {
            // edit container when using links is appended before the data div taht we are trying to edit, therefore if in links we want to get the next element
            parent = editIterationContainer.nextElementSibling;
        }
        // if (parent.querySelector('.edit-iteration').dataset.added) {
        //     // just added do not choose anything for edited.
        // }
        const value = this.previousElementSibling.querySelector('textarea').value.trim();
        if (iterations[parent.dataset.which].edit == null) {
            iterations[parent.dataset.which]["edit"] = {};
        }
        if (parent.dataset.which ==  0) {
            const inputTitleValue = this.previousElementSibling.querySelector('input').value.trim(); 
            iterations[parent.dataset.which].edit[parent.dataset.iteration] = [parseInt(parent.dataset.forwhich), inputTitleValue, value];
            // iterations[this.dataset.which].edit[iteration][0] = this.previousElementSibling.querySelector('input').value.trim();
            // iterations[this.dataset.which].edit[iteration][1] = value.trim();
            this.parentElement.nextElementSibling.querySelector('a').innerText = inputTitleValue.trim();
            this.parentElement.nextElementSibling.querySelector('a').setAttribute('href', value.trim());
        } else {
            iterations[parent.dataset.which].edit[parent.dataset.iteration] = value.trim();
            this.parentElement.parentElement.querySelector('.data').querySelector('p').innerText = value.trim();
        }

        toggleEditIterationContainer()
    })


})