import os
import numpy as np
from os.path import basename
import subprocess
from scipy.io.wavfile import read,write
import librosa
import crepe
import scipy.signal

def bpm_sync(file1, file2):

    wav, sr = librosa.load(file1, mono=True, sr=22050)
    bpm_base, _ = librosa.beat.beat_track(y=wav, sr=sr)

    wav, sr = librosa.load(file2, mono=True, sr=22050)
    bpm, _ = librosa.beat.beat_track(y=wav, sr=sr)
    wav = librosa.effects.time_stretch(wav, bpm_base/bpm)

    if len(wav) > 3 * sr: wav = wav[:3 * sr]
    else: wav = np.pad(wav, (0, 3 * sr - len(wav)), 'wrap')

    return wav, sr
