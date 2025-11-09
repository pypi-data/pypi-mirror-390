from clinicedc_constants import YES
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_form_validators import FormValidator

from ..constants import (
    ALL_WINDOWS_SCREENED,
    FAMILY_OWNED,
    JOINT_OWNED,
    NON_FAMILY_OWNED,
    OWNER,
    SOME_WINDOWS_SCREENED,
)


class HealthEconomicsAssetsFormValidator(
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        self.applicable_if(
            OWNER,
            FAMILY_OWNED,
            NON_FAMILY_OWNED,
            JOINT_OWNED,
            field="residence_ownership",
            field_applicable="dwelling_value_known",
        )
        self.required_if(YES, field="dwelling_value_known", field_required="dwelling_value")
        self.validate_other_specify(field="water_source")
        self.validate_other_specify(field="toilet")
        self.validate_other_specify(field="roof_material")
        self.validate_other_specify(field="external_wall_material")
        self.validate_other_specify(field="external_window_material")
        self.applicable_if(
            ALL_WINDOWS_SCREENED,
            SOME_WINDOWS_SCREENED,
            field="window_screens",
            field_applicable="window_screen_type",
        )
        self.validate_other_specify(field="floor_material")
        self.validate_other_specify(field="light_source")
        self.validate_other_specify(field="cooking_fuel")
