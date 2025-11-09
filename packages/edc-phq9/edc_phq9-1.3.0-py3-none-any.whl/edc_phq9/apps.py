from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_phq9"
    verbose_name = "Edc PHQ9"
    has_exportable_data = True
    include_in_administration_section = True
