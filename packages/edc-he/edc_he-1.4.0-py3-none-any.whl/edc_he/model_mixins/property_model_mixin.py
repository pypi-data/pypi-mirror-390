from __future__ import annotations

from typing import TYPE_CHECKING

from clinicedc_constants import NOT_APPLICABLE, QUESTION_RETIRED
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from edc_constants.choices import YES_NO_DONT_KNOW_DWTA

from edc_he.calculators import convert_to_sq_meters
from edc_he.choices import LAND_AREA_UNITS

if TYPE_CHECKING:
    from decimal import Decimal


class PropertyModelMixin(models.Model):
    land_owner = models.CharField(
        verbose_name=_("Do you own any land."),
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA,
    )

    # QUESTION_RETIRED
    land_value_known = models.CharField(
        verbose_name=_("Do you know about how much is this worth in total?"),
        max_length=25,
        default=QUESTION_RETIRED,
        help_text=_("Use cash equivalent in local currency"),
    )

    land_value = models.IntegerField(
        verbose_name=_("About how much is this worth in total?"),
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        null=True,
        blank=True,
        help_text=_("Use cash equivalent in local currency"),
    )

    land_surface_area = models.DecimalField(
        verbose_name=_("Surface area"),
        decimal_places=1,
        max_digits=15,
        validators=[MinValueValidator(0.1), MaxValueValidator(999999999.9)],
        null=True,
        blank=True,
    )

    land_surface_area_units = models.CharField(
        verbose_name=_("Surface area (units)"),
        max_length=15,
        choices=LAND_AREA_UNITS,
        default=NOT_APPLICABLE,
    )

    land_additional = models.CharField(
        verbose_name=_("Do you own any other property other than your primary dwelling?"),
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA,
    )

    # QUESTION_RETIRED
    land_additional_known = models.CharField(
        verbose_name=_("Do you know about how much is this worth in total?"),
        max_length=25,
        default=QUESTION_RETIRED,
        help_text=_("Use cash equivalent in local currency"),
    )

    land_additional_value = models.IntegerField(
        verbose_name=_("About how much is this worth in total?"),
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        null=True,
        blank=True,
        help_text=_("Use cash equivalent in local currency"),
    )

    calculated_land_surface_area = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(0), MaxValueValidator(999999999.99)],
        null=True,
        blank=True,
        help_text="m2 (system calculated)",
    )

    def save(self, *args, **kwargs):
        self.calculated_land_surface_area = self.get_calculated_land_surface_area()
        super().save(*args, **kwargs)

    def get_calculated_land_surface_area(self) -> Decimal | None:
        """Returns land surface area converted to m2."""
        calculated_land_surface_area = None
        if self.land_surface_area and self.land_surface_area_units:
            calculated_land_surface_area = convert_to_sq_meters(
                area=self.land_surface_area,
                area_units=self.land_surface_area_units,
            )
        return calculated_land_surface_area

    class Meta:  # noqa: DJ012
        abstract = True
