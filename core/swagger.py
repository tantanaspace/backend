from django.urls import re_path, path, include

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import permissions

class AppNameTagAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        

                        
        view_tags = getattr(self.view, 'swagger_tags', None)
        if view_tags:
            return view_tags

        module_path = self.view.__module__
        
        # example path: apps.api.mobile.v1.logs.views
        try:
            parts = module_path.split('.')
            api_index = parts.index('api')
            
            # app_name always after: apps.api.<interface>.v1.<app>
            # 0=apps, 1=api, 2=interface, 3=v1, 4=app_name
            app_name = parts[api_index + 3]  
        except (ValueError, IndexError):
            app_name = "other"

        return [app_name]



class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        if request and request.is_secure():
            schema.schemes = ["https", "http"]
        else:
            schema.schemes = ["http", "https"]

        return schema
    

swagger_title = "Tantana"
swagger_description = "Tantana swagger"
swagger_terms_of_service = "https://www.google.com/policies/terms/"
swagger_contact_email = "nuftillayevjavohir@gmail.com"
swagger_license_name = "BSD License"


mobile_schema_view_v1 = get_schema_view(
    openapi.Info(
        title=swagger_title,
        default_version="v1",
        description=swagger_description,
        terms_of_service=swagger_terms_of_service,
        contact=openapi.Contact(email=swagger_contact_email),
        license=openapi.License(name=swagger_license_name),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=[permissions.AllowAny, ],  # todo: change to permissions.IsAuthenticated
    patterns=[
        path("api/mobile/v1/", include("apps.api.mobile.v1.urls", namespace='mobile_v1'))
    ]
)

mobile_swagger_urlpatterns_v1 = [
    re_path(
        r"^api/mobile/v1/docs(?P<format>\.json|\.yaml)$",
        mobile_schema_view_v1.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^api/mobile/v1/docs/$",
        mobile_schema_view_v1.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api/mobile/v1/redoc/$",
        mobile_schema_view_v1.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]



shared_schema_view_v1 = get_schema_view(
    openapi.Info(
        title=swagger_title,
        default_version="v1",
        description=swagger_description,
        terms_of_service=swagger_terms_of_service,
        contact=openapi.Contact(email=swagger_contact_email),
        license=openapi.License(name=swagger_license_name),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=[permissions.AllowAny, ],  # todo: change to permissions.IsAuthenticated
    patterns=[
        path("api/v1/", include("apps.api.shared.v1.urls", namespace='shared_v1'))
    ]
)

shared_swagger_urlpatterns_v1 = [
    re_path(
        r"^api/v1/docs(?P<format>\.json|\.yaml)$",
        shared_schema_view_v1.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^api/v1/docs/$",
        shared_schema_view_v1.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api/v1/redoc/$",
        shared_schema_view_v1.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]



swagger_urlpatterns = (
    mobile_swagger_urlpatterns_v1 
    + shared_swagger_urlpatterns_v1
)