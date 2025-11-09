from edc_metadata import NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_rules import CrfRule, CrfRuleGroup


class HealthEconomicsRuleGroup(CrfRuleGroup):
    hoh = CrfRule(
        predicate="household_head_required",
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["healtheconomicshouseholdhead"],
    )

    patient = CrfRule(
        predicate="patient_required",
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["healtheconomicspatient"],
    )

    assets = CrfRule(
        predicate="assets_required",
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["healtheconomicsassets"],
    )

    property = CrfRule(
        predicate="property_required",
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["healtheconomicsproperty"],
    )

    income = CrfRule(
        predicate="income_required",
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["healtheconomicsincome"],
    )

    class Meta:
        abstract = True
