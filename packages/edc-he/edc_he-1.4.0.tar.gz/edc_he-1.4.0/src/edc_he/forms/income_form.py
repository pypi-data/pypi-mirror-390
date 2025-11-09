from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin, CrfSingletonModelFormMixin

from ..form_validators import HealthEconomicsIncomeFormValidator
from ..models import HealthEconomicsIncome
from .modelform_mixins import HealthEconomicsModelFormMixin


class HealthEconomicsIncomeForm(
    CrfSingletonModelFormMixin,
    HealthEconomicsModelFormMixin,
    CrfModelFormMixin,
    forms.ModelForm,
):
    form_validator_cls = HealthEconomicsIncomeFormValidator

    class Meta:
        model = HealthEconomicsIncome
        fields = "__all__"
        help_texts = {"external_remit_value": ""}  # noqa: RUF012
