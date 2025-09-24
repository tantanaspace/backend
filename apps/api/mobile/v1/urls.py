from django.urls import path

from apps.api.mobile.v1.common import (
    StoryDetailAPIView,
    StoryListAPIView,
    UserSearchHistoryCreateAPIView,
    UserSearchHistoryDeleteAPIView,
    UserSearchHistoryListAPIView,
    UserVenueFavouriteListAPIView,
    UserVenueFavouriteToggleAPIView,
)
from apps.api.mobile.v1.payments import (
    TransactionCreateAPIView,
    TransactionDetailAPIView,
)
from apps.api.mobile.v1.venues import (
    MapVenueListAPIView,
    RecommendedVenuesAPIView,
    VenueCategoryListAPIView,
    VenueDetailAPIView,
    VenueListAPIView,
    VenueReviewCreateAPIView,
    VenueReviewListAPIView,
)

app_name = "mobile_v1"

urlpatterns = [
    # venues
    path("venues/", VenueListAPIView.as_view(), name="venue-list"),
    path(
        "venue-categories/",
        VenueCategoryListAPIView.as_view(),
        name="venue-category-list",
    ),
    path(
        "recommended-venues/",
        RecommendedVenuesAPIView.as_view(),
        name="recommended-venues",
    ),
    path("map-venues/", MapVenueListAPIView.as_view(), name="map-venues"),
    path("venue/<int:venue_id>/", VenueDetailAPIView.as_view(), name="venue-detail"),
    path(
        "venue/<int:venue_id>/reviews/",
        VenueReviewListAPIView.as_view(),
        name="venue-review-list",
    ),
    path(
        "venue-review-create/",
        VenueReviewCreateAPIView.as_view(),
        name="venue-review-create",
    ),
    # common
    path(
        "search-histories/",
        UserSearchHistoryListAPIView.as_view(),
        name="search-history",
    ),
    path(
        "search-history-create/",
        UserSearchHistoryCreateAPIView.as_view(),
        name="search-history-create",
    ),
    path(
        "search-history/<int:pk>/delete/",
        UserSearchHistoryDeleteAPIView.as_view(),
        name="search-history-delete",
    ),
    path(
        "favourite-venue-toggle/",
        UserVenueFavouriteToggleAPIView.as_view(),
        name="favourite-venue-toggle",
    ),
    path(
        "favourite-venues/",
        UserVenueFavouriteListAPIView.as_view(),
        name="favourite-venue-list",
    ),
    path("stories/", StoryListAPIView.as_view(), name="story-list"),
    path(
        "story/<int:story_group_id>/", StoryDetailAPIView.as_view(), name="story-detail"
    ),
    # payments
    path(
        "transaction-create/",
        TransactionCreateAPIView.as_view(),
        name="transaction-create",
    ),
    path(
        "transaction-detail/<int:pk>/",
        TransactionDetailAPIView.as_view(),
        name="transaction-detail",
    ),
]
