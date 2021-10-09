document.addEventListener('DOMContentLoaded', function () {
    let [prevButton, nextButton] = document.querySelectorAll('.calendar-button');
    let current = 10;
    let calendar = [];
    let month = null;
    const tbody = document.querySelector('tbody');
    let windowURL = new URL(window.location.href);
    let origin = windowURL.origin;
    function getHeatmapData() {
        let url = new URL('get_heatmap', origin);
        url.searchParams.append('month', current);
        return new Promise((resolve, reject) => {
            fetch(url)
                .then(async r => {
                    console.log(r.status);
                    return await r.json()
                })
                .then(body => {
                    calendar = body.calendar;
                    month = body.month;
                    resolve()
                }).catch(e => console.error(e));
        })
    }
    function clearHeatMap() {
        while (tbody.children.length > 0) {
            tbody.removeChild(tbody.children[0]);
        }
        const pending = document.createElement('p');
        pending.innerText = 'Fetching data...';
        tbody.appendChild(pending)
    }
    function populateHeatmap() {
        tbody.removeChild(tbody.firstElementChild)
        document.querySelector('.month').innerText = month;
        for (const week of calendar) {
            const tr = document.createElement('tr');
            for (const info of week) {
                const td = document.createElement('td');
                const activity = info[1];
                const modified = info[2];
                const day = info[0];
                td.setAttribute('aria-label', `Day of month: ${day}`)
                td.classList.add('heatmap_data')
                let hdata_info = null;
                if (day == null) {
                    td.classList.add('hdata_nothing')
                } else {
                    const p = document.createElement('p');
                    p.classList.add('hdata_day')
                    p.innerText = day;
                    td.appendChild(p)

                    switch (activity) {
                        case activity > 0:
                            hdata_info = document.createElement('div');
                            hdata_info.classList.add('hdata_info')
                            hdata_info.dataset.day = day;
                            const p = document.createElement('p');
                            p.innerText = `Modified ${modified}`;
                            const arrow = document.createElement('div');
                            arrow.classList.add('arrow')
                            hdata_info.appendChild(p)
                            hdata_info.appendChild(arrow)
                        case activity <= .25:
                            td.classList.add('hdata_lessquarter')
                            break;
                        case activity > .25 && activity <= .50:
                            td.classList.add('hdata_half')
                            break;
                        case activity > .50 && activity <= .75:
                            td.classList.add('hdata_quarterhalf')
                            break;
                        case activity > .75 && activity <= 1:
                            td.classList.add('hdata_full')
                            break;
                    }
                }
                tr.appendChild(td)
            }
            tbody.appendChild(tr)
            const space = document.createElement('tr');
            space.classList.add('space')
            tbody.appendChild(space)
        }
    }
    async function calendarButton(value) {
        current += value;
        clearHeatMap()
        await getHeatmapData();
        populateHeatmap()
    }
    prevButton.addEventListener('click', (() => { calendarButton(-1) }))
    nextButton.addEventListener('click', (() => { calendarButton(1) }))

    const spinnerContainer = document.querySelector('.spinner_container');
    const firstSpinner = spinnerContainer.firstElementChild;
    const secondSpinner = firstSpinner.nextElementSibling;
    let currentActive = null;
    document.querySelectorAll('.hdata_info').forEach(item => {
        item.parentElement.addEventListener('mouseenter', function () {
            item.parentElement.style.zIndex = 1;
            item.style.display = "initial";
        })
        item.parentElement.addEventListener('mouseleave', function () {
            item.parentElement.style.zIndex = 1;
            item.style.display = "none";
        })
        function displaySpinner() {
            spinnerContainer.style.display = 'initial';
            firstSpinner.style.animationPlayState = 'running';
            secondSpinner.style.animationPlayState = 'running';
        }
        const notesContainer = document.querySelector('#items-flex-container');
        function hideSpinner() {
            spinnerContainer.style.display = 'none';
            firstSpinner.style.animationPlayState = 'paused';
            secondSpinner.style.animationPlayState = 'paused';
        }
        item.parentElement.addEventListener('click', function () {
            if (currentActive) {
                if (currentActive == item.parentElement) {
                    hideSpinner()
                    currentActive.classList.remove('heatmap_active')
                    currentActive = null;
                    return;
                }
                // remove from active as the user clicked on a new heatmap
                currentActive.classList.remove('heatmap_active')
                currentActive = null;
            }
            while (notesContainer.children.length > 0) {
                notesContainer.removeChild(notesContainer.firstElementChild)
            }
            currentActive = item.parentElement;
            currentActive.classList.add('heatmap_active')
            displaySpinner()
            fetch(`/notes?json=True&day=${item.dataset.day}`, {
                method: "GET",
                headers: new Headers({
                    "Authorization": `Bearer ${window.sessionStorage.getItem("token")}`
                })
            })
                .then(async r => await r.json())
                .then(r => {
                    for (const item of r.notes) {
                        addNote(item.id, item.title, '/notes/' + item.id)
                    }
                    spinnerContainer.style.display = 'none';
                    hideSpinner()
                })
                .catch(e => { console.log(e); console.log('error'); hideSpinner() })
        })
    })
})
