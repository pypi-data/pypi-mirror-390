from clinicedc_constants import NOT_APPLICABLE
from django.db import models
from edc_constants.choices import PRESENT_ABSENT_NA, YES_NO

from ..choices import MALARIA_TEST_CHOICES


class MalariaTestModelMixin(models.Model):
    performed = models.CharField(
        verbose_name="Was the malaria test performed?",
        max_length=15,
        choices=YES_NO,
    )

    not_performed_reason = models.CharField(
        verbose_name="If NO, provide reason", max_length=150, default="", blank=True
    )

    diagnostic_type = models.CharField(
        verbose_name="Diagnostic test used",
        max_length=15,
        choices=MALARIA_TEST_CHOICES,
        default=NOT_APPLICABLE,
    )

    result = models.CharField(
        verbose_name="Result",
        max_length=25,
        choices=PRESENT_ABSENT_NA,
        default=NOT_APPLICABLE,
    )

    class Meta:
        abstract = True
        verbose_name = "Malaria Test"
