import numpy as np
import sounddevice as sd
import webrtcvad

SAMPLE_RATE = 16000
VAD_AGGRESSIVENESS = 3
SILENCE_TIMEOUT_S = 1.2
MAX_RECORD_S = 30

MIC_NAME_HINT = "Arctis"

FRAME_MS = 30
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)

def _find_input_device(name_hint: str) -> int | None:
    for idx, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0 and name_hint.lower() in dev["name"].lower():
            return idx
    return None


_MIC_DEVICE = _find_input_device(MIC_NAME_HINT)

def listen(idle_timeout_s: float | None = None) -> np.ndarray | None:
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    silence_frames_needed = int(SILENCE_TIMEOUT_S * 1000 / FRAME_MS)
    idle_frame_limit = int(idle_timeout_s * 1000 / FRAME_MS) if idle_timeout_s else None
    max_frames = int(MAX_RECORD_S * 1000 / FRAME_MS)

    frames = []
    silence_run = 0
    started_speaking = False
    frame_count = 0

    print("🎤 Je t'écoute...")

    with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=FRAME_SAMPLES, device=_MIC_DEVICE) as stream:
        while True:
            chunk, _ = stream.read(FRAME_SAMPLES)
            chunk = chunk.flatten()
            frame_count += 1
            is_speech = vad.is_speech(chunk.tobytes(), SAMPLE_RATE)

            if not started_speaking:
                if is_speech:
                    started_speaking =  True
                    frames.append(chunk)
                    silence_run = 0
                elif idle_frame_limit and frame_count >= idle_frame_limit:
                    return None
                continue

            frames.append(chunk)
            if is_speech:
                silence_run = 0
            else:
                silence_run += 1
                if silence_run >= silence_frames_needed:
                    break

            if len(frames) >= max_frames:
                break

    audio_int16 = np.concatenate(frames)
    return audio_int16.astype(np.float32) / 32768.0

def play_audio(samples: np.ndarray, sample_rate: int):
    sd.play(samples, sample_rate)
    sd.wait()
