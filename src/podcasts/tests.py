from django.test import TestCase
from .models import Podcast, Episode , Tags , Category
from .views import (
    CategoryListCreateView, CategoryRetrieveUpdateDestroyView,
    TagsListCreateView, TagsRetrieveUpdateDestroyView,
    PodcastListCreateView, PodcastRetrieveUpdateDestroyView,
    EpisodeListCreateView, EpisodeRetrieveUpdateDestroyView
)

from .serializers import (
    PodcastSerializer, EpisodeSerializer,
    CategorySerializer, TagsSerializer
)

class PodcastModelTestCase(TestCase):
    def setUp(self):
        self.podcast = Podcast.objects.create(
            title="Test Podcast",
            description="This is a test podcast.",
            author="Test Author"
        )

    def test_podcast_creation(self):
        self.assertEqual(self.podcast.title, "Test Podcast")
        self.assertEqual(self.podcast.description, "This is a test podcast.")
        self.assertEqual(self.podcast.author, "Test Author")