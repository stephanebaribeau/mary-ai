"""
Reconnaissance d'identité -- compare un visage détecté par la webcam aux photos de référence dans known_faces/.
"""
from pathlib import Path

import cv2
import face_recognition
import numpy as np

KNOWN_FACES_DIR = Path(__file__).parent / "known_faces"
MATCH_TOLERANCE = 0.6  # plus bas = plus strict

def load_known_faces() -> list[tuple[str, np.ndarray]]:
    """Charge et encode tous les visages de référence -- à appeler UNE SEULE
    FOIS au démarrage, pas à chaque frame (calcul coûteux)."""

    known = []
    for photo_path in KNOWN_FACES_DIR.glob("*.jpg"):
        name = photo_path.stem
        image = face_recognition.load_image_file(photo_path)
        face_locations = face_recognition.face_locations(image, model="cnn")
        encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
        if not encodings:
            print(f"⚠️  Aucun visage détecté dans {photo_path.name}, ignoré.")
            continue
        known.append((name, encodings[0]))
    return known

def identify_face(frame: np.ndarray, known_faces: list[tuple[str, np.ndarray]]) -> str | None:
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
    if not face_locations:
        return None

    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    known_names = [name for name, _ in known_faces]
    known_encodings = [enc for _, enc in known_faces]

    for encoding in encodings:
        distances = face_recognition.face_distance(known_encodings, encoding)
        if len(distances) == 0:
            continue
        best_index = distances.argmin()
        if distances[best_index] <= MATCH_TOLERANCE:
            return known_names[best_index]

    return None

