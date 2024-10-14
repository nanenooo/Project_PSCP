const camera = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((error) => {
            console.error("ไม่สามารถเข้าถึงกล้องได้: ", error);
        });
function startDetection() {
    console.log('Start');
    // ปิดปุ่ม Start เปิดปุ่ม Stop
    document.getElementById('start_button').disabled = true;
    document.getElementById('stop_button').disabled = false;
}
function stopDetection() {
    console.log('Stop');
    // ปิดปุ่ม Stop เปิดปุ่ม Start
    document.getElementById('start_button').disabled = false;
    document.getElementById('stop_button').disabled = true;
}