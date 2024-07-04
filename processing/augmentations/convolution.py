import random
import os
import numpy as np
import tempfile
from os.path import basename
import subprocess
from scipy.io.wavfile import read,write
import math
import librosa

def convolve(file, noise_path, snr=20):
    """ Add noise to infile

    Args:
        infile (str): Filename
        noise_name (str): Name of noise (currently only 'white-noise')
        snr (float): SNR of output sound
    """

    y, sr = librosa.load(file, mono=True, sr=22050)
    level = 0.5

    x = np.copy(y)
    ir, _ = librosa.load(noise_path, mono=True,sr=22050)

    y = np.convolve(x, ir, 'full')[0:x.shape[0]] * level + x * (1 - level)

    return y, sr