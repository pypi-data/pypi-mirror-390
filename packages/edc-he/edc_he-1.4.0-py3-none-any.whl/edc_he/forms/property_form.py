from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin, CrfSingletonModelFormMixin

from ..form_validators import HealthEconomicsPropertyFormValidator
from ..models import HealthEconomicsProperty
from .modelform_mixins import HealthEconomicsModelFormMixin


class HealthEconomicsPropertyForm(
    CrfSingletonModelFormMixin,
    HealthEconomicsModelFormMixin,
    CrfModelFormMixin,
    forms.ModelForm,
):
    form_validator_cls = HealthEconomicsPropertyFormValidator

    class Meta:
        model = HealthEconomicsProperty
        fields = "__all__"
