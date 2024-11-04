import cv2
import cvzone
from cvzone.PlotModule import LivePlot
from cvzone.FaceMeshModule  import FaceMeshDetector
# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def index() :
#     return render_template(index.html)

def blinkCount():

    cap = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces=1)
    plotY = LivePlot(640, 360, [20, 50], invert=True)

    #จุดรอบดวงตาซ้าย
    idList = [22, 23, 24, 26, 110, 157, 158, 159 ,160 ,161, 130, 243]
    eyeList = []
    blinkCouter = 0
    counter = 0

    while True:

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, img = cap.read()
        img, faces = detector.findFaceMesh(img, draw=False)

        #วาดจุดรอบดวงตา
        if faces:
            face = faces[0]
            for id in idList:
                cv2.circle(img, face[id], 3, (255, 0, 255), cv2.FILLED)

            #วาดจุดแนวตั้งกับแนวนอน
            leftUp = face[159]
            leftDown = face[145]
            leftLeft = face[33]
            leftRight = face[133]
            lenghtVer, _ = detector.findDistance(leftUp, leftDown)
            lenghtHor, _ = detector.findDistance(leftLeft, leftRight)
            cv2.line(img, leftUp, leftDown, (0, 200, 0), 2)
            cv2.line(img, leftLeft, leftRight, (0, 200, 0), 2)

            #หาพื้นที่ดวงตา
            eyeArea = int((0.05*(lenghtVer*lenghtHor)))
            eyeList.append(eyeArea)

            if len(eyeList) > 3:
                eyeList.pop(0)

            eyeAvg = sum(eyeList)/len(eyeList)
            eyeDiff = abs(eyeAvg - eyeList[-1])

            if eyeDiff > 4 and counter == 0:
                blinkCouter += 1
                counter += 1
            if counter != 0:
                counter += 1
                if counter > 10:
                    counter = 0

            cvzone.putTextRect(img, f"Blink Count: {blinkCouter}", (50,100))
            imgPlot = plotY.update(eyeAvg)
            imgStack = cvzone.stackImages([img, imgPlot], 2, 1)

        # ตรวจสอบ frame
        if not  success:
            print("Can not connect")
            break

        cv2.imshow("Image", imgStack)

        # q for close
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cv2.waitKey(25)

    cap.release()
    cv2.destroyAllWindows()
blinkCount()