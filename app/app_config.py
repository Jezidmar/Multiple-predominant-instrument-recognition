import os

PRODUCTION = os.environ.get("PRODUCTION", False)
MODELS_DIR = os.path.join("app", "hdf5_files")

instruments = {
    0: "cel",
    1: "cla",
    2: "flu",
    3: "gac",
    4: "gel",
    5: "org",
    6: "pia",
    7: "sax",
    8: "tru",
    9: "vio",
    10: "voi",
}

CQT = "cqt"
MEL = "mel"
DEFAULT_MODEL_NAME = "bpm_mix"
cqt_model_names = {"bpm_mix": "BPM Mix", "genre_mix": "Genre Mix"}
mel_model_names = {"cnn_mono_mel": "CNN Mono Mel"}
