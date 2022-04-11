const form = document.getElementById("fileUpload")

/*
    Creates a div representing a 2 student pair
*/
function createChild(name1, name2, s) {
    let pair = document.createElement("div")
    pair.className = "matrixCell"
    let name = document.createElement("p")

    name.textContent = name1 + ", " + name2 

    if (s < 0) {
        pair.style.background = "#ab354d"
    } else if (s == 0) {
        pair.style.background = "#7d7d7d"
    } else {
        pair.style.background = "#49d184"
    }
    
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
    Submits student data and matching headers, receives json response and creates matrix
*/
async function fetchData() {
    const file1 = document.getElementById('file1').files[0]
    const file2 = document.getElementById('file2').files[0]

    var data = new FormData(form)
    data.append('data', file1)
    data.append('headers', file2)

    const returnDownloadLink = document.getElementById('excelCheck').checked

    if (returnDownloadLink) {
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
    } else {
        fetch("http:/localhost:5000/upload_data", {
            method: "POST",     
            body: data
        })
        .then(response => response.json())
        .then(data => {
            createMatrix(data)
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
    const parent = document.getElementById("matrixContainer") // Gets container to insert into 
    while (parent.firstChild) {
        parent.firstChild.remove()
    }
}

function matrixMagnify() {
    let cells = document.getElementsByClassName("matrixCell")
    for (c of cells) {
        const newLength = parseInt(c.offsetHeight + screen.height *0.04) + "px"
        c.style.height = newLength
        c.style.width = c.style.height
    }
}

function matrixShrink() {
    let cells = document.getElementsByClassName("matrixCell")
    for (c of cells) {
        const newLength = parseInt(c.offsetHeight - screen.height *0.04) + "px"
        c.style.height = newLength
        c.style.width = c.style.height
    }
}

form.onsubmit = function(event) {
    event.preventDefault()
    cleanup()
    fetchData()
    return false
}

document.getElementById("matrixMagnify").addEventListener("click", matrixMagnify);
document.getElementById("matrixShrink").addEventListener("click", matrixShrink);