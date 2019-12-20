from abc import (
    ABC,
    abstractmethod
)
import dipy.reconst.fwdti as fwdti
from dmipy.signal_models import cylinder_models, gaussian_models
from dmipy.core.modeling_framework import *
from dmipy.distributions.distribute_models import SD1WatsonDistributed

class DIPYModel(ABC):
    
    @abstractmethod
    def fit(data, mask):
        pass


class DMIPYModel(ABC):

    @abstractmethod
    def fit(scheme, data, mask):
        pass


class FreeWaterTensorModel(DIPYModel): 
    
    def __init__(self, gradient_table):
        self.gradient_table = gradient_table
    
    def fit(self, data, mask):
        self.model = fwdti.FreeWaterTensorModel(self.gradient_table)
        self.f = self.model.fit(data, mask=mask)
        self.FA = self.f.fa
        self.MD = self.f.md
        
        return self


class NODDIModel(DMIPYModel):

    def __init__(self):
        self.stick = cylinder_models.C1Stick()
        self.ball = gaussian_models.G1Ball()
        self.zeppelin = gaussian_models.G2Zeppelin()
    
    def _set_watson_parameters(self, bundle):
        bundle.set_tortuous_parameter('G2Zeppelin_1_lambda_perp', 'C1Stick_1_lambda_par', 'partial_volume_0')
        bundle.set_equal_parameter('G2Zeppelin_1_lambda_par', 'C1Stick_1_lambda_par')
        bundle.set_fixed_parameter('G2Zeppelin_1_lambda_par', 1.7e-9)

        return bundle
 
    def _set_model_parameters(self, model):
        model.set_fixed_parameter('G1Ball_1_lambda_iso', 3e-9)

        return model
   
    def _build_watson_dispersed_model(self):
        watson_dispersed_bundle = SD1WatsonDistributed(models=[self.stick, self.zeppelin])

        return self._set_watson_parameters(watson_dispersed_bundle)	

    def _build_model(self):
        watson_dispersed_bundle = self._build_watson_dispersed_model()
        model = MultiCompartmentModel(models=[self.ball, watson_dispersed_bundle])
        
        return self._set_model_parameters(model)

    def fit(self, scheme, data, mask):
        
        model = self._build_model()
        fitted_model = model.fit(
            scheme, data, mask=data[..., 0]>0)
        
        return fitted_model



     
