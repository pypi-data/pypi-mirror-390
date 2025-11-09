from edc_auth.site_auths import site_auths

from .auth_objects import EDC_MICROSCOPY, EDC_MICROSCOPY_SUPER, EDC_MICROSCOPY_VIEW, codenames

site_auths.add_group(*codenames, name=EDC_MICROSCOPY_VIEW, view_only=True)
site_auths.add_group(*codenames, name=EDC_MICROSCOPY, no_delete=True)
site_auths.add_group(*codenames, name=EDC_MICROSCOPY_SUPER)
