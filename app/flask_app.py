from typing import Dict, Union
from flask import Flask, render_template, request, jsonify
from werkzeug.datastructures import FileStorage
from models.cqt_model import CqtModel
from models.mel_model import MelModel
from app_config import cqt_model_names, mel_model_names, CQT, MEL, DEFAULT_MODEL_NAME
from json import loads
from models.model_runner import parallelize_predictions

app = Flask(__name__)
models: Dict[str, Union[MelModel, CqtModel]] = {}
model_names = cqt_model_names | mel_model_names

default_weights = {model_name: "1" if model_name ==
                   DEFAULT_MODEL_NAME else "0" for model_name in model_names}

for model_name in cqt_model_names.keys():
    models[model_name] = (CqtModel(CQT, model_name))

for model_name in mel_model_names.keys():
    models[model_name] = (MelModel(MEL, model_name))


@app.route("/")
def index():
    return render_template("index.html", model_names=model_names, DEFAULT_MODEL_NAME=DEFAULT_MODEL_NAME)


@app.route("/analyze_files/single_model", methods=["POST"])
def single_model_analyze():
    wav_files: list[FileStorage] = request.files.getlist("wav_files")
    model_name = request.form.get("model_name", DEFAULT_MODEL_NAME)

    model = models[model_name]
    predictions = parallelize_predictions([model], wav_files)
    return jsonify(predictions)


@app.route("/analyze_files/mix_model", methods=["POST"])
def mix_model_analyze():
    wav_files: list[FileStorage] = request.files.getlist("wav_files")
    model_weights = request.form.get(
        "model_weights", default_weights)

    model_weights = parse_weights_dict(model_weights)

    weighted_models = []
    for model in models.values():
        if model_weights[model.name] > 0:
            weighted_models.append(model)

    predictions = parallelize_predictions(
        weighted_models, wav_files, model_weights)
    return jsonify(predictions)


def parse_weights_dict(weights_dict_json) -> Dict[str, int]:
    weights_dict = loads(weights_dict_json)
    for k, v in weights_dict.items():
        weights_dict[k] = float(v)

    return weights_dict
