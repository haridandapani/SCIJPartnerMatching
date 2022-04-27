const form = document.getElementById("fileUpload")

/*
    Creates a div representing a 2 student pair
*/
function createChild(name1, name2, s) {
    // Div for one cell in matrix. This is a single box in the matrix
    let pair = document.createElement("div")
    pair.className = "matrixCell"
    pair.textContent = name1 + "\r\n" + name2

    // Red if score < 0, grey if score == 0, green if score > 0
    if (s < 0) {
        pair.style.background = "#ab354d"
    } else if (s == 0) {
        pair.style.background = "#7d7d7d"
    } else {
        pair.style.background = "#49d184"
    }

    // Add names to pair div
    //pair.appendChild(name)

    return pair
}

function createNameChild(name1) {
    let pair = document.createElement("div")
    pair.className = "matrixCell"
    pair.textContent = name1
    pair.style.background = "#f46500" // orange background

    return pair
}

/*
    Takes in response json, inserts legal pairing matrix into the HTML
*/
function createMatrix(data) {
    // JSON FORMAT: {p1: {p1: score, ... pn: score}, ..., pn: {p1: score, ... pn: score}}

    const container = document.getElementById("matrixContainer") // Gets container to insert into

    // Add top name row 
    const names = Object.values(data)[0]
    let nameRow = document.createElement("div") // Row for the person
    nameRow.className = "matrixRow"

    // First Cell is empty
    let emptyCell = document.createElement("div")
    emptyCell.className = "matrixCell"
    nameRow.appendChild(emptyCell)

    for (var p1 in names) {
        const nameColCell = createNameChild(p1)
        nameRow.appendChild(nameColCell)
    }

    container.appendChild(nameRow)

    // Each subsequent row first cell is a name cell followed by pair cells
    for (var p1 in data) {
        let person = document.createElement("div") // Row for the person
        person.className = "matrixRow"

        const nameColCell = createNameChild(p1)
        person.appendChild(nameColCell)

        for (var p2 in data[p1]) {
            pair = createChild(p1, p2, data[p1][p2])
            person.appendChild(pair)
        }
        container.appendChild(person)
    }

    textFit(document.getElementsByClassName("matrixCell"), {minFontSize:0}) // make text fit within matrix

    container.scrollIntoView({
        behavior: 'smooth', 
        block: 'center', 
        inline: 'center'
    })
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

function createDownloadButton(filename){
    const downloaddiv = document.getElementById('downloadparent');

    var a = document.createElement("a");
    downloaddiv.appendChild(a);
    url = "http://localhost:5000/uploads/"+filename;
    console.log(url);
    a.textContent = "Download your file here"
    a.href = url
}

function handleError(message) {
    let errorMessage = document.createElement("p")
    let errorContext = document.createElement("p")
    errorMessage.textContent = "Something went wrong processing your files"
    errorContext.textContent = message
    document.getElementById("error").appendChild(errorMessage)
    document.getElementById("error").appendChild(errorContext)
}

async function handleFormExcelSubmission() {
    const file1 = document.getElementById('file1').files[0]
    const file2 = document.getElementById('file2').files[0]
    const minHours = document.getElementById("minHours").value
    
    var data = new FormData(form)
    data.append('data', file1)
    data.append('headers', file2)
    data.append("minHours", minHours)

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
}

async function handleFormMatrixSubmission() {
    const file1 = document.getElementById('file1').files[0]
    const file2 = document.getElementById('file2').files[0]
    const minHours = document.getElementById("minHours").value
    
    var data = new FormData(form)
    data.append('data', file1)
    data.append('headers', file2)
    data.append("minHours", minHours)

    fetch("http:/localhost:5000/upload_data", {
        method: "POST",
        body: data
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        if (data.success) {
            createMatrix(data.matrix)
            createOptimal(data.optimal)
            createUnpaired(data.unpaired)
            createDownloadButton(data.filename)

        } else {
            handleError(data.message)
        }


        
    })
    .catch(err => {
        console.log(err)
    })
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

    parent = document.getElementById("downloadparent") // Gets container to insert into 
    while (parent.firstChild) {
        parent.firstChild.remove()
    }

    parent = document.getElementById("error")
    while (parent.firstChild) {
        parent.firstChild.remove()
    }
}

// Form submit event handler
form.onsubmit = function(event) {
    event.preventDefault()
    cleanup()
    handleFormMatrixSubmission()
    return false
}