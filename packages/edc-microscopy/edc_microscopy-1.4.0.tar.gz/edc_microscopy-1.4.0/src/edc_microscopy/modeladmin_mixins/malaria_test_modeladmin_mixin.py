from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.fieldset import crf_status_fieldset


class MalariaTestModelAdminMixin:
    form = None

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_visit",
                    "report_datetime",
                    "performed",
                    "diagnostic_type",
                    "not_performed_reason",
                    "result",
                )
            },
        ),
        crf_status_fieldset,
        audit_fieldset_tuple,
    )

    radio_fields = {  # noqa: RUF012
        "performed": admin.VERTICAL,
        "diagnostic_type": admin.VERTICAL,
        "result": admin.VERTICAL,
    }
