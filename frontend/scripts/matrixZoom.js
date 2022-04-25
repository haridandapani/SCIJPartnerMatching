currScale = 1.0

/*
    Handles zooming in on matrix resizing
*/
function matrixMagnify() {
    container = document.getElementById("matrixContainer")
    currScale += 0.1
    container.style.transform = "scale(" + currScale + ")"
}

/*
    Handles zooming out on matrix resizing
*/
function matrixShrink() {
    if (currScale >= 0.2) { // Prevents inverting the matrix 
        container = document.getElementById("matrixContainer")
        currScale -= 0.1
        container.style.transform = "scale(" + currScale + ")"
    }
}

// Zoom button click event handlers
document.getElementById("matrixMagnify").addEventListener("click", matrixMagnify);
document.getElementById("matrixShrink").addEventListener("click", matrixShrink);

function zoom(event) {
    event.preventDefault(); // blocks default scroll action
    if (event.deltaY < 0) { // scroll up --> magnify
        matrixMagnify()
    } else if (event.deltaY > 0) { // scroll down --> shrink
        matrixShrink()
    }
}

const el = document.getElementById('matrixWindow');
el.onwheel = zoom;