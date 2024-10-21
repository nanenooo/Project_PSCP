const video = document.getElementById('video');
let stream;

// Start webcam access
function startVideoStream() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((mediaStream) => {
            video.srcObject = mediaStream;
            stream = mediaStream;
        })
        .catch((error) => {
            alert("Cannot access camera. Please allow camera permissions in your browser settings.");
            console.error("Camera access error:", error);
        });
}

// Start detection (to be implemented)
function startDetection() {
    document.getElementById('start_button').disabled = true;
    document.getElementById('stop_button').disabled = false;
    console.log("Face detection started...");
}

// Stop detection
function stopDetection() {
    document.getElementById('start_button').disabled = false;
    document.getElementById('stop_button').disabled = true;

    // Stop video stream
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    console.log("Face detection stopped.");
}

// Immediately request camera access on page load
startVideoStream();
