from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_he_admin = EdcAdminSite(name="edc_he_admin", app_label=AppConfig.name)
