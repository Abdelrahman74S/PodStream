from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import models
from .models import Subscription, Playlist, Comment
from .serializers import SubscriptionSerializer, PlaylistSerializer, CommentSerializer

# --- Subscription Views ---
class SubscriptionListCreateView(ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionDestroyView(DestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


# --- Playlist Views ---

class PlaylistListCreateView(ListCreateAPIView):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Playlist.objects.filter(
            models.Q(user=self.request.user) | models.Q(is_public=True)
        )


class PlaylistRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Playlist.objects.filter(user=self.request.user)
        return Playlist.objects.filter(
            models.Q(user=self.request.user) | models.Q(is_public=True)
        )


# --- Comment Views ---
class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Comment.objects.all()
        episode_id = self.request.query_params.get('episode')
        if episode_id:
            queryset = queryset.filter(episode_id=episode_id)
        return queryset


class CommentDestroyView(DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
