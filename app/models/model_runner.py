import concurrent.futures
from io import BytesIO
from typing import Dict, List, Union
from librosa import load
from werkzeug.datastructures import FileStorage
from models.mel_model import MelModel
from models.cqt_model import CqtModel


def parallelize_predictions(models: List[Union[MelModel, CqtModel]], wav_files: List[FileStorage], model_weights=None):
    predictions_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for wav_file in wav_files:
            multi_sr_file = multi_sr_file_load(wav_file)

            for model in models:
                audio = multi_sr_file[model.SAMPLING_RATE]
                future = executor.submit(
                    preprocess_and_predict, audio, wav_file.filename, model, model_weights)
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            prediction = future.result()
            predictions_list.append(prediction)

    predictions = unify_predictions(predictions_list)

    return predictions


def preprocess_and_predict(audio, filename, model, model_weights=None):
    model_weight = model_weights[model.name] if model_weights else 1
    prediction = model.predict(audio, model_weight)
    return {filename: prediction}


def multi_sr_file_load(wav_file):
    file_content = wav_file.read()
    audio_44100, _ = load(BytesIO(file_content), sr=44100, mono=True)
    audio_22050, _ = load(BytesIO(file_content), sr=22050, mono=True)
    return {22050: audio_22050, 44100: audio_44100}


def unify_predictions(predictions_list: List[Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
    unified_predictions = {}

    for prediction in predictions_list:
        for song_name, prediction_dict in prediction.items():
            if song_name not in unified_predictions:
                unified_predictions[song_name] = prediction_dict
            else:
                for instr, value in prediction_dict.items():
                    unified_predictions[song_name][instr] += value

    for song_name, prediction_dict in unified_predictions.items():
        for instr, value in prediction_dict.items():
            unified_predictions[song_name][instr] = 1 if value > 0.5 else 0

    return unified_predictions
