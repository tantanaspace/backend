from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("mobile/v1/", include("apps.api.mobile.v1.urls", namespace="mobile_v1")),
    path("webapp/v1/", include("apps.api.webapp.v1.urls", namespace="webapp_v1")),
    path("v1/", include("apps.api.shared.v1.urls", namespace="shared_v1")),
]
