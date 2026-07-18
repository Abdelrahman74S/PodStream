from .models import Podcast, Episode, Category, Tags
from .serializers import PodcastSerializer, EpisodeSerializer, CategorySerializer, TagsSerializer  
from rest_framework import status
from rest_framework.views import APIView, Response
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView , GenericAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from common.permission import ISListener, IsPodcasterOrAdmin
from common.services.views_count import increment_listen_count
from django.http import JsonResponse
from rest_framework import mixins
from common.services.chroma_service import chroma_service
from rest_framework.exceptions import ValidationError

User = get_user_model()


# Category Views
class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

class CategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


# Tags Views
class TagsListCreateView(ListCreateAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

class TagsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


# Podcast Views
class PodcastListCreateView(ListCreateAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsPodcasterOrAdmin()]
        return [AllowAny()]    

class PodcastRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsPodcasterOrAdmin()]
        return [AllowAny()]


# Episode Views
class EpisodeListCreateView(ListCreateAPIView):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsPodcasterOrAdmin()]
        return [AllowAny()]

class EpisodeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsPodcasterOrAdmin()]
        return [AllowAny()]
        
    def retrieve(self, request, *args, **kwargs):
        episode_id = self.kwargs.get('id')
        increment_listen_count(request, episode_id) 
        return super().retrieve(request, *args, **kwargs)


class PodcastSemanticSearch(mixins.ListModelMixin, GenericAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        
        if not query:
            raise ValidationError({'q': 'This search parameter is required.'})
        
        raw_results = chroma_service.podcasts_collection.query(
            query_texts=[query],
            n_results=3
        )
    
        metadatas = raw_results.get('metadatas', [[]])[0] if raw_results.get('metadatas') else []
        podcast_ids = [item['django_id'] for item in metadatas if 'django_id' in item]
        
        if not podcast_ids:
            return Podcast.objects.none()
    
        podcasts = list(Podcast.objects.filter(id__in=podcast_ids))
        
        podcasts.sort(key=lambda x: podcast_ids.index(str(x.id)) if str(x.id) in podcast_ids else len(podcast_ids))
        
        return podcasts

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class EpisodeSemanticSearch(mixins.ListModelMixin, GenericAPIView):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        
        if not query:
            raise ValidationError({'q': 'This search parameter is required.'})
        
        raw_results = chroma_service.episodes_collection.query(
            query_texts=[query],
            n_results=3
        )
    
        metadatas = raw_results.get('metadatas', [[]])[0] if raw_results.get('metadatas') else []
        episode_ids = [item['django_id'] for item in metadatas if 'django_id' in item]
        
        if not episode_ids:
            return Episode.objects.none()
    
        episodes = list(Episode.objects.filter(id__in=episode_ids))
        
        episodes.sort(key=lambda x: episode_ids.index(str(x.id)) if str(x.id) in episode_ids else len(episode_ids))
        
        return episodes

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)