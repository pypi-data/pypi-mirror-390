from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings

if TYPE_CHECKING:
    from .models import (
        HealthEconomicsAssets,
        HealthEconomicsHouseholdHead,
        HealthEconomicsIncome,
        HealthEconomicsPatient,
        HealthEconomicsProperty,
    )


def get_household_head_model() -> str:
    return getattr(
        settings, "EDC_HE_HOUSEHOLDHEAD_MODEL", "edc_he.healtheconomicshouseholdhead"
    )


def get_household_head_model_cls() -> type[HealthEconomicsHouseholdHead]:
    return django_apps.get_model(get_household_head_model())


def get_patient_model() -> str:
    return getattr(settings, "EDC_HE_PATIENT_MODEL", "edc_he.healtheconomicspatient")


def get_patient_model_cls() -> type[HealthEconomicsPatient]:
    return django_apps.get_model(get_patient_model())


def get_property_model() -> str:
    return getattr(settings, "EDC_HE_PROPERTY_MODEL", "edc_he.healtheconomicsproperty")


def get_property_model_cls() -> type[HealthEconomicsProperty]:
    return django_apps.get_model(get_property_model())


def get_income_model() -> str:
    return getattr(settings, "EDC_HE_INCOME_MODEL", "edc_he.healtheconomicsincome")


def get_income_model_cls() -> type[HealthEconomicsIncome]:
    return django_apps.get_model(get_income_model())


def get_assets_model() -> str:
    return getattr(settings, "EDC_HE_ASSETS_MODEL", "edc_he.healtheconomicsassets")


def get_assets_model_cls() -> type[HealthEconomicsAssets]:
    return django_apps.get_model(get_assets_model())
