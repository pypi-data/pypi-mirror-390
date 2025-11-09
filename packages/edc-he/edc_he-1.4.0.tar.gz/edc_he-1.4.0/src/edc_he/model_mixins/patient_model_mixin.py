from clinicedc_constants import QUESTION_RETIRED
from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _
from edc_model_fields.fields import OtherCharField

from ..choices import EMPLOYMENT_STATUS_CHOICES, MARITAL_CHOICES


class PatientModelMixin(models.Model):
    pat_religion = models.ForeignKey(
        "edc_he.religions",
        verbose_name=_("How would you describe your religious orientation?"),
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    pat_religion_other = OtherCharField(
        verbose_name=_("If OTHER religious orientation, specify ..."),
    )

    pat_ethnicity = models.ForeignKey(
        "edc_he.ethnicities",
        verbose_name=_("What is your ethnic background?"),
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    pat_ethnicity_other = OtherCharField(
        verbose_name=_("If OTHER ethnic background, specify ..."),
    )

    pat_education = models.ForeignKey(
        "edc_he.educationtype",
        verbose_name=_("Highest level of education completed?"),
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    pat_education_other = OtherCharField(
        verbose_name=_("If OTHER level of education, specify ..."),
    )

    pat_employment_status = models.CharField(
        verbose_name=_("What is your employment status?"),
        max_length=25,
        choices=EMPLOYMENT_STATUS_CHOICES,
    )

    pat_employment_type = models.ForeignKey(
        "edc_he.employmenttype",
        verbose_name=_("What is your type of employment?"),
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    pat_employment_type_other = OtherCharField(
        verbose_name=_("If OTHER type of employment, specify ..."),
        max_length=100,
    )

    pat_marital_status = models.CharField(
        verbose_name=_("What is your marital status?"),
        max_length=25,
        choices=MARITAL_CHOICES,
    )
    pat_marital_status_other = OtherCharField(
        verbose_name=_("If OTHER marital status, specify ..."),
    )

    pat_insurance = models.ManyToManyField(
        "edc_he.insurancetypes",
        verbose_name=_("What is your health insurance status?"),
        related_name="+",
    )

    pat_insurance_other = OtherCharField(
        verbose_name=_("If OTHER health insurance status, specify ..."),
    )

    # not used
    pat_ethnicity_old = models.CharField(
        verbose_name=_("What is your ethnic background?"),
        max_length=25,
        default=QUESTION_RETIRED,
        editable=False,
    )

    # not used
    pat_employment_type_old = models.CharField(
        verbose_name=_("What is your type of employment?"),
        max_length=25,
        default=QUESTION_RETIRED,
        editable=False,
    )

    # not used
    pat_education_old = models.CharField(
        verbose_name=_("Highest level of education completed?"),
        max_length=25,
        default=QUESTION_RETIRED,
        editable=False,
    )

    # not used
    pat_religion_old = models.CharField(
        verbose_name=_("How would you describe your religious orientation?"),
        max_length=25,
        default=QUESTION_RETIRED,
        editable=False,
    )

    class Meta:
        abstract = True
