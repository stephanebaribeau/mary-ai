import select
import sys
import os
import queue
import threading
import logging

from audio_io import listen
from stt import transcribe
import brain
import vision
from tts import speak
from config import IDLE_CHECKIN_MAX_S, IDLE_CHECKIN_S, VISION_ENABLED
import lipsync

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpx2").setLevel(logging.WARNING)
logging.getLogger("faster_whisper").setLevel(logging.WARNING)

_EMOTION_ICONS = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😠",
    "neutral": "😐",
    "relaxed": "😌",
}

class _IdleState:
    def __init__(self):
        self.timeout: float | None = None

def _audio_worker(event_queue: "queue.Queue", idle_state: _IdleState, stop_event:threading.Event, listen_gate: threading.Event):
    while not stop_event.is_set():
        listen_gate.wait()
        audio = listen(idle_timeout_s=idle_state.timeout)
        event_queue.put(("audio", audio))

def input_with_timeout(prompt: str, timeout_s: float) -> str | None:
    """Retourne None si personne ne tape rien avant le délai."""
    print(prompt, end="", flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout_s)
    if ready:
        return sys.stdin.readline().rstrip("\n")
    print()
    return None

def _say(reply: str, label: str = "Elle"):
    """Affiche + parle une réponse, en transmettant l'émotion détectée à Godot."""
    emotion = brain.get_last_emotion()
    icon = _EMOTION_ICONS.get(emotion, "")
    print(f"{label} [{emotion} {icon}] : {reply}")
    lipsync.send_emotion(emotion)
    speak(reply)
    lipsync.send_emotion("neutral")

def main():
    print("=== Compagne virtuelle ===")
    print("Parle après le message 'Je t'écoute...'. Ctrl+C pour quitter.\n")

    event_queue : "queue.Queue" = queue.Queue()
    stop_event = threading.Event()
    idle_state = _IdleState()

    listen_gate = threading.Event()
    listen_gate.set()

    audio_thread = threading.Thread(
            target = _audio_worker, args=(event_queue, idle_state, stop_event, listen_gate), daemon=True
            )

    audio_thread.start()

    if VISION_ENABLED:
        vision_thread = threading.Thread(
                target=vision.watch, args=(event_queue, stop_event), daemon=True
                )
        vision_thread.start()

    
    had_first_exchange = False
    idle_delay = IDLE_CHECKIN_S
    
    while True:
        try:
            kind, payload = event_queue.get()
            listen_gate.clear()
            
            try:
                if kind == "audio":
                    audio = payload
    
                    if audio is None:
                        reply = brain.check_in()
                        _say(reply)
                        idle_delay = min(idle_delay * 2, IDLE_CHECKIN_MAX_S)
                        idle_state.timeout = idle_delay
                        continue

                    user_text = transcribe(audio)
                    if not user_text:
                        continue
            

                    print(f"Toi: {user_text}")
                    reply = brain.ask(user_text)
                    _say(reply)

                    had_first_exchange = True
                    idle_delay = IDLE_CHECKIN_S
                    idle_state.timeout = idle_delay

                elif kind == "vision":
                    image_b64, mood = payload
                    reply = brain.react_to_vision(image_b64, mood)
                    if reply.strip() in ("", "..."):
                        continue
                    _say(reply, label="Elle (a remarqué quelque chose)")

                elif kind == "mood_change":
                    name, mood = payload
                    reply = brain.react_to_mood(name, mood)
                    if reply.strip() in ("", "..."):
                        continue
                    _say(reply, label="Elle (remarque un changement d'humeur)")

                elif kind == "identity":
                    name, mood = payload
                    reply = brain.greet(name, mood)
                    _say(reply,label=f"Elle (reconnait {name}, humeur : {mood})")

            finally:
                listen_gate.set()

        except KeyboardInterrupt:
            print("\nElle retient ce qui compte de cette conversation...")
            stop_event.set()
            brain.update_memory()
            print("\nÀ la prochaine !")
            os._exit(0)

if __name__ == "__main__":
    main()
