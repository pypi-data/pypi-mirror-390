from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class HouseholdModelMixin(models.Model):
    hh_count = models.IntegerField(
        verbose_name=_("What is the total number of people who live in your household?"),
        validators=[MinValueValidator(1), MaxValueValidator(25)],
        help_text=_("Persons"),
    )

    hh_minors_count = models.IntegerField(
        verbose_name=_(
            "What is the total number of people 14 years or under who live in your household?"
        ),
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        help_text=_("Persons"),
    )

    class Meta:
        abstract = True
