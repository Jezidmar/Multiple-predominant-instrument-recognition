import random
import os
import numpy as np
import tempfile
from os.path import basename
import subprocess
from scipy.io.wavfile import read,write
import math
import librosa

def add_noise(file, noise_path, snr=20):
    """ Add noise to infile

    Args:
        infile (str): Filename
        noise_name (str): Name of noise (currently only 'white-noise')
        snr (float): SNR of output sound
    """

    x, sr = librosa.load(file, mono=True, sr=22050)

    z, _ = librosa.load(noise_path, mono=True, sr=22050)

    while z.shape[0] < x.shape[0]:
        z = np.concatenate((z, z), axis=0)
    z = z[0: x.shape[0]]
    
    rms_z = np.sqrt(np.mean(np.power(z, 2)))
    rms_x = np.sqrt(np.mean(np.power(x, 2)))
    snr_linear = 10 ** (snr / 20.0)
    noise_factor = rms_x / rms_z / snr_linear
    y = x + z * noise_factor
    rms_y = np.sqrt(np.mean(np.power(y, 2)))
    y = y * rms_x / rms_y

    return y, sr