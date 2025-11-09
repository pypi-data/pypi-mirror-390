from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_microbiology"
    verbose_name = "Edc Microbiology"
    has_exportable_data = True
    include_in_administration_section = True
