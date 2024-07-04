import os
PROJECT_ROOT = os.environ.get("PROJECT_ROOT")
import yaml

with open(os.path.join(PROJECT_ROOT, 'config.yml'), 'r') as f:
    config = yaml.full_load(f)
    
training_data_relative_path = config['paths']['training_data_relative_path']
raw_training_data_path = os.path.join(PROJECT_ROOT, training_data_relative_path, 'raw')

changed_training_data_path = os.path.join(PROJECT_ROOT, training_data_relative_path, 'processed', 'augmented', 'overlay')

dir = raw_training_data_path
instr = [dir + '/' + d for d in os.listdir(dir) if '-' not in d]

from pydub import AudioSegment
from random import shuffle
import itertools, os, numpy as np

NUM_IN_COMBINATION = 3
if NUM_IN_COMBINATION == 3:
    for (instr1, instr2, instr3) in list(itertools.combinations(instr, 3)):

        list1 = [instr1+'/'+f for f in os.listdir(instr1)]
        list2 = [instr2+'/'+f for f in os.listdir(instr2)]
        list3 = [instr3+'/'+f for f in os.listdir(instr3)]
        shuffle(list1); shuffle(list2); shuffle(list3)

        folder = instr1[-3:]+'-'+instr2[-3:]+'-'+instr3[-3:]
        os.makedirs(changed_training_data_path+folder,exist_ok=True)

        
        lists = [list1,list2,list3]
        m = np.argmin([len(lists[0]),len(lists[1]),len(lists[2])])

        for i in range(len(lists[m])):
            sound1 = AudioSegment.from_file(lists[m][i])
            sound2 = AudioSegment.from_file(lists[(m+1)%3][i])
            sound3 = AudioSegment.from_file(lists[(m+2)%3][i])
            mix = (sound1.overlay(sound2)).overlay(sound3)
            mix.export(dir + '/' + folder + '/' + folder + '_' + str(i+1) + '.wav', format='wav') 
        print("Done with folder:",folder)