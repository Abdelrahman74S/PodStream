from django.utils import timezone
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import Podcast, Episode, Tags, Category
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
from django.contrib.auth import get_user_model

from common.services.views_count import increment_listen_count





User = get_user_model()




# ==========================================
# 1. MODEL TESTS
# ==========================================
class PodcastModelTestCase(TestCase):
    def setUp(self):
        # 1. Create a User
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='securepassword123'
        )
        
        # 2. Create a Category
        self.category = Category.objects.create(name='Technology')
        
        # 3. Create Tags
        self.tag1 = Tags.objects.create(name='python')
        self.tag2 = Tags.objects.create(name='django')

        # 4. Create the Podcast (Notice 'tags' is NOT here)
        self.podcast = Podcast.objects.create(
            title="Test Podcast",
            description="This is a test podcast.",
            creator=self.user,
            category=self.category,
            is_published=True
        )
        
        self.podcast.tags.add(self.tag1, self.tag2)

    def test_podcast_creation(self):
        self.assertEqual(self.podcast.title, "Test Podcast")
        self.assertEqual(self.podcast.description, "This is a test podcast.")
        self.assertEqual(self.podcast.creator, self.user)
        self.assertEqual(self.podcast.category, self.category)
        self.assertTrue(self.podcast.is_published)

    def test_podcast_str_method(self):
        self.assertEqual(str(self.podcast), "Test Podcast")

    def test_podcast_tags_relationship(self):
        self.assertEqual(self.podcast.tags.count(), 2)
        self.assertIn(self.tag1, self.podcast.tags.all())
        self.assertIn(self.tag2, self.podcast.tags.all())

    def test_podcast_default_and_auto_fields(self):
        self.assertTrue(self.podcast.is_published)
        self.assertIsNotNone(self.podcast.created_at)
        self.assertIsNotNone(self.podcast.updated_at)
        self.assertFalse(self.podcast.cover_image) 


# ==========================================
# 2. SERIALIZER TESTS 
# ==========================================
class PodcastSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='serializer_user', password='pass123')
        self.podcast = Podcast.objects.create(
            title="Serializer Podcast",
            description="Testing serializers",
            creator=self.user
        )
        self.serializer = PodcastSerializer(instance=self.podcast)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {'id', 'title', 'description', 'creator', 'category', 'tags', 'is_published' , 'cover_image', 'created_at', 'updated_at'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serializer_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['title'], "Serializer Podcast")
        self.assertEqual(data['creator'], str(self.user.id)) 


# ==========================================
# 3. VIEW / API TESTS 
# ==========================================
class PodcastViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='view_user', email='view_user@example.com', password='pass123')
        self.category = Category.objects.create(name='Technology')
        self.podcast = Podcast.objects.create(
            title="View Podcast",
            description="Testing views",
            creator=self.user,
            category=self.category
        )

        self.list_url = reverse('podcast-list-create') 
        self.detail_url = reverse('podcast-detail', kwargs={'id': str(self.podcast.pk)})

    def test_podcast_list_view(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 

    def test_podcast_retrieve_view(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "View Podcast")
        
    def test_podcast_create_view_unauthenticated(self):
        data = {
            'title': 'New Podcast',
            'description': 'Should fail',
            'creator': str(self.user.id),
            'category': str(self.category.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])





# ==========================================
# 1. MODEL TESTS
# ==========================================
class EpisodeModelTestCase(TestCase):
    def setUp(self):
        # 1. Create a User
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='securepassword123'
        )
        
        # 2. Create a Category
        self.category = Category.objects.create(name='Technology')
        
        self.tag1 = Tags.objects.create(name='python')
        self.tag2 = Tags.objects.create(name='django')
    
        self.podcast = Podcast.objects.create(
            title="Test Podcast",
            description="This is a test podcast.",
            creator=self.user,         
            category=self.category,     
            is_published=True
        )
        
        self.podcast.tags.add(self.tag1, self.tag2)
        
        # 5. Create Episode 
        self.episode = Episode.objects.create(
            title="Test Episode",
            description="This is a test episode.",
            podcast=self.podcast,        
            audio_file="test_audio.mp3",
            duration=1800,
            file_size=1024000,
            episode_number=1,
            publish_date=timezone.now()
        )
        
    def test_episode_creation(self):
        self.assertEqual(self.episode.title, "Test Episode")
        self.assertEqual(self.episode.description, "This is a test episode.")
        self.assertEqual(self.episode.podcast, self.podcast)
        self.assertEqual(self.episode.duration, 1800)
        self.assertEqual(self.episode.file_size, 1024000)
        self.assertEqual(self.episode.episode_number, 1)
    
    def test_episode_str_method(self):
        self.assertEqual(str(self.episode), f"{self.podcast.title} - Ep #{self.episode.episode_number}: {self.episode.title}")
    
    def test_episode_default_and_auto_fields(self):
        self.assertIsNotNone(self.episode.created_at)
        self.assertEqual(self.episode.listen_count, 0)


