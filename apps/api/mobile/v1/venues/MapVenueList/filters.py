from django.db.models import F, Func, FloatField
from django.db.models.expressions import ExpressionWrapper
from django_filters import rest_framework as filters

from apps.api.mobile.v1.venues.VenueList.filters import VenueListFilter
from apps.venues.models import Venue


class Radians(Func):
    function = 'RADIANS'
    output_field = FloatField()


class MapVenueListFilter(VenueListFilter):
    radius = filters.NumberFilter(method='filter_by_lat_lon_radius')

    class Meta(VenueListFilter.Meta):
        model = Venue
        fields = VenueListFilter.Meta.fields + ("radius",)

    def filter_by_lat_lon_radius(self, queryset, name, value):
        lat = self.data.get('user_latitude')
        lon = self.data.get('user_longitude')
        radius = self.data.get('radius')

        print(lat, lon, radius)

        if lat and lon and radius:
            try:
                lat = float(lat)
                lon = float(lon)
                radius = float(radius)
            except ValueError:
                return queryset

            earth_radius = 6371  # km

            # Haversine formula
            dlon = Radians(F('longitude') - lon)
            dlat = Radians(F('latitude') - lat)

            a = (
                Func(dlat / 2, function='SIN') ** 2 +
                Func(Radians(lat), function='COS') *
                Func(Radians(F('latitude')), function='COS') *
                Func(dlon / 2, function='SIN') ** 2
            )

            distance_expr = ExpressionWrapper(
                earth_radius * 2 * Func(
                    Func(a, function='SQRT'),
                    Func(1 - a, function='SQRT'),
                    function='ATAN2'
                ),
                output_field=FloatField()
            )

            queryset = queryset.annotate(distance=distance_expr).filter(distance__lte=radius)

        return queryset