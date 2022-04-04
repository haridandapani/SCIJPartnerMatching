const form = document.getElementById("fileUpload")

/*
    Creates a div representing a 2 student pair
*/
function createChild(name1, name2, s) {
    let pair = document.createElement("div")
    let name = document.createElement("p")
    let score = document.createElement("p")

    name.textContent = name1 + ", " + name2 
    score.textContent = s
    
    pair.appendChild(name)
    pair.appendChild(score)
    
    return pair
}

/*
    Takes in response json, inserts legal pairing matrix into the HTML
*/
function createMatrix(data) {
    // JSON FORMAT: {p1: {p1: score, ... pn: score}, ..., pn: {p1: score, ... pn: score}}

    const container = document.getElementById("pairContainer") // Gets container to insert into 

    for (var p1 in data) {
        let person = document.createElement("div") // Row for the person
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
    const parent = document.getElementById("pairContainer") // Gets container to insert into 
    while (parent.firstChild) {
        parent.firstChild.remove()
    }
}

form.onsubmit = function(event) {
    event.preventDefault()
    cleanup()
    fetchData()
    return false
}