from clinicedc_constants import YES
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_form_validators import FormValidator


class HealthEconomicsPropertyFormValidator(
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        self.required_if(YES, field="land_owner", field_required="land_value")
        self.required_if(YES, field="land_owner", field_required="land_surface_area")
        self.applicable_if_true(
            self.cleaned_data.get("land_surface_area"),
            field_applicable="land_surface_area_units",
        )
        self.required_if(YES, field="land_additional", field_required="land_additional_value")
