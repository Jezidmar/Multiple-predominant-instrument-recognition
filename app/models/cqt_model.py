import numpy as np
from librosa.core import cqt, amplitude_to_db
from models.abstract_model import Model
from pydub.utils import make_chunks


class CqtModel(Model):
    SAMPLING_RATE = 22050
    N_BINS = 96
    BINS_PER_OCTAVE = 12
    HOP_LENGTH = 256

    def predict(self, audio, model_weight=1):
        preprocessed_chunks = self.preprocess_audio(audio)
        fold_predictions = []
        for fold in self.model_folds:
            prediction = np.array(
                [np.max(fold.predict(chunk), 0)
                 for chunk in preprocessed_chunks]
            )
            fold_predictions.append(prediction)

        return self.post_process_predictions(fold_predictions, model_weight)

    def preprocess_audio(self, audio: np.ndarray) -> list:
        preprocessed_chunks = []
        chunks = make_chunks(audio, self.SAMPLING_RATE)

        for wav_chunk in chunks:
            wav_chunk = wav_chunk / np.sqrt(np.mean(wav_chunk**2))
            cqt_output = cqt(
                wav_chunk,
                n_bins=self.N_BINS,
                bins_per_octave=self.BINS_PER_OCTAVE,
                hop_length=self.HOP_LENGTH,
            )
            cqt_output = np.abs(cqt_output)
            cqt_output = amplitude_to_db(cqt_output)
            preprocessed_chunks.append(cqt_output)
        return [np.expand_dims(np.array(preprocessed_chunks), -1)]
