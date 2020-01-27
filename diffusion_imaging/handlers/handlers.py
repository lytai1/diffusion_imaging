from abc import ABC, abstractmethod
from dependency_injector import providers, containers
from dipy.core.gradients import gradient_table
import nibabel as nib
import os
import numpy as np
from itertools import groupby
import logging

logger = logging.getLogger(__name__)

from .containers import Patient, MRI


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
    
    def _make_patient(self, directory):
        
        patient = Patient()
        filtered_files = self._get_files(self.patient_directory)
        patient.directory = self.patient_directory
        patient.mri = self._make_mri(filtered_files)
        
        return patient
    
    def load(self):
        
        return self._make_patient(self.patient_directory)


class HCPLocalHandler(HandlerBase):
    """
    Class to hanlde the loading of the specific patient files from the Human Connectome Project
    """
    
    def __init__(self, config):
        self.config = config
        self.patient_directory = config['patient_directory']
        self.sub_directory = os.path.join("T1w", "Diffusion")
        self.label = "hcp"
        
    def _get_files(self, path):
        
        grouped_file_paths = []
        base = os.path.join(self.patient_directory, path, self.sub_directory)
        files = os.listdir(base)
        
        filtered = []
        for file in files:
            if not "eddylogs" in file and not "nodif_brain_mask" in file and not "grad_dev" in file:
                filtered.append(os.path.join(base, file))
        
        return filtered
        
    def _load_dwi(self, file):
        image = nib.load(file)
        return image
    
    def _load_bvec(self, file):
        return np.loadtxt(file)
    
    def _load_bval(self, file):
        return np.loadtxt(file)
    
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
        
        mri = MRI(nifti_image, gtab, self.label)
        
        return mri
        
    def load(self):
        
        patients = []
        for patient in os.listdir(self.patient_directory):
            p = Patient(patient_number=patient)
            
            filtered_files = self._get_files(os.path.join(self.patient_directory,
                                                         patient))
            p.directory = os.path.join(self.patient_directory, patient) 
            p.mri = self._make_mri(filtered_files)
            patients.append(p)
            
        return patients
        

class DMIPYLocalHandler(HCPLocalHandler):
    def __init__(self, config):
        self.config = config
        self.patient_directory = config['patient_directory']
        self.label = "andi"

    def _get_files(self, path=None):

        base = os.path.join(self.patient_directory, path)
        files = os.listdir(base)
        files_full_dir = []

        for file in files:
            files_full_dir.append(os.path.join(self.patient_directory, path, file))

        return files_full_dir


Handler = providers.FactoryAggregate(local=providers.Factory(LocalHandler))
