from .models import Category, Tags, Podcast, Episode
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class TagsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = Tags
        fields = ['id', 'name']

class PodcastSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True
    )
    tags = TagsSerializer(many=True, read_only=True)
    tags_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), source='tags', many=True, write_only=True, required=False
    )
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Podcast
        fields = ['id', 'title', 'description', 'category', 'category_id', 'creator',
                'tags', 'tags_ids', 'cover_image', 'is_published', 'created_at', 'updated_at']

class EpisodeSerializer(serializers.ModelSerializer):
    podcast = PodcastSerializer(read_only=True)
    podcast_id = serializers.PrimaryKeyRelatedField(
        queryset=Podcast.objects.all(), source='podcast', write_only=True
    )
    id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Episode
        fields = ['id', 'podcast', 'podcast_id', 'title', 'description', 'audio_file', 'duration',
                'file_size', 'transcript', 'episode_number', 'is_explicit', 
                'publish_date', 'listen_count', 'created_at']