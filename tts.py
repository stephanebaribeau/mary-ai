import subprocess
import time

import numpy as np
import sounddevice as sd

from audio_io import play_audio
import lipsync

PIPER_MODEL = "voices/fr_FR-siwis-medium.onnx"
PIPER_SAMPLE_RATE = 22050

CHUCK_DURATION_S = 0.05
MOUTH_GAIN = 3.0

def speak(text: str):
    if not text:
        return

    result = subprocess.run(
            ["piper-tts", "--model", PIPER_MODEL, "--output-raw"],
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
            )

    samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    #play_audio(samples, PIPER_SAMPLE_RATE)
    _speak_with_lipsync(samples, PIPER_SAMPLE_RATE)

def _speak_with_lipsync(samples: np.ndarray, sample_rate: int):
    chunk_size = int(sample_rate * CHUCK_DURATION_S)

    sd.play(samples, sample_rate)

    start = time.monotonic()
    for i in range(0, len(samples), chunk_size):
        chunk = samples[i:i + chunk_size]
        rms = float(np.sqrt(np.mean(chunk ** 2))) if len(chunk) else 0.0
        mouth_value = min(1.0, rms * MOUTH_GAIN)
        lipsync.send_mouth_value(mouth_value)

        target_time = start + (i + chunk_size) / sample_rate
        sleep_s = target_time - time.monotonic()
        if sleep_s > 0:
            time.sleep(sleep_s)

    sd.wait()
    lipsync.send_mouth_value(0.0)



