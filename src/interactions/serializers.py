from rest_framework import serializers
from .models import Subscription, Playlist, Comment, Reply
from podcasts.models import Podcast, Episode

class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    podcast = serializers.SerializerMethodField(read_only=True)
    podcast_id = serializers.PrimaryKeyRelatedField(
        queryset=Podcast.objects.all(), source='podcast', write_only=True
    )
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'podcast', 'podcast_id', 'subscribed_at', 'notify_new_episodes']

    def get_podcast(self, obj):
        return {
            "id": str(obj.podcast.id),
            "title": obj.podcast.title,
            "cover_image": obj.podcast.cover_image.url if obj.podcast.cover_image else None
        }

    def validate(self, attrs):
        user = self.context['request'].user
        podcast = attrs.get('podcast')
        if Subscription.objects.filter(user=user, podcast=podcast).exists():
            raise serializers.ValidationError("You are already subscribed to this podcast.")
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PlaylistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    episodes = serializers.SerializerMethodField(read_only=True)
    episodes_ids = serializers.PrimaryKeyRelatedField(
        queryset=Episode.objects.all(), source='episodes', many=True, write_only=True, required=False
    )
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'user', 'title', 'description', 'episodes', 'episodes_ids', 'is_public', 'created_at']

    def get_episodes(self, obj):
        return [
            {
                "id": str(ep.id),
                "title": ep.title,
                "duration": ep.duration,
                "episode_number": ep.episode_number
            } for ep in obj.episodes.all()
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['username', 'text', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    episode_id = serializers.PrimaryKeyRelatedField(
        queryset=Episode.objects.all(), source='episode', write_only=True
    )
    id = serializers.CharField(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'episode_id', 'user', 'text', 'replies', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