# ==========================================
# 2. SERIALIZER TESTS 
# ==========================================
class EpisodeSerializerTestCase(TestCase):
    def setUp(self):
        # 1. Create a User
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='securepassword123'
        )
        
        # 2. Create a Category
        self.category = Category.objects.create(name='Technology')
        
        self.tag1 = Tags.objects.create(name='python')
        self.tag2 = Tags.objects.create(name='django')
    
        self.podcast = Podcast.objects.create(
            title="Test Podcast",
            description="This is a test podcast.",
            creator=self.user,         
            category=self.category,     
            is_published=True
        )
        
        self.podcast.tags.add(self.tag1, self.tag2)
        
        # 5. Create Episode 
        self.episode = Episode.objects.create(
            title="Test Episode",
            description="This is a test episode.",
            podcast=self.podcast,        
            audio_file="test_audio.mp3",
            duration=1800,
            file_size=1024000,
            episode_number=1,
            publish_date=timezone.now()
        )
        
        self.serializer = EpisodeSerializer(instance=self.episode)

    
    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        
        expected_fields = {'id', 'podcast',  'title', 'description', 'audio_file', 'duration',
                'file_size', 'transcript', 'episode_number', 'is_explicit', 
                'publish_date', 'listen_count', 'created_at'}
        
        self.assertEqual(set(data.keys()), expected_fields)

