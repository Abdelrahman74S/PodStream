from django.urls import path
from .views import (
    CategoryListCreateView, CategoryRetrieveUpdateDestroyView,
    TagsListCreateView, TagsRetrieveUpdateDestroyView,
    PodcastListCreateView, PodcastRetrieveUpdateDestroyView,
    EpisodeListCreateView, EpisodeRetrieveUpdateDestroyView,
    PodcastSemanticSearch, EpisodeSemanticSearch
)

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<str:id>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    
    # Tags endpoints
    path('tags/', TagsListCreateView.as_view(), name='tags-list-create'),
    path('tags/<str:id>/', TagsRetrieveUpdateDestroyView.as_view(), name='tags-detail'),
    
    # Podcast endpoints
    path('podcasts/', PodcastListCreateView.as_view(), name='podcast-list-create'),
    path('podcasts/<str:id>/', PodcastRetrieveUpdateDestroyView.as_view(), name='podcast-detail'),
    path('podcasts/search/', PodcastSemanticSearch.as_view(), name='podcast-semantic-search'),

    # Episode endpoints
    path('episodes/', EpisodeListCreateView.as_view(), name='episode-list-create'),
    path('episodes/<str:id>/', EpisodeRetrieveUpdateDestroyView.as_view(), name='episode-detail'),
    path('episodes/search/', EpisodeSemanticSearch.as_view(), name='episode-semantic-search')
]
