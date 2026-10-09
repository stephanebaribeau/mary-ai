"""
Détection locale d'émotion faciale (Phase 2) -- UItilise fer (FER2013) pour
classer l'expression dominante d'un visage détecté dans une frame. Comme
identity.py, tourne entièrement en local, aucun coût API.
"""

from fer.fer import FER

_detector = FER(mtcnn=True)

_EMOTION_FR = {
    "angry": "fâché(e)",
    "disgust": "dégoûté(e)",
    "fear": "craintif(ve)",
    "happy": "content(e)/souriant(e)",
    "sad": "triste",
    "surprise": "surpris(e)",
    "neutral": "neutre",
}

def describe_emotion(emotion: str | None) -> str | None:
    """Traduit le label anglais de fer en description française. Ou None
    si aucune émotion n'a éét détectée. """
    if emotion is None:
        return None
    return _EMOTION_FR.get(emotion, emotion)

def detect_emotion(frame) -> str | None:
    """Retourne l'émotion dominante détectée dans la frame (ex: 'happy',
                                                               'neutral', 'sad'), ou None si 
    aucun isage/émotion n'a pu être détecté.
    """

    emotion, score = _detector.top_emotion(frame)
    return emotion


