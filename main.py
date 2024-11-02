import cv2
import cvzone
import mediapipe
from cvzone.FaceMeshModule  import FaceMeshDetector

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


    success, frame = cap.read()
    faces, img = detector.findFaceMesh(frame)

    # ตรวจสอบ frame
    if not  success:
        print("Can't connect")
        break

    cv2.imshow("Camera", frame)

    # q for close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
