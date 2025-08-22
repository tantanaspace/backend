from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from apps.common.models import GlobalSettings

from apps.api.shared.v1.common.ConfigDetail.serializers import ConfigDetailSerializer

class ConfigDetailAPIView(RetrieveAPIView):
    serializer_class = ConfigDetailSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return GlobalSettings.get_solo()

__all__ = [
    'ConfigDetailAPIView'
]
