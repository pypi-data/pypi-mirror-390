from . import icd_cohort_combined_searching
from . import cxr_preproc
from . import ecg_preproc
from . import echo_preproc
from . import wave_preproc
from . import combination_util
import pandas as pd

VALID_ROTATIONS = ['postero-anterior', 'lateral', 'antero-posterior', 'left lateral','erect', 'recumbent', 'left anterior oblique']


def search(regex_icd):
    '''
    Search all the subject ids that have the icd codes parsed in the regex statement

    Input
    -----
        regex_icd (str) : Regex statement for all ICD codes you want to search

    Return
    ------
    DataFrame - all subject ids that have the icd diagnoses
    '''
    return icd_cohort_combined_searching.icd_combined_search(regex_icd)

class MimicCXR:
    path : str
    rotations: list[str]
    regex_icd = str

    def __init__(self, path, rotations=None, regex_icd=None):
        self.path = path
        self.regex_icd: icd
        if rotations != None and rotations.lower() not in VALID_ROTATIONS:
            raise ValueError(f'Rotations not in {VALID_ROTATIONS}')
        self.rotations = rotations

    def cohort(self, tensor=False, embedding=False, subject_ids=None):
        '''
        Search a cohort, and have it return filtered with tensor, embedding, and subject ids
    
        Input
        -----
        tensor (bool) - Do you want to turn the images into a tensor?
        embedding (bool) - Do you want to turn the images into embeddings?
        subject_ids (list[int]) - Return the list of subject ids you want to search by. 
    
        Return
        ------
        DataFrame - the filtered cohort of the folder of images. 
        '''
        
        if subject_ids == None and self.regex_icd:
            subject_ids = search(self.regex_icd)
        return cxr_preproc.open_images(self.rotations, tensor, embedding, subject_ids)


class MimicECG:
    path: str
    regex_icd : str
        
    def __init__(self, path, regex_icd=None):
        self.path = path
        self.regex_icd = regex_icd

    def cohort(self, tensor=False, embedding=False, subject_ids=None):
        '''
        Search a cohort, and hav it return filtered with tensor, embedding, and subject ids

        Input
        -----
        tensor (bool) - Do you want to turn the images into a tensor?
        embedding (bool) - Do you want to turn the images into embeddings?
        subject_ids (list[int]) - Return the list of subject ids you want to search by. 

        Return
        ------
        DataFrame - the filtered cohort of the folder of ECGS.
        '''
        if subject_ids == None and self.regex_icd:
            subject_ids = search(self.regex)
        return echo_preproc.extract_data(self.path, tensor, embedding, subject_ids)

class MimicECHO:
    path : str
    regex_icd : str

    def __init__(self, path, regex_icd=None):
        self.path = path
        self.regex_icd = regex_icd

    def cohort(self, tensor=False, embedding=False, subject_ids=None):
        '''
        Search a cohort, and hav it return filtered with tensor, embedding, and subject ids

        Input
        -----
        tensor (bool) - Do you want to turn the images into a tensor?
        embedding (bool) - Do you want to turn the images into embeddings?
        subject_ids (list[int]) - Return the list of subject ids you want to search by. 

        Return
        ------
        DataFrame - the filtered cohort of the folder of ECHOS.
        '''
        if subject_ids == None and self.regex_icd:
            subject_ids = search(self.regex_icd)
        return echo_preproc.extract_data(self.path, tensor, embedding, subject_ids)

class MimicWAVE:
    path:str
    regex_icd:str

    def __init__(self, path, regex_icd=None):
        self.path = path
        self.regex_icd = regex_icd

    def cohort(self, tensor=False, embedding=False, subject_ids=None):
        '''
        Search a cohort, and hav it return filtered with tensor, embedding, and subject ids

        Input
        -----
        tensor (bool) - Do you want to turn the images into a tensor?
        embedding (bool) - Do you want to turn the images into embeddings?
        subject_ids (list[int]) - Return the list of subject ids you want to search by. 

        Return
        ------
        DataFrame - the filtered cohort of the folder of WAVE.
        '''
        if subject_ids == None and self.regex_icd:
            subject_ids = search(self.regex_icd)
        return wave_preproc.extract_data(self.path, tensor, embedding, subject_ids)

def combine(*dfs, drop_nan):
    '''
    Combine all modalities. Make a tabular dataframe the first to have it combined on timeseries. 

    Input
    -----
    modalities (list[str]) - give the name of the modalities
    drop_nan (boolean) - whether or not to automatically drop nan rows (any row that contains nan)

    Return
    ------
    DataFrame - all the modalities combined. 
    '''
    return combination_util.raw_combine_modalities(dfs)
    
    
        


    
        
    
    
    
    
    

    