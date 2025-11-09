from __future__ import annotations

from decimal import Decimal

from .constants import ACRES, DECIMALS, HECTARES, SQ_FEET, SQ_METERS


class InvalidAreaUnitsError(Exception):
    pass


def convert_to_sq_meters(area: int | Decimal | float, area_units: str) -> Decimal:
    """Returns the area converted to square meters.

    Raises InvalidAreaUnitsError if `area_units` value not recognised.
    """
    if area_units == SQ_METERS:
        return Decimal(str(area))
    if area_units == ACRES:
        return acres_to_sq_meters(area)
    if area_units == DECIMALS:
        return decimals_to_sq_meters(area)
    if area_units == HECTARES:
        return hectares_to_sq_meters(area)
    if area_units == SQ_FEET:
        return sq_feet_to_sq_meters(area)
    raise InvalidAreaUnitsError(
        "Invalid. Area units not currently supported. "
        "Either modify argument or define a conversion to square meters. "
        f"Got area_units='{area_units}'"
    )


def acres_to_sq_meters(area: int | Decimal | float) -> Decimal:
    # International foot metric equivalent (exact): 1 acre = 4046.8564224 m2

    # Conversion source:
    #   - https://www.nist.gov/pml/us-surveyfoot/revised-unit-conversion-factors

    # NOTE:
    # "Beginning on January 1, 2023, the U.S. survey foot should be avoided
    # [...] and has been superseded by the international foot definition
    # (i.e., 1 foot = 0.3048 meter exactly)"
    # - https://www.nist.gov/pml/us-surveyfoot
    return Decimal(str(area)) * Decimal("4046.8564224")


def hectares_to_sq_meters(area: int | Decimal | float) -> Decimal:
    # Conversion sources:
    # - https://www.nist.gov/pml/owm/metric-si/si-units-area
    # - https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9#AREA  # noqa
    return Decimal(str(area)) * Decimal("1E04")


def decimals_to_sq_meters(area: int | Decimal | float) -> Decimal:
    return acres_to_sq_meters(area) / Decimal(100)


def sq_feet_to_sq_meters(area: int | Decimal | float) -> Decimal:
    # Conversion sources:
    # - https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9#AREA  # noqa
    return Decimal(str(area)) * Decimal("9.290304E-02")
