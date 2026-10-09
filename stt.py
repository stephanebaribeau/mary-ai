import os
import sys

def _ensure_cuda_libs_on_path():
    try:
        import nvidia.cublas.lib
        import nvidia.cudnn.lib
    except ImportError:
        return

    cuda_paths = [
            list(nvidia.cublas.lib.__path__)[0],
            list(nvidia.cudnn.lib.__path__)[0],
            ]
    current = os.environ.get("LD_LIBRARY_PATH", "")
    if all(p in current for p in cuda_paths):
        return

    os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(cuda_paths + [current])
    os.execv(sys.executable, [sys.executable] + sys.argv)


_ensure_cuda_libs_on_path()

from faster_whisper import WhisperModel
import numpy as np

WHISPER_MODEL = "small"

_model = None

def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")
    return _model

def transcribe(audio: np.ndarray) -> str:
    _HALLUCINATIONS = {
            "sous-titres réalisés par la communauté d'amara.org",
        }
    if audio.size == 0:
        return ""
    segments, _ = _get_model().transcribe(audio, language="fr", beam_size=5)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    if text.lower() in _HALLUCINATIONS:
        return ""
    return text


