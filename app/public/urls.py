from django.urls import path
from .views import PublicView, PublicSegmentListView, PublicSegmentDetailView

urlpatterns = [
    path('', PublicView.as_view(), name='public'),
    path('videos', PublicSegmentListView.as_view(), name='public-segments'),
    path('videos/<slug:slug>', PublicSegmentDetailView.as_view(), name='public-segment'),
]