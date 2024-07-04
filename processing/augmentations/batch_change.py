import os

PROJECT_ROOT = os.environ.get("PROJECT_ROOT")

import yaml

with open(os.path.join(PROJECT_ROOT, 'config.yml'), 'r') as f:
    config = yaml.full_load(f)
    
training_data_relative_path = config['paths']['training_data_relative_path']
raw_training_data_path = os.path.join(PROJECT_ROOT, training_data_relative_path, 'raw')

changed_training_data_path = os.path.join(PROJECT_ROOT, training_data_relative_path, 'processed', 'augmented', 'convolved')

import glob
import soundfile as sf

import gaussian_noise
for instrument in config['instruments'].keys():
    instrument_directory = os.path.join(raw_training_data_path, instrument, '*')
    changed_instrument_directory = os.path.join(changed_training_data_path, instrument)
    os.mkdir(changed_instrument_directory)
    for file in glob.glob(instrument_directory):
        changed_path = os.path.join(changed_instrument_directory, os.path.basename(os.path.normpath(file)))
        y, sr = gaussian_noise.add_noise(file, noise_path=os.path.join(PROJECT_ROOT, config['paths']['noise_relative_path'], 'sounds_ir_classroom.wav'))
        sf.write(changed_path, y, sr)