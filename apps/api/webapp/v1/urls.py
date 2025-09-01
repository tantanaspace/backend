from django.urls import path

from apps.api.webapp.v1.visits import (
        VisitListAPIView,
        VisitDetailAPIView,
        VisitCancelAPIView,
        VisitFinishAPIView,
        BookCreateAPIView
    )

app_name = 'webapp_v1'

urlpatterns = [
    path('visits/', VisitListAPIView.as_view(), name='visit-list'),
    path('visits/<int:visit_id>/', VisitDetailAPIView.as_view(), name='visit-detail'),
    path('visits/<int:visit_id>/cancel/', VisitCancelAPIView.as_view(), name='visit-cancel'),
    path('visits/<int:visit_id>/finish/', VisitFinishAPIView.as_view(), name='visit-finish'),
    path('visits/book/', BookCreateAPIView.as_view(), name='book-create'),
]
