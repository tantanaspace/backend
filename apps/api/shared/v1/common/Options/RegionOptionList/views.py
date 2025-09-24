from rest_framework.generics import ListAPIView

from apps.api.shared.v1.common.Options.RegionOptionList.filters import (
    RegionOptionListFilter,
)
from apps.api.shared.v1.common.Options.RegionOptionList.serializers import (
    RegionOptionListSerializer,
)
from apps.common.models import Region


class RegionOptionListAPIView(ListAPIView):
    serializer_class = RegionOptionListSerializer
    queryset = Region.objects.all()
    filterset_class = RegionOptionListFilter
    search_fields = ("name",)


__all__ = [
    "RegionOptionListAPIView",
]
