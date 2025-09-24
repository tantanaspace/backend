from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.api.shared.v1.common.Options.FacilityList.serializers import (
    FacilityListSerializer,
)
from apps.common.models import Facility


class FacilityListAPIView(ListAPIView):
    queryset = Facility.objects.all()
    serializer_class = FacilityListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ("id", "title", "quick_access")
    search_fields = ("title",)
    ordering = ("id", "title")


__all__ = [
    "FacilityListAPIView",
]
