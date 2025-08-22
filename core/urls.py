from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.swagger import swagger_urlpatterns

# class LoginForm(AuthenticationForm):
#     captcha = fields.ReCaptchaField()
#
#     def clean(self):
#         captcha = self.cleaned_data.get("captcha")
#         if not captcha:
#             return
#         return super().clean()


# admin.site.login_form = LoginForm
# admin.site.login_template = "login.html"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls", namespace='api')),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    

if settings.DEBUG and settings.DEBUG_TOOLBAR_ENABLED:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]