import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
from flask import Flask, render_template, jsonify, Response
import threading
import time

app = Flask(__name__)

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)
blinkCounter = 0
blink_count = 0
blink_count_per_minute = 0
blink_counts_per_minute_list = []
average_blinks_per_minute = 0

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

        #ตรวจสอบว่าเจอหน้า
        if not faces:
            print("No faces detected")
            continue

        if faces:
            face = faces[0]

            # ระบุตำแหน่งจมูกกับดวงตา
            nose = face[1]
            leftEyeCorner, rightEyeCorner = face[33], face[263]

            # ตรวจสอบว่าหน้ามองจอมั้ย
            face_direction = abs(leftEyeCorner[0] - rightEyeCorner[0])
            if face_direction < 200:

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
                if leftEyeDiff > 3 and counter == 0:
                    blinkCounter += 1
                    print(f"Blink detected! Total count: {blinkCounter}")
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

def count_blinks_per_minute():
    """ กระพริบตาต่อนาที """
    global blinkCounter, blink_counts_per_minute_list, blink_count_per_minute, average_blinks_per_minute

    while True:
        time.sleep(60)  # หน่วงเวลาหนึ่งนาที

        blink_count_per_minute = blinkCounter  # เก็บค่าการกระพริบในนาทีนี้
        blink_counts_per_minute_list.append(blink_count_per_minute)  # เก็บค่าลงใน list

        # คำนวณค่าเฉลี่ยของการกระพริบต่อนาที
        if blink_counts_per_minute_list:
            average_blinks_per_minute = sum(blink_counts_per_minute_list) / len(blink_counts_per_minute_list)
        else:
            average_blinks_per_minute = 0

        print(f"Blink count per min: {blink_count_per_minute}")
        print(f"Average min: {average_blinks_per_minute:.2f}")

        # รีเซ็ตตัวนับการกระพริบสำหรับนาทีถัดไป
        blinkCounter = 0

@app.route('/')
def index():
    """ index page """
    return render_template('index.html')

@app.route('/blink.html')
def blink():
    """ blink page """
    return render_template('Blink.html')

@app.route('/blink_count', methods=['GET'])
def get_blinkCount():
    """ ส่งข้อมูลไปให้ js """
    global blinkCounter, blink_count_per_minute, average_blinks_per_minute
    print(f"Blink count sent to client: {blinkCounter}")
    return jsonify(
        {
            'blink_count': blinkCounter,
            'blink_count_per_min': blink_count_per_minute,
            'average_min': f"{average_blinks_per_minute:.2f}"
        }
    )


@app.route('/video_feed')
def video_feed():
    """ส่งข้อมูลวิดีโอไปยัง img tag"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    blink_thread = threading.Thread(target=countBlinks)
    blink_thread.daemon = True
    blink_thread.start()
    threading.Thread(target=count_blinks_per_minute, daemon=True).start()
    app.run(debug=True, use_reloader=False)