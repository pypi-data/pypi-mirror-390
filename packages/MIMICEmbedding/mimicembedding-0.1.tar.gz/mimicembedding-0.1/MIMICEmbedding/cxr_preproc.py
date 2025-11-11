import os
import sys
import shutil
import pandas as pd
from tqdm import tqdm
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from torchvision.transforms import transforms
from pathlib import Path
from importlib.resources import files




def _splitext(path, num):
    return os.path.splitext(path)[num]

def _recursive_search(directory):
    data = []
    for file in Path(directory).rglob('*'):
        if file.is_file():
            data.append(file)
    return data
    
def _merge_embedding(df):
    image_embeddings = ie.get_embeddings()
    if "dicom" in df.columns:
        df = df.rename(columns={"dicom": "dicom_id"})
    # option 2: only keep rows where embeddings exist
    return df.merge(image_embeddings, on=["subject_id", "dicom_id"], how="inner")


def _turn_to_tensor(image_file):
    ext = os.path.splitext(image_file)[-1].lower()
    if ext in ['.jpg', '.jpeg', '.dcm']:
        try:
            image = Image.open(image_file).convert("RGB")  # ensure 3 channels
            transform = transforms.ToTensor()
            tensor = transform(image)
            return tensor
        except Exception as e:
            print(f"Failed to load {image_file}: {e}")
            return None
    else:
        return None
    
def _find_image_path(image_name):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if os.path.splitext(file)[0] == image_name:
                return os.path.join(root, file)


def _open_maps():

    with files("MIMICEmbedding.mappings").joinpath("mimic-cxr-2.0.0-metadata.csv.gz").open("rb") as f:
        metadata = pd.read_csv(f, compression="gzip")
    with files("MIMICEmbedding.mappings").joinpath("mapped_cxr_studies.csv.gz").open("rb") as f:
        df = pd.read_csv(f, compression="gzip")
        
    return metadata, df
    
def open_images(path, rotation=None, tensor=False, embedding=False, subject_ids=None):
    if rotation:
        print(f'ROTATIONS: {rotation}')
    else:
        rotation = []

    metadata, df = _open_maps()

    cxr_dir_list = os.listdir(path)

    cxr_files = [d for d in cxr_dir_list if d.endswith(('.dcm', '.jpg'))]
    directories = [d for d in cxr_dir_list if d not in cxr_files]

    for d in directories:
        cxr_files.extend(_recursive_search(os.path.join(path, d)))

    columns = [
        'dicom', 'image_path', 'subject_id', 'study_id',
        'rotation', 'study_text'
    ]
    if tensor:
        columns.append('image_tensor')

    metadata_list = []

    for image in tqdm(cxr_files, total=len(cxr_files), desc="Processing CXR files"):
        image_id = os.path.splitext(os.path.basename(image))[0]
        cxr_path = _find_image_path(image_id)
        if cxr_path is None:
            continue

        dicom_id = _splitext(image, 0)
        type_id = _splitext(image, -1)

        image_metadata = metadata[metadata['dicom_id'] == dicom_id]

        # filter by subject_ids if provided
        if subject_ids is not None and not image_metadata.empty:
            if image_metadata['subject_id'].iloc[0] not in subject_ids:
                continue

        if not rotation:
            filtered = image_metadata
        else:
            filtered = image_metadata[
                image_metadata['ViewCodeSequence_CodeMeaning'].isin(rotation)
            ]

        if filtered.empty:
            continue

        rotation_value = filtered['ViewCodeSequence_CodeMeaning'].iloc[0]
        subject_id = filtered['subject_id'].iloc[0]
        study_id = filtered['study_id'].iloc[0]

        study_text = None
        study_row = df[df['study_id'] == study_id]
        if not study_row.empty:
            study_text = study_row['study'].iloc[0]

        row = [dicom_id, cxr_path, subject_id, study_id, rotation_value, study_text]

        if tensor:
            row.append(_turn_to_tensor(cxr_path))

        metadata_list.append(row)

    f_df = pd.DataFrame(metadata_list, columns=columns)
    return f_df

