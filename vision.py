import base64
import threading
import time
import identity
import emotion

import cv2
import numpy as np

from config import (
        VISION_CAMERA_INDEX,
        VISION_POLL_INTERVAL_S,
        VISION_DIFF_RESIZE,
        VISION_CHANGE_THRESHOLD,
        VISION_COOLDOWN_S,
        VISION_SEND_WIDTH,
        GREETING_COOLDOWN_S,
        EMOTION_POLL_INTERVAL_S,
        MOOD_CHANGE_COOLDOWN_S,
        )

def _encode_frame(frame) -> str:
    h, w = frame.shape[:2]
    scale = VISION_SEND_WIDTH / w
    resized = cv2.resize(frame, (VISION_SEND_WIDTH, int(h * scale)))
    ok, buf = cv2.imencode(".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buf.tobytes()).decode("ascii")

def _change_ratio(prev_small: np.ndarray, curr_small: np.ndarray) -> float:
    diff = cv2.absdiff(prev_small, curr_small)
    changed = int(np.count_nonzero(diff > 25))
    return changed / diff.size

def watch(event_queue, stop_event: threading.Event):
    cap = cv2.VideoCapture(VISION_CAMERA_INDEX)
    if not cap.isOpened():
        print("⚠️  Webcam introuvable — la vision est désactivée pour cette session.")
        return

    known_faces = identity.load_known_faces()
    if known_faces:
        print(f"👤 Visages connus chargés : {', '.join(name for name, _ in known_faces)}")

    prev_small = None
    last_trigger = 0.0
    last_greeting = 0.0
    last_emotion_check = 0.0
    last_mood = None
    last_mood_reaction = 0.0

    try:
        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                time.sleep(VISION_POLL_INTERVAL_S)
                continue

            now = time.time()

            if now - last_emotion_check >= EMOTION_POLL_INTERVAL_S:
                last_emotion_check = now
                current_mood = emotion.describe_emotion(emotion.detect_emotion(frame))
                print(f"[debug] humeur actuelle : {current_mood!r} (précédente : {last_mood!r}, dernière réaction il y a {now - last_mood_reaction:.0f}s)")
                if(
                        current_mood and current_mood != last_mood and (now-last_mood_reaction) >= MOOD_CHANGE_COOLDOWN_S):
                    last_mood_reaction = now
                    name = identity.identify_face(frame, known_faces) if known_faces else None
                    event_queue.put(("mood_change", (name, current_mood)))
                if current_mood:
                    last_mood = current_mood

            small = cv2.cvtColor(cv2.resize(frame, VISION_DIFF_RESIZE), cv2.COLOR_BGR2GRAY)
            small = cv2.GaussianBlur(small, (5,5), 0)

            if prev_small is not None:
                ratio = _change_ratio(prev_small, small)
                now = time.time()
                if ratio >= VISION_CHANGE_THRESHOLD and (now - last_trigger) >= VISION_COOLDOWN_S:
                    last_trigger = now

                    name = identity.identify_face(frame, known_faces) if known_faces else None
                    mood = emotion.describe_emotion(emotion.detect_emotion(frame))

                    if name and (now - last_greeting) >= GREETING_COOLDOWN_S:
                        last_greeting = now
                        event_queue.put(("identity", (name, mood)))
                    else:
                        event_queue.put(("vision", (_encode_frame(frame), mood)))

            prev_small = small
            time.sleep(VISION_POLL_INTERVAL_S)
    finally:
        cap.release()
