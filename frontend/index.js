const form = document.getElementById("fileUpload")

/*
    Creates a div representing a 2 student pair
*/
function createChild(name1, name2, s) {
    // Div for one cell in matrix. This is a single box in the matrix
    let pair = document.createElement("div")
    pair.className = "matrixCell"

    let name = document.createElement("p")
    name.textContent = name1 + ", " + name2

    // Red if score < 0, grey if score == 0, green if score > 0
    if (s < 0) {
        pair.style.background = "#ab354d"
    } else if (s == 0) {
        pair.style.background = "#7d7d7d"
    } else {
        pair.style.background = "#49d184"
    }

    // Add names to pair div
    pair.appendChild(name)

    return pair
}

/*
    Takes in response json, inserts legal pairing matrix into the HTML
*/
function createMatrix(data) {
    // JSON FORMAT: {p1: {p1: score, ... pn: score}, ..., pn: {p1: score, ... pn: score}}

    const container = document.getElementById("matrixContainer") // Gets container to insert into

    for (var p1 in data) {
        let person = document.createElement("div") // Row for the person
        person.className = "matrixRow"
        for (var p2 in data[p1]) {
            pair = createChild(p1, p2, data[p1][p2])
            person.appendChild(pair)
        }
        container.appendChild(person)
    }
}

/*
    Takes in response json, puts optimal pairings on the website
*/
function createOptimal(data) {
    // JSON FORMAT: [{'person1': ..., 'person2': ...}, {...}]

    const container = document.getElementById("optimalList") // Gets container to insert into

    for (var pair of data) {
        let person = document.createElement("li") // Row for the person
        person.textContent = pair["person1"] + ", " + pair["person2"]
        container.appendChild(person)
    }
}

/*
    Takes in response json, puts optimal pairings on the website
*/
function createUnpaired(data) {
    // JSON FORMAT: ["<name1>", "<name2>", ...]
    const container = document.getElementById("unpairedList") // Gets container to insert into

    for (var name of data) {
        let person = document.createElement("li") // Row for the person
        person.textContent = name
        container.appendChild(person)
    }
}

/*
    Submits student data and matching headers, receives json response and creates matrix
*/
async function fetchData() {
    const file1 = document.getElementById('file1').files[0]
    const file2 = document.getElementById('file2').files[0]
    const minHours = document.getElementById("minHours").value
    
    var data = new FormData(form)
    data.append('data', file1)
    data.append('headers', file2)
    data.append("minHours", minHours)

    const returnDownloadLink = document.getElementById('excelCheck').checked

    if (returnDownloadLink) { // Excel download case
        fetch("http:/localhost:5000/download", {
            method: "POST",
            body: data
        })
        .then(response => {
            return response.blob()
        })
        .then(blob => {
            // Create hidden link element to download, click & delete link
            var a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = "legal_pairings.xlsx";
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(err => {
            console.log(err)
        })
    } else { // Create matrix directly on website
        fetch("http:/localhost:5000/upload_data", {
            method: "POST",
            body: data
        })
        .then(response => response.json())
        .then(data => {
            createMatrix(data.matrix)
            createOptimal(data.optimal)
            createUnpaired(data.unpaired)
        })
        .catch(err => {
            console.log(err)
        })
    }
}

/*
    Clears the current matrix
*/
function cleanup() {

    let parent = document.getElementById("matrixContainer") // Gets container to insert into 
    while (parent.firstChild) {
        parent.firstChild.remove()
    }

    parent = document.getElementById("optimalList") // Gets container to insert into 
    while (parent.firstChild) {
        parent.firstChild.remove()
    }

    parent = document.getElementById("unpairedList") // Gets container to insert into 
    while (parent.firstChild) {
        parent.firstChild.remove()

    }
}

/*
    Handles zooming in on matrix resizing
*/
function matrixMagnify() {
    let cells = document.getElementsByClassName("matrixCell")

    // Increase sides by 4% of screen height
    for (c of cells) {
        const length = parseInt(c.offsetHeight + screen.height *0.04)
        const newLength = length + "px"
        c.style.fontSize = parseInt(length / 2)
        c.style.height = newLength
        c.style.width = c.style.height
    }
}

/*
    Handles zooming out on matrix resizing
*/
function matrixShrink() {
    let cells = document.getElementsByClassName("matrixCell")

    // Decrease sides by 4% of screen height
    for (c of cells) {
        const length = parseInt(c.offsetHeight - screen.height *0.04)
        const newLength = length + "px"
        c.style.fontSize = parseInt(length / 2)
        c.style.height = newLength
        c.style.width = c.style.height
    }
}

// Form submit event handler
form.onsubmit = function(event) {
    event.preventDefault()
    cleanup()
    fetchData()
    return false
}

// Zoom button click event handlers
document.getElementById("matrixMagnify").addEventListener("click", matrixMagnify);
document.getElementById("matrixShrink").addEventListener("click", matrixShrink);

/* Adds drag scrolling for the matrix ========================================*/
const ele = document.getElementById("matrixWindow")
ele.style.cursor = 'grab';
let pos = { top: 0, left: 0, x: 0, y: 0 };
const mouseDownHandler = function (e) {
    ele.style.cursor = 'grabbing';
    ele.style.userSelect = 'none';

    pos = {
        left: ele.scrollLeft,
        top: ele.scrollTop,
        // Get the current mouse position
        x: e.clientX,
        y: e.clientY,
    };

    document.addEventListener('mousemove', mouseMoveHandler);
    document.addEventListener('mouseup', mouseUpHandler);
};

const mouseMoveHandler = function (e) {
    // How far the mouse has been moved
    const dx = e.clientX - pos.x;
    const dy = e.clientY - pos.y;

    // Scroll the element
    ele.scrollTop = pos.top - dy;
    ele.scrollLeft = pos.left - dx;
};

const mouseUpHandler = function () {
    ele.style.cursor = 'grab';
    ele.style.removeProperty('user-select');

    document.removeEventListener('mousemove', mouseMoveHandler);
    document.removeEventListener('mouseup', mouseUpHandler);
};

// Attach the handler
ele.addEventListener('mousedown', mouseDownHandler);
/* ========================================================================== */

/* ========================================================================== */
/* 
https://developer.mozilla.org/en-US/docs/Web/API/Element/wheel_event <<< BEtter scale impl
 */
function zoom(event) {
    event.preventDefault();

    if (event.deltaY < 0) {
        matrixMagnify()
    } else if (event.deltaY > 0) {
        matrixShrink()
    }
}

const el = document.getElementById('matrixWindow');
el.onwheel = zoom;
