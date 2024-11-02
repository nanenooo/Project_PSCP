import cv2
import cvzone
from cvzone.FaceMeshModule  import FaceMeshDetector

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

#จุดรอบดวงตาซ้าย
idList = [
        263, 249, 390, 373, 374, 380, 381, 382, 362
        , 466, 388, 387, 386, 386, 385, 384, 398
        , 246, 161, 160, 159, 158, 157, 173
        , 33, 7, 163, 144, 145, 153, 154, 155, 133
        ]
leftList, rightList = [], []
blinkCounter = 0
counter = 0

while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        face = faces[0]
        for id in idList:
            #วาดจุดรอบดวงตา
            cv2.circle(img, face[id], 3, (255, 0, 255), cv2.FILLED)

        #วาดจถดแนวตั้งกับแนวนอน
        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]
        rightUp = face[386]
        rightDown = face[374]
        rightLeft = face[382]
        rightRight = face[263]
        rlenghtVer, _ = detector.findDistance(rightUp, rightDown)
        rlenghtHor, _ = detector.findDistance(rightLeft, rightRight)
        llenghtVer, _ = detector.findDistance(leftUp, leftDown)
        llenghtHor, _ = detector.findDistance(leftLeft, leftRight)
        cv2.line(img, leftUp, leftDown, (0, 200, 0), 2)
        cv2.line(img, leftLeft, leftRight, (0, 200, 0), 2)
        cv2.line(img, rightUp, rightDown, (0, 200, 0), 2)
        cv2.line(img, rightLeft, rightRight, (0, 200, 0), 2)

    #ระยะห่างของแกนแนวตั้งกับแนวนอน
    lration = int((llenghtVer/llenghtHor)*100)
    rration = int((rlenghtVer/rlenghtHor)*100)+5

    if len(leftList) > 10 and len(rightList) > 10:
        leftList.pop(0)
        rightList.pop(0)
    while len(leftLeft) <= 10:
        leftList.append(lration)
        rightList.append(rration)

    leftAvg = sum(leftList)/len(leftList) - leftList[-1]
    rightAvg = sum(rightList)/len(rightList) - rightList[-1]
    print(leftAvg, leftList[-1], rightAvg, rightList[-1])

    if leftAvg - leftList[-1] < 2 and rightAvg - rightList[-1] < 2:
        blinkCounter += 1
        counter += 1
        print("BLINK")

    if not counter:
        counter += 1
        if counter > 10:
            counter = 0

    # ตรวจสอบ frame
    if not  success:
        print("Can not connect")
        break

    cv2.imshow("Image", img)

    # q for close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.waitKey(25)

cap.release()
cv2.destroyAllWindows()
