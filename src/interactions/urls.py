from django.urls import path
from .views import (
    SubscriptionListCreateView, SubscriptionDestroyView,
    PlaylistListCreateView, PlaylistRetrieveUpdateDestroyView,
    CommentListCreateView, CommentDestroyView
)

urlpatterns = [
    # Subscriptions
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<str:id>/', SubscriptionDestroyView.as_view(), name='subscription-destroy'),

    # Playlists
    path('playlists/', PlaylistListCreateView.as_view(), name='playlist-list-create'),
    path('playlists/<str:id>/', PlaylistRetrieveUpdateDestroyView.as_view(), name='playlist-detail'),

    # Comments
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<str:id>/', CommentDestroyView.as_view(), name='comment-destroy'),
]
