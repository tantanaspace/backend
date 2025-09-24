from rest_framework import serializers

from apps.venues.models import Company, Venue


class MapVenueListCompanySerializer(serializers.ModelSerializer):
    logo_small = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "logo_small",
        )

    def get_logo_small(self, obj):
        request = self.context.get("request")
        if obj.logo:
            return request.build_absolute_uri(obj.logo.thumbnail["100x100"].url)
        return None


class MapVenueListSerializer(serializers.ModelSerializer):
    company = MapVenueListCompanySerializer()
    distance = serializers.FloatField(allow_null=True)

    class Meta:
        model = Venue
        fields = (
            "id",
            "name",
            "company",
            "longitude",
            "latitude",
            "rating",
            "distance",
        )
