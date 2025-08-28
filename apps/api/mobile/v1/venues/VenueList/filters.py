from django_filters import rest_framework as filters
from django_filters.filters import DateTimeFromToRangeFilter
from django.db.models import Q
from datetime import time

from apps.venues.models import Venue, VenueWorkingHour


class WorkingHoursRangeFilter(filters.BaseInFilter):
    """
    Custom filter for working hours range
    Filters venues that are open during specified time range
    """
    
    def filter(self, qs, value):
        if not value or len(value) != 2:
            return qs
            
        start_time, end_time = value
        
        if not start_time or not end_time:
            return qs
            
        # Convert string times to time objects if needed
        if isinstance(start_time, str):
            try:
                start_time = time.fromisoformat(start_time)
            except ValueError:
                return qs
                
        if isinstance(end_time, str):
            try:
                end_time = time.fromisoformat(end_time)
            except ValueError:
                return qs
        
        # Find venues that have working hours overlapping with the specified range
        return qs.filter(
            working_hours__opening_time__lte=end_time,
            working_hours__closing_time__gte=start_time
        ).distinct()


class VenueListFilter(filters.FilterSet):
    # Multiple choice filters
    categories = filters.BaseInFilter(
        field_name='categories', 
        lookup_expr='in',
        help_text='Filter by venue categories (multiple IDs separated by comma)'
    )
    
    facilities = filters.BaseInFilter(
        field_name='facilities', 
        lookup_expr='in',
        help_text='Filter by venue facilities (multiple IDs separated by comma)'
    )
    
    tags = filters.BaseInFilter(
        field_name='tags', 
        lookup_expr='in',
        help_text='Filter by venue tags (multiple IDs separated by comma)'
    )
    
    # Working hours range filter
    working_hours_range = WorkingHoursRangeFilter(
        help_text='Filter by working hours range (format: HH:MM,HH:MM)'
    )
    
    # Working days filter
    working_days = filters.BaseInFilter(
        field_name='working_hours__weekday',
        lookup_expr='in',
        help_text='Filter by working days (mon,tue,wed,thu,fri,sat,sun)'
    )
    
    # Rating filter
    min_rating = filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        help_text='Minimum rating (0.0 - 5.0)'
    )
    
    max_rating = filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        help_text='Maximum rating (0.0 - 5.0)'
    )
        
    # Company filter
    company = filters.NumberFilter(
        field_name='company',
        lookup_expr='exact',
        help_text='Filter by company ID'
    )
        
    class Meta:
        model = Venue
        fields = (
            'categories',
            'facilities', 
            'tags',
            'working_hours_range',
            'working_days',
            'min_rating',
            'max_rating',
            'latitude',
            'longitude',
            'company',
        )