"""
Script d'enrolement -- à lancer une fois par personne à reconaître.
Capture une photo avec la webcam et la sauvegarde comme référence dans known_faces/, sous le nom fourni.
"""
import sys
from pathlib import Path
import cv2
from config import VISION_CAMERA_INDEX

KNOWN_FACES_DIR = Path(__file__).parent / "known_faces"

def _apply_zoom(frame, zoom_level: float):
    h, w = frame.shape[:2]
    crop_w, crop_h = int(w/zoom_level), int(h / zoom_level)
    x1 = (w-crop_w) // 2
    y1 = (h-crop_h) // 2
    cropped = frame[y1:y1 + crop_h, x1:x1 + crop_w]
    return cv2.resize(cropped, (w, h))

def main():
    if len(sys.argv) < 2:
        print("Usage : python enroll_face.py <ton nom")
        sys.exit(1)

    name = sys.argv[1]
    KNOWN_FACES_DIR.mkdir(exist_ok=True)

    cap = cv2.VideoCapture(VISION_CAMERA_INDEX)
    print("Positionne-toi bien en face de la caméra, éclairage de face si possible.")
    print("Appuie sur ESPACE piour capturer | + / - = zoom | ESC pour annuler.")

    zoom_level = 1.0 
    photo_path = None
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Erreur de lecture caméra.")
            break
    
        display_frame = _apply_zoom(frame, zoom_level) if zoom_level > 1.0 else frame
        cv2.imshow("Enrôlement -- ESPACE pour capturer, ESC pour annuler", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key != 255:  # 255 = aucune touche pressée cette frame
            print(f"[debug] touche détectée : {key}")
        if key == 27: #ESC
            break
        elif key in (ord("+"), ord("=")):
            print(f"[debug] zoom : {zoom_level}")
            zoom_level = min(zoom_level + 0.2, 3.0)
        elif key == ord("-"):
            print(f"[debug] zoom : {zoom_level}")
            zoom_level = max(zoom_level - 0.2, 1.0)
        elif key == 32: #ESPACE
            photo_path = KNOWN_FACES_DIR / f"{name}.jpg"
            cv2.imwrite(str(photo_path), display_frame)
            print(f"Photo sauvegardée : {photo_path}")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
