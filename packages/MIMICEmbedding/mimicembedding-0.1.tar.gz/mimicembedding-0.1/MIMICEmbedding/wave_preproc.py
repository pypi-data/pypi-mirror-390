import os
import pandas as pd
from tqdm import tqdm
from . import ecg_signal_embedding_extraction
from importlib.resources import files

with files("MIMICEmbedding.mappings").joinpath("wave_record_list.csv.gz").open("rb") as f:
    mapping_df = pd.read_csv(f, compression="gzip")

def _turn_to_embedding():
    return ecg_signal_embedding_extraction.extract_data('wave')

def _turn_to_tensor(record_name):
    record = wfdb.rdrecord(os.path.join(ecg_path, record_name))
    signal_data = record.p_signal
    ecg_tensor = torch.tensor(signal_data, dtype=torch.float32)
    return ecg_tensor

def _get_note_info(note_df,file_id, col):
    file_id_str = str(file_id).strip()
    note_df['file_name'] = note_df['file_name'].astype(str).str.strip()

    match = note_df[note_df['file_name'] == file_id_str]

    if match.empty:
        raise ValueError(f"No match found for file_id: {file_id_str}")
    if col not in match.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")

    return match.iloc[0][col]

def _find_image_path(image_name):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if os.path.splitext(file)[0] == image_name:
                return os.path.join(root, file)

def extract_data(wave_path, op, wave_tensor_op, wave_embedding_op, subject_ids=None):
    print('===========MIMIC-IV WAVEFORM============')
    records = []
    for file in tqdm(os.listdir(wave_path), total=len(os.listdir(wave_path))):
        file_name = os.path.splitext(file)[0]
        if op == 'Yes':
            file_path = _find_image_path(file_name)
        else:
            file_path = None

        if wave_tensor_op:
            records.append({
                'subject_id': _get_note_info(mapping_df, file_name, 'subject_id'),
                'study_id': _get_note_info(mapping_df, file_name, 'study_id'),
                'file_name': file_name,
                'path': file_path,
                'wave_tensor': _turn_to_tensor(file_name)
            })
        else:
            records.append({
                'subject_id': _get_note_info(mapping_df, file_name, 'subject_id'),
                'study_id': file_name,
                'wave_id': _get_note_info(mapping_df, file_name, 'wave_id'),
                'path': file_path
            })

    df = pd.DataFrame(records)

    # Filter by subject_ids if provided
    if subject_ids is not None and len(subject_ids) > 0:
        df = df[df['subject_id'].isin(subject_ids)]

    out_csv = os.path.join(root_dir, 'data', 'cohort', 'mimiciv_wave_cohort.csv.gz')
    df.to_csv(out_csv, compression='gzip')
    print('[SAVED COHORT]')

    if wave_embedding_op:
        _turn_to_embedding()

    return df

    



