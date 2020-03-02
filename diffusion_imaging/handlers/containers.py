from dmipy.core.acquisition_scheme import gtab_dipy2dmipy
from dipy.segment.mask import median_otsu, bounding_box

class MRI:
    """
    Wrapper class for each MRI processed
    
    Args:
        image (Nifti1Image): The resulting loaded image in the Nifti1Image class loaded from the dwi and the affine values
        gradient_table (gradient_table): The gradient table found through the b-values and b-vectors from the given data
        year (str): The given year?
        orientation (str): Possible use 
    """
    def __init__(self, nifti_image, gradient_table, label, mask=None):
        
        self.nifti_image = nifti_image
        self.label = label
        self.gradient_table = gradient_table

        self.data = self.nifti_image.get_data()
        self.scheme = gtab_dipy2dmipy(self.gradient_table)

        if mask is not None: 
            self.mask = mask.get_data()
        else:
            self.make_mask()

        self.bound_data()

    def make_mask(self, *args, **kwargs):
        _, self.mask = median_otsu(self.data, kwargs)

    def bound_data(self):

        min_indicies, max_indicies = bounding_box(self.mask)

        min_x, min_y, min_z = min_indicies
        max_x, max_y, max_z = max_indicies

        self.data = self.data[min_x:max_x, min_y:max_y, min_z:max_z, :]
        self.mask = self.mask[min_x:max_x, min_y:max_y, min_z:max_z]



def build_mri(nifti_image, gradient_table, label, mask):
    switch = {
        "hcp": HCPMRI,
        "adni": ADNIMRI,
        "rosen": RosenMRI
    }

    return switch[label](nifti_image=nifti_image, gradient_table=gradient_table, label=label, mask=mask)

class HCPMRI(MRI):

    def __init__(self, nifti_image, gradient_table, label, mask):
        super(HCPMRI, self).__init__(nifti_image=nifti_image, gradient_table=gradient_table, label=label, mask=mask)

    def pull_axial_slices(self, start, end): # this might not be axial
        return self.data[:, :, start : end, :]

    def pull_axial_middle_slice(self):
        slice_index = self.data.shape[2] // 2
        return self.data[:, :, slice_index : slice_index + 1, :]
    

class ADNIMRI(MRI):

    def __init__(self, nifti_image, gradient_table, label, mask):
        super(ADNIMRI, self).__init__(nifti_image=nifti_image, gradient_table=gradient_table, label=label, mask=mask)

    def pull_axial_slices(self, start, end):
        return self.data[:, :, start : end, :]

    def pull_middle_slice(self):
        slice_index = self.data.shape[1] // 2
        return self.data[:, slice_index : slice_index + 1]


class RosenMRI(MRI):

    def __init__(self, nifti_image, gradient_table, label, mask):
        super(RosenMRI, self).__init__(nifti_image=nifti_image, gradient_table=gradient_table, label=label, mask=mask)

    def pull_axial_slices(self,  start, end):
        return self.data[:, :, start : end, :]

    def pull_axial_middle_slice(self):
        slice_index = self.data.shape[2] // 2
        return self.data[:, :, slice_index : slice_index + 1, :]

class Patient:
    
    def __init__(self, patient_number=None, mri=None):
        self.patient_number = patient_number
        self.mri = mri
        self.directory = ""
        
    def __str__(self):
        return f"Patient(parient_number = {self.patient_number})"
    
class Info:

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
