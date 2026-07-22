from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import models
from .models import Subscription, Playlist, Reply , Comment
from .serializers import SubscriptionSerializer, PlaylistSerializer, CommentSerializer , ReplySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


# --- Subscription Views ---
class SubscriptionListCreateView(ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['podcast']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

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
    filterset_fields = ['is_public', 'user']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

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
    filterset_fields = ['episode', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

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


class CommentReplyView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ReplySerializer

    def post(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            if request.user and request.user.is_authenticated:
                username = request.user.username
            else:
                username = serializer.validated_data.get('username') or 'Anonymous'
                if not username:
                    username = 'Anonymous'
            
            reply = Reply(
                username=username,
                text=serializer.validated_data['text']
            )
            
            if comment.replies is None:
                comment.replies = []
            comment.replies.append(reply)
            comment.save()
            
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
