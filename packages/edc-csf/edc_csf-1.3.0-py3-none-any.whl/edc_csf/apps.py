from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_csf"
    verbose_name = "Edc CSF"
    has_exportable_data = True
    include_in_administration_section = True
