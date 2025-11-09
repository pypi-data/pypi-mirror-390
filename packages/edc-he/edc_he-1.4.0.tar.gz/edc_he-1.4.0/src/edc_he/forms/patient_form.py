from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin, CrfSingletonModelFormMixin

from ..form_validators import HealthEconomicsPatientFormValidator
from ..models import HealthEconomicsPatient
from .modelform_mixins import HealthEconomicsModelFormMixin


class HealthEconomicsPatientForm(
    CrfSingletonModelFormMixin,
    HealthEconomicsModelFormMixin,
    CrfModelFormMixin,
    forms.ModelForm,
):
    form_validator_cls = HealthEconomicsPatientFormValidator

    class Meta:
        model = HealthEconomicsPatient
        fields = "__all__"
