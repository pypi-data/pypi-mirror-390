from edc_auth.site_auths import site_auths

from .auth_objects import EDC_HEALTH_ECONOMICS_VIEW, codenames

site_auths.add_group(*codenames, name=EDC_HEALTH_ECONOMICS_VIEW, view_only=True)
