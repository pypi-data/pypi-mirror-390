from clinicedc_constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator


class MalariaTestFormValidator(CrfFormValidator):
    def clean(self):
        self.applicable_if(YES, field="performed", field_applicable="diagnostic_type")

        self.required_if(NO, field="performed", field_required="not_performed_reason")

        self.applicable_if(YES, field="performed", field_applicable="result")
