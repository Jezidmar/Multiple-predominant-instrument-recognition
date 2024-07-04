import os
import numpy as np
from os.path import basename
import subprocess
from scipy.io.wavfile import read,write
import librosa
import crepe
import scipy.signal

def pitch_sync(file1, file2):
    
    wav1, sr = librosa.load(file1, mono=True, sr=22050)
    wav2, sr = librosa.load(file2, mono=True, sr=22050)


    pitch1 = crepe.predict(wav1, sr, viterbi=False)
    pitch2 = crepe.predict(wav2, sr, viterbi=False) 

    shifts = 12 * np.log2(pitch1 / pitch2)
    filter_size = int(0.09 * len(shifts))
    shifts_filtered = scipy.signal.medfilt(shifts, kernel_size=filter_size)


    segment_length = wav2.shape[0] / len(shifts_filtered)
    shifted_wav2 = np.copy(wav2)

    for i in range(0, len(shifts_filtered) - 1):
        wav2_segment = wav2[int(i * segment_length) : int((i + 1) * segment_length)]
        shifted_wav2[int(i * segment_length) : int((i + 1) * segment_length)] = pyrubberband.pyrb.pitch_shift(wav2_segment, sr, shifts_filtered[i])

    if len(shifted_wav2) > 3 * sr: shifted_wav2 = shifted_wav2[:3 * sr]
    else: shifted_wav2 = np.pad(shifted_wav2, (0, 3 * sr - len(shifted_wav2)),'wrap')
    
    return shifted_wav2, sr

