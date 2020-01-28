from dmipy.core.acquisition_scheme import gtab_dipy2dmipy

class MRI:
    """
    Wrapper class for each MRI processed
    
    Args:
        image (Nifti1Image): The resulting loaded image in the Nifti1Image class loaded from the dwi and the affine values
        gradient_table (gradient_table): The gradient table found through the b-values and b-vectors from the given data
        year (str): The given year?
        orientation (str): Possible use 
    """
    def __init__(self, nifti_image, gradient_table, label):
        
        self.nifti_image = nifti_image
        self.label = label
        self.gradient_table = gradient_table

        self.data = self.nifti_image.get_data()
        self.scheme = gtab_dipy2dmipy(self.gradient_table)


def build_mri(nifti_image, gradient_table, label):
    switch = {
        "hcp": HCPMRI,
        "adni": ADNIMRI,
        "rosen": RosenMRI
    }

    return switch[label](nifti_image, gradient_table, label)

class HCPMRI(MRI):

    def __init__(self, nifti_image, gradient_table, label):
        super(HCPMRI, self).__init__(nifti_image, gradient_table, label)

    def pull_axial_slices(self, start, end): # this might not be axial
        return self.data[:, start : end]

    def pull_middle_slice(self):
        slice_index = self.data.shape[1] // 2
        return data[:, slice_index : slice_index + 1]
    

class ADNIMRI(MRI):

    def __init__(self, nifti_image, gradient_table, label):
        super(ADNIMRI, self).__init__(nifti_image, gradient_table, label)

    def pull_axial_slices(self, start, end):
        return self.data[:, :, start : end, 0]

    def pull_middle_slice(self):
        slice_index = self.data.shape[1] // 2
        return data[:, slice_index : slice_index + 1]


class RosenMRI(MRI):

    def __init__(self, nifti_image, gradient_table, label):
        super(RosenMRI, self).__init__(nifti_image, gradient_table, label)

    def pull_axial_slices(self,  start, end):
        return self.data[:, :, start : end, :]

    def pull_middle_slice(self):
        slice_index = self.data.shape[2] // 2
        return data[:, :, slice_index : slice_index + 1, :]

class Patient:
    
    def __init__(self, patient_number=None, mri=None):
        self.patient_number = patient_number
        self.mri = mri
        self.directory = ""
        
    def __str__(self):
        return f"Patient(parient_number = {self.patient_number})"
    
