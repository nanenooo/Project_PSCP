const camera = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((error) => {
            console.error("ไม่สามารถเข้าถึงกล้องได้: ", error);
        });