import os
import math
import base64
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
from transformers import AutoImageProcessor, ResNetForImageClassification
import wfdb
from pathlib import Path
import numpy as np
import torch 
ecg_dir = os.path.join('mimiciv', 'ecg')
cxr_dir = os.path.join('mimiciv', 'cxr')
cxr_metadata = os.path.join('mappings', 'mimic-cxr-2.0.0-metadata.csv.gz')
ecg_metadata = os.path.join('mappings', 'ecg_record_list.csv.gz')

def _resize_images(pil_image, target_width):
    image_aspect_ratio = pil_image.width/pil_image.height
    resized_pil_image = pil_image.resize(
        (target_width, math.floor(target_width * image_aspect_ratio)),
        resample=Image.Resampling.LANCZOS)
    np_image = np.array(resized_pil_image)
    if np_image.ndim < 3:
        np_image = np.stack([np_image] * 3, axis=-1)
        resized_pil_image = Image.fromarray(np_image.astype('uint8'))
    return resized_pil_image

def _convert_image_to_base64(pil_image):
    image_data = BytesIO()
    pil_image.save(image_data, format='JPEG')
    base64_string = base64.b64encode(image_data.getvalue()).decode('utf-8')
    return base64_string



def get_embeddings():
    df = pd.read_csv(cxr_metadata, compression='gzip')
    
    all_image_files = list(filter(lambda x: x.endswith('.jpg') or x.endswith('.jpeg'),
                                  os.listdir(cxr_dir)))
    all_image_urls = [os.path.join(cxr_dir, f) for f in all_image_files]

    payloads = pd.DataFrame({'image_file': all_image_files, 'image_urls': all_image_urls})
    payloads['type'] = 'cxr'

    payloads['file_stem'] = payloads['image_file'].str.replace(r"\.jpe?g$", "", regex=True)
    df['file_stem'] = df['dicom_id'].astype(str)  
    merged = payloads.merge(df, on="file_stem", how="left")

    images = [Image.open(path) for path in merged['image_urls']]
    target_width = 264
    resized_images = [_resize_images(img, target_width) for img in images]


    processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
    model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")
    
    inputs = processor(resized_images, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.logits  

    logits_df = pd.DataFrame({
        "embeddings": list(embeddings.numpy()),
        "subject_id": merged["subject_id"].values,
        "dicom_id": merged["dicom_id"].values,
    })
    
    # save
    return logits_df

    
        
                                    
    

