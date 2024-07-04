import os

PROJECT_ROOT = os.environ.get("PROJECT_ROOT")

import yaml

with open(os.path.join(PROJECT_ROOT, 'config.yml'), 'r') as f:
    config = yaml.full_load(f)

print(config)
print(type(config))

import librosa
import numpy as np

def remove_background(audio_file):
    y, sr = librosa.load(audio_file, sr=44100, mono=True)

    S_full, phase = librosa.magphase(librosa.stft(y))

    S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))
    
    S_filter = np.minimum(S_full, S_filter)

    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)

    S_background = mask_i * S_full
    D_background = S_background * phase
    y_background = librosa.istft(D_background)

    y_background = np.pad(librosa.to_mono(y_background), 168, 'edge')

    return y_background, sr