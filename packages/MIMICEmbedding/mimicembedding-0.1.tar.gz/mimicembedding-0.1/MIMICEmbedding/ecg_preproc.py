import os
import pandas as pd
from tqdm import tqdm
import wfdb
import sys
from pathlib import Path
import numpy as np
import torch 
from . import ecg_signal_embedding_extraction
from importlib.resources import files

with files("MIMICEmbedding.mappings").joinpath("ecg_record_list.csv.gz").open("rb") as f:
    mapping_df = pd.read_csv(f, compression="gzip")



#recursively find the root and append on to the record_list path

def _turn_to_embedding():
    return ecg_signal_embedding_extraction.extract_data('ecg')
    
def _turn_to_tensor(record_name):
    record = wfdb.rdrecord(os.path.join(ecg_path, record_name))
    signal_data = record.p_signal
    ecg_tensor = torch.tensor(signal_data, dtype=torch.float32)
    return ecg_tensor

def _get_note_info(note_df, file_id, col):
    file_id_str = str(file_id).strip()
    note_df['file_name'] = note_df['file_name'].astype(str).str.strip()

    match = note_df[note_df['file_name'] == file_id_str]

    if match.empty:
        raise ValueError(f"No match found for file_id: {file_id_str}")
    if col not in match.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")

    return match.iloc[0][col]

def _recursive_search(directory):
    data = []
    for file in Path(directory).rglob('*'):
        if file.is_file():
            data.append(file)
    return data


def _find_image_path(image_name):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if os.path.splitext(file)[0] == image_name:
                return os.path.join(root, file)

def extract_data(path, tensor_op, embedding_op, subject_ids=None):
    print('===========MIMIC-IV ECG============')
    records = []

    ecg_dir_list = os.listdir(path)
    ecg_dir = [d for d in ecg_dir_list if d.endswith('.dat')]
    directories = [d for d in ecg_dir_list if d not in ecg_dir]
    for d in directories:
        ecg_dir.extend(_recursive_search(d))

    for file in tqdm(ecg_dir, total=len(ecg_dir)):
        file_name = os.path.splitext(file)[0]
        file_path = _get_note_info(mapping_df, file_name, 'path')
        file_path = _find_image_path(file_name)

        record = {
            'subject_id': _get_note_info(mapping_df, file_name, 'subject_id'),
            'study_id': _get_note_info(mapping_df, file_name, 'study_id'),
            'file_name': file_name,
            'ecg_time': _get_note_info(mapping_df, file_name, 'ecg_time'),
            'path': file_path
        }

        if tensor_op:
            record['ecg_tensor'] = _turn_to_tensor(file_name)

        records.append(record)

    df = pd.DataFrame(records)

    # If subject_id filter is passed, apply it here
    if subject_ids is not None and len(subject_ids) > 0:
        df = df[df['subject_id'].isin(subject_ids)]

    print(f'SIZE: {df.size}')
    df.to_csv(os.path.join(root_dir, 'data', 'cohort', 'mimiciv_ecg_cohort.csv.gz'))
    print('[SAVED COHORT]')

    if embedding_op:
        _turn_to_embedding()

    return df

        

    
    
    
    



    

    
    
    
    
