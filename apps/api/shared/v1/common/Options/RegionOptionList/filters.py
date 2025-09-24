from django_filters import rest_framework as filters

from apps.common.models import Region


class RegionOptionListFilter(filters.FilterSet):
    country = filters.NumberFilter(field_name="country", lookup_expr="exact")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    pk = filters.NumberFilter(field_name="id", lookup_expr="exact")

    class Meta:
        model = Region
        fields = (
            "country",
            "name",
            "pk",
        )
