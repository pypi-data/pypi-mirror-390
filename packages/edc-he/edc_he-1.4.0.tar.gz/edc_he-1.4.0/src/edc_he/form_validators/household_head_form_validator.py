from clinicedc_constants import DONT_KNOW, NO, NONE, OTHER
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_form_validators import INVALID_ERROR, FormValidator


class HealthEconomicsHouseholdHeadFormValidator(
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        if (
            self.cleaned_data.get("hh_minors_count") is not None
            and self.cleaned_data.get("hh_count") is not None
            and self.cleaned_data.get("hh_minors_count") >= self.cleaned_data.get("hh_count")
        ):
            self.raise_validation_error(
                {
                    "hh_minors_count": (
                        f"Invalid. Expected less than {self.cleaned_data.get('hh_count')}."
                    )
                },
                INVALID_ERROR,
            )
        self.applicable_if(NO, field="hoh", field_applicable="hoh_gender")
        self.required_if(
            NO,
            field="hoh",
            field_required="hoh_age",
            field_required_evaluate_as_int=True,
        )
        self.applicable_if(NO, field="hoh", field_applicable="relationship_to_hoh")
        self.validate_other_specify(field="relationship_to_hoh")
        self.applicable_if(NO, field="hoh", field_applicable="hoh_religion")
        self.validate_other_specify(field="hoh_religion")
        self.applicable_if(NO, field="hoh", field_applicable="hoh_ethnicity")
        self.validate_other_specify(field="hoh_ethnicity")
        self.applicable_if(NO, field="hoh", field_applicable="hoh_education")
        self.validate_other_specify(field="hoh_education")
        self.applicable_if(NO, field="hoh", field_applicable="hoh_employment_status")
        self.validate_other_specify(field="hoh_employment_status")
        self.applicable_if(NO, field="hoh", field_applicable="hoh_employment_type")
        self.validate_other_specify(field="hoh_employment_type")
        self.applicable_if(NO, field="hoh", field_applicable="hoh_marital_status")
        self.validate_other_specify(field="hoh_marital_status")
        self.m2m_applicable_if(NO, field="hoh", m2m_field="hoh_insurance")
        self.m2m_single_selection_if(DONT_KNOW, NONE, m2m_field="hoh_insurance")
        self.m2m_other_specify(
            OTHER, m2m_field="hoh_insurance", field_other="hoh_insurance_other"
        )
