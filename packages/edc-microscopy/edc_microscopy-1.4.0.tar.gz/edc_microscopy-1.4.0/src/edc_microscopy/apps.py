from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_microscopy"
    has_exportable_data = True
    include_in_administration_section = True
