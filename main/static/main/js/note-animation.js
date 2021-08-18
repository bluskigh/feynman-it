// when editing a note there is a table row = title <input> which does not contain a next item just 
// the th that encapsulates the input therefore an error occurs when item.nextElementSibling runs so ignore that first item (slicing it)
let headers = document.querySelectorAll('#item-table th');
if (document.location.pathname.indexOf('edit') > 0) {
    headers = Array.from(headers).slice(1);
}

function flashHeader(item) {
    item.classList.toggle('tableitem-mouseenter')
    item.nextElementSibling.classList.toggle('tableitem-mouseleave')
}

function flashed(item) {
    return new Promise((resolve, reason) => {
        flashHeader(item)
        setTimeout(() => {
            flashHeader(item)
            resolve()
        }, 500)
    })
}

function sleep(time) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve()
        }, time)
    })
}

async function beginConsecutiveExecution() {
    // flash every item with 500 break inbetween flash
    for (const item of headers) {
        await flashed(item)
    }
    // flash them all again *****
    for (const item of headers) {
        flashHeader(item)
    }

    // allow user to see final time
    await sleep(500)

    // return all headers back to original state
    for (const item of headers)  {
        flashHeader(item)
        item.addEventListener('mouseenter', function() {
            flashHeader(item)
        })
        item.addEventListener('mouseleave', function() {
            flashHeader(item)
        })
    }
}

beginConsecutiveExecution()
