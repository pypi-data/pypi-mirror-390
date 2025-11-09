from __future__ import annotations

from clinicedc_constants import YES
from django.core.exceptions import ObjectDoesNotExist

from ..utils import (
    get_assets_model_cls,
    get_household_head_model_cls,
    get_income_model_cls,
    get_patient_model_cls,
    get_property_model_cls,
)


class Predicates:
    def is_required_by_date(self, visit, **kwargs) -> bool:  # noqa: ARG002
        return True

    @staticmethod
    def get_household_head(visit):
        try:
            obj = get_household_head_model_cls().objects.get(
                subject_visit__subject_identifier=visit.subject_identifier
            )
        except ObjectDoesNotExist:
            obj = None
        return obj

    def household_head_required(self, visit, **kwargs) -> bool:  # noqa: ARG002
        return (
            self.is_required_by_date(visit)
            and not get_household_head_model_cls()
            .objects.filter(subject_visit__subject_identifier=visit.subject_identifier)
            .exists()
        )

    def patient_required(self, visit, **kwargs) -> bool:  # noqa: ARG002
        required = False
        hoh_obj = self.get_household_head(visit)
        if hoh_obj and (
            not get_patient_model_cls()
            .objects.filter(subject_visit__subject_identifier=visit.subject_identifier)
            .exists()
        ):
            required = hoh_obj.hoh == YES and self.is_required_by_date(visit)

        return required

    def assets_required(self, visit, **kwargs) -> bool:  # noqa: ARG002
        return (
            self.is_required_by_date(visit)
            and not get_assets_model_cls()
            .objects.filter(subject_visit__subject_identifier=visit.subject_identifier)
            .exists()
        )

    def property_required(self, visit, **kwargs) -> bool:  # noqa: ARG002
        return (
            self.is_required_by_date(visit)
            and not get_property_model_cls()
            .objects.filter(subject_visit__subject_identifier=visit.subject_identifier)
            .exists()
        )

    def income_required(self, visit, **kwargs) -> bool:  # noqa: ARG002
        return (
            self.is_required_by_date(visit)
            and not get_income_model_cls()
            .objects.filter(subject_visit__subject_identifier=visit.subject_identifier)
            .exists()
        )
