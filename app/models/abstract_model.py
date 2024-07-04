import numpy as np
from os import listdir
from os.path import join, abspath
from keras import Sequential
from keras.models import load_model
from functools import lru_cache
from app_config import MODELS_DIR


class Model():
    FOLD_COUNT = 5

    def __init__(self, folder_name, model_name) -> None:
        self.name = model_name
        self.model_folds: list[Sequential] = self.load_model_folds(folder_name,
                                                                   model_name)

    @lru_cache()
    def load_model_folds(self, folder_name, model_name):
        model_folds = []
        folder = (abspath(join(
            MODELS_DIR, folder_name, model_name)))

        for model_part_name in listdir(folder):
            model_part = join(folder, model_part_name)
            model_folds.append(load_model(model_part))
        return model_folds

    def post_process_predictions(self, fold_predictions: list[np.ndarray], model_weight=1) -> dict:
        from app_config import instruments

        instruments_prediction = {instr: 0 for instr in instruments.values()}

        # for fold_prediction in fold_predictions:
        #     for i, instr_pred in enumerate(fold_prediction[0]):
        #         prediction = instr_pred / self.FOLD_COUNT * model_weight
        #         instruments_prediction[instruments[i]] += prediction

        # prediction = np.sum(fold_predictions) instr_pred / self.FOLD_COUNT * model_weight
        # instruments_prediction[instruments[i]] += prediction

        prediction = 0
        for fold_prediction in fold_predictions:
            prediction += fold_prediction
        prediction = prediction / len(fold_predictions)
        prediction = prediction * model_weight

        for i in range(len(instruments.keys())):
            instruments_prediction[instruments[i]] = prediction[0, i]
        return instruments_prediction
