import numpy as np
from numba import njit
from librosa import stft
from librosa.feature import melspectrogram
from librosa.core import power_to_db
from models.abstract_model import Model


class MelModel(Model):
    SAMPLING_RATE = 44100
    N_BINS = 128
    HOP_LENGTH = 441
    N_FFT = 8192
    WIN_LENGTH = 2205

    def preprocess_audio(self, audio: np.ndarray):
        audio = audio / np.sqrt(np.mean(audio**2))
        stft_output = stft(audio, n_fft=self.N_FFT, hop_length=self.HOP_LENGTH, win_length=self.WIN_LENGTH,
                           window='hann')
        mel_spec = melspectrogram(
            S=np.abs(stft_output)**2, sr=self.SAMPLING_RATE, n_mels=self.N_BINS, fmin=0.0, fmax=None)
        mel_spDB = power_to_db(mel_spec, ref=np.max)

        chunks = []
        for start_idx in range(0, mel_spDB.shape[1] - 100 + 1, 100):
            chunks.append(mel_spDB[:, start_idx:start_idx + 100])

        return [np.expand_dims(np.array(chunks), -1)]

    def predict(self, audio, model_weight=1):
        chunks = self.preprocess_audio(audio)
        fold_predictions = []
        for fold in self.model_folds:
            prediction = np.array(
                [np.sum(fold.predict(chunk), 0) for chunk in chunks])
            prediction = prediction / np.max(prediction, axis=1, keepdims=True)
            fold_predictions.append(prediction)

        return self.post_process_predictions(fold_predictions, model_weight)
