from .models import Podcast, Episode, Category, Tags
from .serializers import PodcastSerializer, EpisodeSerializer, CategorySerializer, TagsSerializer  
from rest_framework import status
from rest_framework.views import APIView, Response
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from common.permission import ISListener, IsPodcasterOrAdmin

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