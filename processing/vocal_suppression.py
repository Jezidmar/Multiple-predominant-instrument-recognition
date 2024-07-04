import librosa
from scipy.signal import butter, filtfilt
import numpy as np

def suppress_vocals(audio_file, bass_cutoff=300, sr=22050):
    y, sr = librosa.load(audio_file, sr=sr, mono=False)
    # print(sr)
    cutoff_freq = bass_cutoff

    # Get the filter coefficients for a Butterworth highpass filter
    nyquist_freq = 0.5 * sr
    cutoff_normalized = cutoff_freq / nyquist_freq
    b, a = butter(1, cutoff_normalized, btype='highpass')

    # Apply the filter to the audio signal
    y_filtered = filtfilt(b, a, y)

    bass = y - y_filtered

    # Separate left and right channels
    left_channel = y_filtered[0]
    right_channel = y_filtered[1]

    # Subtract higher frequency signals from left and right channels
    vocals_removed_left = left_channel - right_channel
    vocals_removed_right = right_channel - left_channel

    # # Add the bass signal back to the instrumental signal
    instrumental_audio_left = vocals_removed_left + bass[0]
    instrumental_audio_right = vocals_removed_right + bass[1]
    # instrumental_audio = vocals_removed_left + bass[0]

    instrumental_audio = np.vstack([instrumental_audio_left, instrumental_audio_right])

    # instrumental_audio, _ = librosa.effects.hpss(instrumental_audio)

    return librosa.to_mono(instrumental_audio), sr
