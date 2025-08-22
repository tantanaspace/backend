from rest_framework.generics import ListAPIView
from apps.common.models import Region
from apps.api.shared.v1.common.Options.RegionOptionList.serializers import RegionOptionListSerializer
from apps.api.shared.v1.common.Options.RegionOptionList.filters import RegionOptionListFilter

class RegionOptionListAPIView(ListAPIView):
    serializer_class = RegionOptionListSerializer
    queryset = Region.objects.all()
    filterset_class = RegionOptionListFilter
    search_fields = ('name',)
    
__all__ = [
    'RegionOptionListAPIView',
]