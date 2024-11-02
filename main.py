import cv2
import cvzone
import mediapipe
from cvzone.FaceMeshModule  import FaceMeshDetector

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

#จุดรอบดวงตาซ้าย
idList = [22, 23, 24, 26, 110, 157, 158, 159 ,160 ,161, 130, 243]

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
        lenghtVer, _ = detector.findDistance(leftUp, leftDown)
        lenghtHor, _ = detector.findDistance(leftLeft, leftRight)
        cv2.line(img, leftUp, leftDown, (0, 200, 0), 2)
        cv2.line(img, leftLeft, leftRight, (0, 200, 0), 2)

        #แสดงระยะห่างของแกนแนวตั้งกับแนวนอน 
        print(int((lenghtVer/lenghtHor)*100))

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
