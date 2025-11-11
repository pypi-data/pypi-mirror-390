import os
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
import pydicom
from PIL import Image
from . import image_embeddings
import ast
import torch
import torchvision.transforms as transforms
from tqdm import tqdm
from importlib.resources import files
from transformers import AutoImageProcessor, ResNetForImageClassification

with files("MIMICEmbedding.mappings").joinpath("echo-record-list.csv.gz").open("rb") as f:
    mapping_df = pd.read_csv(f, compression="gzip")

#recursively find the root and append on to the record_list path

processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")


def _dicom_to_images(image_path):
    dicom = pydicom.dcmread(image_path)
    image = dicom.pixel_array.astype(float)
    rescaled_image = (np.maximum(image, 0) / image.max()) * 255
    final_image = np.uint8(rescaled_image)
    final_image = np.squeeze(final_image)
    if final_image.ndim == 4:
        final_image = final_image[0]
    if final_image.ndim == 3 and final_image.shape[-1] == 1:
        final_image = final_image[:, :, 0]

    return Image.fromarray(final_image)


def _get_image_tensor(dicom, op: bool):
    image = _dicom_to_images(dicom)
    inputs = processor(images=image, return_tensors="pt")
    tensor = inputs["pixel_values"].squeeze(0)  # shape (3, H, W)

    if op:
        return tensor.numpy().tolist()
    return tensor

def _build_embeddings_from_tensor_csv(tensor_csv):
    df = pd.read_csv(tensor_csv)

    embeddings = []
    print('Creating embeddings for ECHO...')
    for _, row in tqdm(df.iterrows(), total=len(df)):
        tensor = torch.tensor(eval(row['tensor_list']))  
        tensor = tensor.unsqueeze(0)  

        with torch.no_grad():
            output = model(tensor)   
            emb = output.logits      
        embeddings.append(emb.squeeze().numpy().tolist())

    df['embedding'] = embeddings
    df.to_csv(tensor_csv, index=False)
    print(f"saved embeddings to {tensor_csv}")
    return df
    

def _get_note_info(note_df,file_id, col):
    file_id_str = str(file_id).strip()
    
    note_df['dicom_filepath'] = note_df['dicom_filepath'].apply(lambda x: os.path.splitext(x.split('/')[-1])[0])

    match = note_df[note_df['dicom_filepath'] == file_id_str]

    if match.empty:
        raise ValueError(f"No match found for file_id: {file_id_str}")
    if col not in match.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")

    return match.iloc[0][col]

def _find_image_path(image_name):
    for root, dirs, files in os.walk(wave_path):  # not root_dir
        for file in files:
            if os.path.splitext(file)[0] == image_name:
                return os.path.join(root, file)
    return None



def extract_data(wave_path, op, tensor_op, embedding_op, subject_ids=None):
    print('===========MIMIC-IV ECHO============')
    records = []
    files = os.listdir(wave_path)

    print('Preparing ECHO cohort...')
    for file in tqdm(files, total=len(files)):
        file_name = os.path.splitext(file)[0]

        file_path = None
        if op:
            file_path = _find_image_path(file_name)

        if tensor_op:
            record = {
                'subject_id': _get_note_info(mapping_df, file_name, 'subject_id'),
                'study_id': file_name,
                'acquisition_datetime': _get_note_info(mapping_df, file_name, 'acquisition_datetime'),
                'dicom_filepath': file_path,
                'tensor': _get_image_tensor(file_path, False),
                'tensor_list': _get_image_tensor(file_path, True)
            }
        else:
            record = {
                'subject_id': _get_note_info(mapping_df, file_name, 'subject_id'),
                'study_id': file_name,
                'acquisition_datetime': _get_note_info(mapping_df, file_name, 'acquisition_datetime'),
                'dicom_filepath': file_path,
            }

        records.append(record)

    df = pd.DataFrame(records)

    # Filter by subject_ids if provided
    if subject_ids is not None and len(subject_ids) > 0:
        df = df[df['subject_id'].isin(subject_ids)]

    out_csv = os.path.join('data', 'cohort', 'mimiciv_echo_cohort.csv.gz')

    if embedding_op and tensor_op:
        df = _build_embeddings_from_tensor_csv(out_csv)

    print(f"[SAVED {out_csv}]")
    return df
