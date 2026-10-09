# test_vision.py
import queue
import threading

import vision

event_queue = queue.Queue()
stop_event = threading.Event()

t = threading.Thread(target=vision.watch, args=(event_queue, stop_event))
t.start()

print("Bouge devant la caméra... (Ctrl+C pour arrêter)")
try:
    while True:
        kind, payload = event_queue.get()
        print(f"Changement détecté ! (image encodée : {len(payload)} caractères)")
except KeyboardInterrupt:
    stop_event.set()
    t.join()
