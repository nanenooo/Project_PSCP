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
    """ ตรวจจับและนับการกระพริบตา """
    global blinkCounter, cap, detector

    leftEyeList, rightEyeList, counter = [], [], 0

    while True:
        #ตรวจสอบเฟรม
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, img = cap.read()
        img, faces = detector.findFaceMesh(img, draw=False)

        if faces:
            face = faces[0]

            # ระบุตำแหน่งจมูกกับดวงตา
            nose = face[1]
            leftEyeCorner, rightEyeCorner = face[33], face[263]

            # ตรวจสอบว่าหน้ามองจอมั้ย
            face_direction = abs(leftEyeCorner[0] - rightEyeCorner[0])
            if face_direction < 120:

                # ระบุตำแหน่งดวงตา
                leftUp, leftDown = face[159], face[145]
                leftLeft, leftRight = face[33], face[133]
                rightUp, rightDown = face[243], face[37]
                rightLeft, rightRight = face[463], face[263]

                # คำนวณหาระยะดวงตาแต่ละจุด
                leftLenghtVer, _ = detector.findDistance(leftUp, leftDown)
                leftLenghtHor, _ = detector.findDistance(leftLeft, leftRight)
                rightLenghtVer, _ = detector.findDistance(rightUp, rightDown)
                rightLenghtHor, _ = detector.findDistance(rightLeft, rightRight)

                # หาพื้นที่ของดวงตา
                leftEyeArea = int(0.05 * (leftLenghtVer * leftLenghtHor))
                rightEyeArea = int(0.05 * (rightLenghtVer * rightLenghtHor))
                leftEyeList.append(leftEyeArea)
                rightEyeList.append(rightEyeArea)

                # จำกัดข้อมูลใน List
                if len(leftEyeList) > 3:
                    leftEyeList.pop(0)
                if len(rightEyeList) > 3:
                    rightEyeList.pop(0)

                # หา Avg, Diff
                leftEyeAvg = sum(leftEyeList) / len(leftEyeList)
                rightEyeAvg = sum(rightEyeList) / len(rightEyeList)
                leftEyeDiff = abs(leftEyeAvg - leftEyeList[-1])
                rightEyeDiff = abs(rightEyeAvg - rightEyeList[-1])

                # ตรวจจับการกระพริบ
                if leftEyeDiff > 4 and counter == 0:
                    blinkCounter += 1
                    counter = 1

                # หน่วงเวลา
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
