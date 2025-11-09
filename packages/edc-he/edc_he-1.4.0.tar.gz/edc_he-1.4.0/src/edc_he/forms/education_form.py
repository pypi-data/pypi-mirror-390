from django import forms
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_form_validators import FormValidatorMixin
from edc_form_validators.form_validator import FormValidator

from edc_he.form_validators import SimpleFormValidatorMixin

from ..models import Education


class EducationFormValidator(CrfFormValidatorMixin, SimpleFormValidatorMixin, FormValidator):
    def clean(self) -> None:
        self.clean_education()


class EducationForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = EducationFormValidator

    class Meta:
        model = Education
        fields = "__all__"
