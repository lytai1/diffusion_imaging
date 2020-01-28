from abc import ABC, abstractmethod
from dependency_injector import providers, containers
from dipy.core.gradients import gradient_table
import nibabel as nib
import os
import numpy as np
from itertools import groupby
import logging

logger = logging.getLogger(__name__)

from .containers import Patient, MRI, build_mri


class HandlerBase(ABC):
    """
    Base class for the Handler functions for the loading of data
    """
    
    @abstractmethod
    def load(self):
        pass

class LocalHandler(HandlerBase):
    
    def __init__(self, patient_directory, label):
        self.patient_directory = patient_directory
        self.label = label
        
    def _filter(self, file, filters):
        
        for filt in filters:
            if filt in file:
                return True
            
        return False
        
    def _get_files(self, path, filters=[]):
        
        grouped_file_paths = []
        files = os.listdir(self.patient_directory)
        
        filtered = []
        for file in files:
            if len(filters):
                if not self._filter(file, filters):
                    filtered.append(os.path.join(self.patient_directory, file))
            else:
                filtered.append(os.path.join(self.patient_directory, file))
        
        return filtered
    
    def _load_dwi(self, file):
        image = nib.load(file)
        return image
    
    def _make_mri(self, filtered_files):

        # The group is the group associated with the specific 'dir*'
        # this includes both LR and RL orientations
        print(filtered_files)
        for file in filtered_files:
            if "bvec" in os.path.basename(file):
                bvecs_file_path = file
            elif "bval" in os.path.basename(file):
                bvals_file_path = file
            elif os.path.basename(file).endswith('.nii.gz'):
                dwi_data = self._load_dwi(file)
                image = dwi_data.get_data()
                aff = dwi_data.affine
        
        # Take the 
        gtab = gradient_table(bvals_file_path, bvecs_file_path)
        
        nifti_image = nib.Nifti1Image(image, aff)
        
        mri = build_mri(nifti_image, gtab, self.label)
        
        return mri
    
    def _make_patient(self, directory, filters):
        
        patient = Patient()
        filtered_files = self._get_files(self.patient_directory, filters=filters)
        patient.directory = self.patient_directory
        _, patient.patient_number = os.path.split(self.patient_directory)
        patient.mri = self._make_mri(filtered_files)
        
        return patient
    
    def load(self, filters):
        
        return self._make_patient(self.patient_directory, filters)


def make_handler(patient_directory, label):

    switch = {
        "hcp": HCPLocalHandler,
        "adni": ADNILocalHandler,
        "rosen": RosenLocalHandler
    }

    return switch[label](patient_directory)


class HCPLocalHandler(LocalHandler):

    def __init__(self, patient_directory, label='hcp'):
        super(HCPLocalHandler, self).__init__(patient_directory, label)

    def load(self, filters=["nodif_brain_mask.nii.gz"]):

        return self._make_patient(self.patient_directory, filters)
        

class ADNILocalHandler(LocalHandler):

    def __init__(self, patient_directory, label='adni'):
        super(ADNILocalHandler, self).__init__(patient_directory, label)

    def load(self, filters=[]):

        return self._make_patient(self.patient_directory, filters)


class RosenLocalHandler(LocalHandler):

    def __init__(self, patient_directory, label='rosen'):
        super(RosenLocalHandler, self).__init__(patient_directory, label)

    def load(self, filters=[]):

        return self._make_patient(self.patient_directory, filters)


Handler = providers.FactoryAggregate(local=providers.Factory(LocalHandler))
