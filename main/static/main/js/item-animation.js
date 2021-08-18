document.addEventListener('DOMContentLoaded', function() {
        const newNoteTitle = document.querySelector('#id_title');

        // querySelectorAll returns a NodeList therefore does not have slice() method built in 
        let items = Array.from(document.querySelectorAll('.item')).slice(0, -1);

        items.forEach(item => {
            item.addEventListener('mouseenter', function() {
                // initiate shader
                item.firstElementChild.classList.toggle('hidden')
            })
            item.addEventListener('mouseleave', function() {
                // deactivate shader
                item.firstElementChild.classList.toggle('hidden')
            })
        })

        // iteration would be the parts of the keyframe that are reached 
        // in this case, 0% and 100% are cause the iteration event listener to fire 
        // therefore we can track where in the animation process we are at by 
        // tracking the iteration event listener
        let iteration = 0;

        const itemAdd = document.querySelector('.item-add');
        function itemAddClicked() {
            itemAdd.style.animationPlayState = 'running';
            if (iteration % 2 != 0) {
                // animation going back to original state therefore hide form first
                itemAdd.parentElement.querySelector('form').classList.toggle('hidden')
            }
        }
        itemAdd.addEventListener('click', itemAddClicked)

        itemAdd.addEventListener('animationiteration', function() {
            itemAdd.style.animationPlayState = 'paused';
            iteration+=1;
            if (iteration % 2 == 0) {
                // original state, user may have exited therefore clear input and "reveal" shader so that the user cannot click on the inputs of the form
                itemAdd.parentElement.querySelector('form').firstElementChild.style.zIndex = 'initial';
                newNoteTitle.value = "";
                itemAdd.innerText = '+';
            } else {
                itemAdd.innerText = 'X';
                // creation state, hide the shader (shader is always the first element in the form)
                itemAdd.parentElement.querySelector('form').firstElementChild.style.zIndex = -1;
                // after the button has reached creation iteration then reveal
                itemAdd.parentElement.querySelector('form').classList.toggle('hidden')
            }
        })
})