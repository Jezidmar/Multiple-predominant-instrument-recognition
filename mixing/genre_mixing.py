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
import itertools, os, re, numpy as np

for (instr1, instr2) in list(itertools.combinations(instr,2)):
    
    folder = instr1[-3:]+'-'+instr2[-3:]
    os.makedirs(changed_training_data_path+folder,exist_ok=True)
    
    list1 = [instr1+'/'+f for f in os.listdir(instr1)]
    list2 = [instr2+'/'+f for f in os.listdir(instr2)]
    shuffle(list1); shuffle(list2)
    
    genre1 = [re.findall('\[.*?\]',x)[-1] for x in list1]
    genre2 = [re.findall('\[.*?\]',x)[-1] for x in list2]
    common_genres = set(genre1).intersection(genre2)
    
    for x in common_genres:

        if instr1[-3:] in x: list1 = [instr1+'/'+f for f in os.listdir(instr1) if f.count(x)>1]
        else: list1 = [instr1+'/'+f for f in os.listdir(instr1) if f.count(x)>0]
        
        if instr2[-3:] in x: list2 = [instr2+'/'+f for f in os.listdir(instr2) if f.count(x)>1]
        else: list2 = [instr2+'/'+f for f in os.listdir(instr2) if f.count(x)>0]

        if len(list1)>=len(list2): list_b = list2; list_s = list1
        else: list_b = list1; list_s = list2
                
        for i in range(len(list_s)):
            sound1 = AudioSegment.from_file(list_s[i])
            sound2 = AudioSegment.from_file(list_b[i%len(list_b)])
            mix = sound1.overlay(sound2)
            mix.export(new_dir + folder + '/' + folder + x + '_' + str(i+1) + '.wav', format='wav') 
    
    print("Done with folder:",folder)

