"""
Envoie l'amplitude audio en temps réel à Godot par UDP, pour piloter
le lip-sync de l'avatar 3D pendant que Piper parle.
"""
import socket

GODOT_HOST = "127.0.0.1"
GODOT_PORT = 9999

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_emotion(emotion: str):
    """Envoie le nom d'une émotion"""
    try:
        _sock.sendto(f"EMO:{emotion}".encode("utf-8"), (GODOT_HOST, GODOT_PORT))
    except OSError:
        pass

def send_mouth_value(value: float):
    """ Envoie une valeur 0.0-1.0 représentant l'ouverture de bouche voulue."""
    try:
        _sock.sendto(str(value).encode("utf-8"), (GODOT_HOST, GODOT_PORT))
    except OSError:
        pass
