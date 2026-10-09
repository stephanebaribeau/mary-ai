import os


import numpy as np
import soundfile as sf
from scipy.signal import resample
from stt import transcribe

data, sample_rate = sf.read("test.wav")

if data.ndim > 1:
    data = data.mean(axis=1)

if sample_rate != 16000:
    nb_samples = int(len(data) * 16000 / sample_rate)
    data = resample(data, nb_samples)

data = data.astype(np.float32)

print("Transcription : ", transcribe(data))

