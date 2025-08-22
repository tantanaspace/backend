from rest_framework import serializers
from django.contrib.gis.geos import Point


class PointFieldSerializer(serializers.Field):
    """
    Custom serializer field for handling PointField.
    Converts between PointField and [longitude, latitude] list.
    """
    def to_representation(self, value):
        """
        Convert PointField to [longitude, latitude] list
        """
        if value is None:
            return None
        return [value.x, value.y]

    def to_internal_value(self, data):
        """
        Convert [longitude, latitude] list to PointField
        """
        if data is None:
            return None
            
        if not isinstance(data, list):
            raise serializers.ValidationError(
                "Coordinates must be a list of [longitude, latitude]"
            )
            
        if len(data) != 2:
            raise serializers.ValidationError(
                "Coordinates must contain exactly 2 values: [longitude, latitude]"
            )
            
        try:
            longitude, latitude = data
            return Point(longitude, latitude, srid=4326)
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                "Invalid coordinates format. Must be [longitude, latitude]"
            )
