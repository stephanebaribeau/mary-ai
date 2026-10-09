import cv2
from config import VISION_CAMERA_INDEX

cap = cv2.VideoCapture(VISION_CAMERA_INDEX)
ok, frame = cap.read()
cap.release()

if ok:
    cv2.imwrite("snapshot.jpg", frame)
    print("Photo sauvegardée dans snapshot.jpg — ouvre-la pour vérifier.")
else:
    print("Impossible de capturer une image — vérifie VISION_CAMERA_INDEX ou les permissions.")
