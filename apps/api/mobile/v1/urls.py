from django.urls import path

from apps.api.mobile.v1.common import (
    UserSearchHistoryListAPIView,
    UserSearchHistoryCreateAPIView,
    UserSearchHistoryDeleteAPIView,
    UserVenueFavouriteToggleAPIView,
    UserVenueFavouriteListAPIView,
)

from apps.api.mobile.v1.venues import (
        VenueListAPIView, 
        VenueCategoryListAPIView,
        VenueDetailAPIView,
        VenueReviewListAPIView,
        VenueReviewCreateAPIView,
    )

app_name = 'mobile_v1'

urlpatterns = [    
    # venues
    path('venues/', VenueListAPIView.as_view(), name='venue-list'),
    path('venue-categories/', VenueCategoryListAPIView.as_view(), name='venue-category-list'),
    path('venue/<int:venue_id>/', VenueDetailAPIView.as_view(), name='venue-detail'),
    path('venue/<int:venue_id>/reviews/', VenueReviewListAPIView.as_view(), name='venue-review-list'),
    path('venue-review-create/', VenueReviewCreateAPIView.as_view(), name='venue-review-create'),

    # common
    path('search-histories/', UserSearchHistoryListAPIView.as_view(), name='search-history'),
    path('search-history-create/', UserSearchHistoryCreateAPIView.as_view(), name='search-history-create'),
    path('search-history/<int:pk>/delete/', UserSearchHistoryDeleteAPIView.as_view(), name='search-history-delete'),

    # User venue favourite
    path('favourite-venue-toggle/', UserVenueFavouriteToggleAPIView.as_view(), name='favourite-venue-toggle'),
    path('favourite-venues/', UserVenueFavouriteListAPIView.as_view(), name='favourite-venue-list'),
]