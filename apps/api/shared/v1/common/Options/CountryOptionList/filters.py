from django_filters import rest_framework as filters
from apps.common.models import Country

class CountryOptionListFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    pk = filters.NumberFilter(field_name='id', lookup_expr='exact')
    alpha_2 = filters.CharFilter(field_name='alpha_2', lookup_expr='exact')
    alpha_3 = filters.CharFilter(field_name='alpha_3', lookup_expr='exact')
    numeric = filters.CharFilter(field_name='numeric', lookup_expr='exact')
    
    class Meta:
        model = Country
        fields = (
            'name',
            'alpha_2',
            'alpha_3',
            'numeric',
            'pk',
        )