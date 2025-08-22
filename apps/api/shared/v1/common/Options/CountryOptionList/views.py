from rest_framework.generics import ListAPIView

from apps.common.models import Country
from apps.api.shared.v1.common.Options.CountryOptionList.serializers import CountryOptionListSerializer
from apps.api.shared.v1.common.Options.CountryOptionList.filters import CountryOptionListFilter

class CountryOptionListAPIView(ListAPIView):
    serializer_class = CountryOptionListSerializer
    queryset = Country.objects.all()
    filterset_class = CountryOptionListFilter
    search_fields = ('name', 'alpha_2', 'alpha_3', 'numeric')
    
__all__ = [
    'CountryOptionListAPIView',
]