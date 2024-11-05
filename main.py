import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from flask import Flask, render_template, jsonify, Response
import threading

app = Flask(__name__)

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)
blinkCounter = 0

def countBlinks():
    """ ตรวจจับตา และหาการกระพริบตา """
    global blinkCounter, cap, detector

    eyeList, counter = [], 0

    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, img = cap.read()
        img, faces = detector.findFaceMesh(img, draw=False)

        if faces:
            face = faces[0]
            # วาดจุดแนวตั้งกับแนวนอน
            leftUp, leftDown = face[159], face[145]
            leftLeft, leftRight = face[33], face[133]
            lenghtVer, _ = detector.findDistance(leftUp, leftDown)
            lenghtHor, _ = detector.findDistance(leftLeft, leftRight)
            cv2.line(img, leftUp, leftDown, (0, 200, 0), 2)
            cv2.line(img, leftLeft, leftRight, (0, 200, 0), 2)

            # หาพื้นที่ดวงตา
            eyeArea = int((0.05 * (lenghtVer * lenghtHor)))
            eyeList.append(eyeArea)

            if len(eyeList) > 3:
                eyeList.pop(0)

            eyeAvg = sum(eyeList) / len(eyeList)
            eyeDiff = abs(eyeAvg - eyeList[-1])

            if eyeDiff > 4 and counter == 0:
                blinkCounter += 1
                counter += 1
            if counter != 0:
                counter += 1
                if counter > 10:
                    counter = 0

def generate_frames():
    """ส่งเฟรมวิดีโอจากกล้อง"""
    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            # เฟรมเป็น jpg
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            # ส่งออกเฟรม
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """ index page """
    return render_template('index.html')

@app.route('/blink_count', methods=['GET'])
def get_blinkCount():
    """ ส่งข้อมูลไปให้ js """
    global blinkCounter
    return jsonify(blink_count=blinkCounter)

@app.route('/video_feed')
def video_feed():
    """ส่งข้อมูลวิดีโอไปยัง img tag"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    blink_thread = threading.Thread(target=countBlinks)
    blink_thread.daemon = True
    blink_thread.start()
    app.run(debug=True, use_reloader=False)
