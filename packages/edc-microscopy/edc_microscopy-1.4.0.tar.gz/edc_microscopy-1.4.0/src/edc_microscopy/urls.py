from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_microscopy_admin

app_name = "edc_microscopy"

urlpatterns = [
    path("admin/", edc_microscopy_admin.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
