import librosa
import numpy as np

def remove_drums(audio_file):
    y, sr = librosa.load(audio_file, sr=44100, mono=True)

    y_harmonic, _ = librosa.effects.hpss(y)

    return y_harmonic, sr