# ==========================================
# 3. VIEW / API TESTS 
# ==========================================
class EpisodeViewsTestCase(APITestCase):
    def setUp(self):
        # Clear database to prevent leakage across tests (MongoDB transaction limitations)
        Episode.objects.all().delete()
        Podcast.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

        # 1. Create a podcaster user
        self.podcaster = User.objects.create_user(
            username='podcaster_user',
            email='podcaster_user@example.com',
            password='pass123',
            role=User.Role.PODCASTER
        )
        # 2. Create a listener user
        self.listener = User.objects.create_user(
            username='listener_user',
            email='listener_user@example.com',
            password='pass123',
            role=User.Role.LISTENER
        )
        # 3. Create a category
        self.category = Category.objects.create(name='Technology')
        # 4. Create a podcast
        self.podcast = Podcast.objects.create(
            title="View Podcast",
            description="Testing views",
            creator=self.podcaster,
            category=self.category
        )
        # 5. Create an episode
        self.episode = Episode.objects.create(
            title="View Episode",
            description="Testing episode views",
            podcast=self.podcast,
            audio_file="test_audio.mp3",
            duration=300,
            file_size=5000,
            episode_number=1,
            publish_date=timezone.now()
        )

        self.list_url = reverse('episode-list-create')
        self.detail_url = reverse('episode-detail', kwargs={'id': str(self.episode.pk)})

    def test_episode_list_view(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_episode_retrieve_view(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "View Episode")

    def test_episode_create_view_unauthenticated(self):
        audio_file = SimpleUploadedFile("test_audio.mp3", b"file_content", content_type="audio/mpeg")
        data = {
            'title': 'New Episode',
            'description': 'Should fail',
            'podcast_id': str(self.podcast.id),
            'duration': 120,
            'file_size': 2000,
            'episode_number': 2,
            'publish_date': timezone.now().isoformat(),
            'audio_file': audio_file
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_episode_create_view_authenticated_podcaster(self):
        self.client.force_authenticate(user=self.podcaster)
        audio_file = SimpleUploadedFile("test_audio.mp3", b"file_content", content_type="audio/mpeg")
        data = {
            'title': 'New Episode',
            'description': 'Should succeed',
            'podcast_id': str(self.podcast.id),
            'duration': 120,
            'file_size': 2000,
            'episode_number': 2,
            'publish_date': timezone.now().isoformat(),
            'audio_file': audio_file
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Episode')

    def test_episode_create_view_authenticated_listener(self):
        self.client.force_authenticate(user=self.listener)
        audio_file = SimpleUploadedFile("test_audio.mp3", b"file_content", content_type="audio/mpeg")
        data = {
            'title': 'New Episode',
            'description': 'Should fail',
            'podcast_id': str(self.podcast.id),
            'duration': 120,
            'file_size': 2000,
            'episode_number': 2,
            'publish_date': timezone.now().isoformat(),
            'audio_file': audio_file
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_episode_update_by_creator(self):
        self.client.force_authenticate(user=self.podcaster)
        data = {'title': 'Updated Episode Title'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Episode Title')

    def test_episode_update_by_other_podcaster(self):
        other_podcaster = User.objects.create_user(
            username='other_podcaster',
            email='other_podcaster@example.com',
            password='pass123',
            role=User.Role.PODCASTER
        )
        self.client.force_authenticate(user=other_podcaster)
        data = {'title': 'Updated Episode Title'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_episode_delete_by_creator(self):
        self.client.force_authenticate(user=self.podcaster)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_episode_delete_by_other_podcaster(self):
        other_podcaster_del = User.objects.create_user(
            username='other_podcaster_del',
            email='other_podcaster_del@example.com',
            password='pass123',
            role=User.Role.PODCASTER
        )
        self.client.force_authenticate(user=other_podcaster_del)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


from unittest.mock import patch, MagicMock

class AudioProcessingTestCase(TestCase):
    def setUp(self):
        # Clear database to prevent leakage across tests
        Episode.objects.all().delete()
        Podcast.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

        self.podcaster = User.objects.create_user(
            username='podcaster_test',
            email='podcaster_test@example.com',
            password='pass123',
            role=User.Role.PODCASTER
        )
        self.category = Category.objects.create(name='Test Category')
        self.podcast = Podcast.objects.create(
            title="Audio Test Podcast",
            description="Testing audio signals",
            creator=self.podcaster,
            category=self.category
        )

    @patch('common.services.audio_processing.genai')
    def test_audio_processing_service(self, mock_genai):
        # Mock genai.Client and its methods
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        mock_file = MagicMock()
        mock_file.name = "mocked_gemini_file"
        mock_client.files.upload.return_value = mock_file

        mock_response = MagicMock()
        mock_response.text = "This is a mocked transcription from Gemini."
        mock_client.models.generate_content.return_value = mock_response

        # Create a mock file
        audio_file = SimpleUploadedFile("test_episode.mp3", b"dummy mp3 content", content_type="audio/mpeg")
        
        from common.services.audio_processing import process_episode_audio
        result = process_episode_audio(audio_file)

        self.assertEqual(result["size_bytes"], len(b"dummy mp3 content"))
        self.assertEqual(result["transcript"], "This is a mocked transcription from Gemini.")

    @patch('common.services.audio_processing.genai')
    @patch('common.services.audio_processing.process_episode_audio')
    def test_audio_processing_signal(self, mock_process, mock_genai):
        mock_process.return_value = {
            "size_bytes": 12345,
            "duration_seconds": 120.0,
            "transcript": "Hello world from signal test."
        }

        audio_file = SimpleUploadedFile("test_episode_signal.mp3", b"dummy audio content", content_type="audio/mpeg")
        
        from common.services.audio_processing import process_audio_task
        
        episode = Episode.objects.create(
            title="Signal Test Episode",
            description="Testing signal triggers",
            podcast=self.podcast,
            audio_file=audio_file,
            duration=0,
            file_size=0,
            episode_number=1,
            publish_date=timezone.now()
        )

        process_audio_task(episode.id)

        # Refresh from database
        episode.refresh_from_db()
        self.assertEqual(episode.file_size, 12345)
        self.assertEqual(episode.duration, 120)
        self.assertEqual(episode.transcript, "Hello world from signal test.")
        
        
class TestviewsCounts(TestCase):
    def setUp(self):
        # Clear database to prevent leakage across tests (MongoDB transaction limitations)
        Episode.objects.all().delete()
        Podcast.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

        # 1. Create a podcaster user
        self.podcaster = User.objects.create_user(
            username='podcaster_user',
            email='podcaster_user@example.com',
            password='pass123',
            role=User.Role.PODCASTER
        )
        # 2. Create a listener user
        self.listener = User.objects.create_user(
            username='listener_user',
            email='listener_user@example.com',
            password='pass123',
            role=User.Role.LISTENER
        )
        # 3. Create a category
        self.category = Category.objects.create(name='Technology')
        # 4. Create a podcast
        self.podcast = Podcast.objects.create(
            title="View Podcast",
            description="Testing views",
            creator=self.podcaster,
            category=self.category
        )
        # 5. Create an episode
        self.episode = Episode.objects.create(
            title="View Episode",
            description="Testing episode views",
            podcast=self.podcast,
            audio_file=SimpleUploadedFile("test_audio.mp3", b"dummy_audio_content", content_type="audio/mpeg"),            
            episode_number=1,
            publish_date=timezone.now()
        )

        self.detail_url = reverse('episode-detail', kwargs={'id': str(self.episode.pk)})
    
    def test_increment_listen_count_on_first_visit(self):
        
        self.assertEqual(self.episode.listen_count, 0)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['listen_count'], 1)

        self.episode.refresh_from_db()
        self.assertEqual(self.episode.listen_count, 1)

    def test_no_duplicate_increment_in_same_session(self):
        
        response1 = self.client.get(self.detail_url)
        self.assertEqual(response1.data['listen_count'], 1)

        response2 = self.client.get(self.detail_url)
        self.assertEqual(response2.data['listen_count'], 1)

        self.episode.refresh_from_db()
        self.assertEqual(self.episode.listen_count, 1)