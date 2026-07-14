from .models import Category, Tags, Podcast, Episode
from rest_framework import serializers
from interactions.serializers import CommentSerializer
from bson import ObjectId  


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



class SimplePodcastSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Podcast
        fields = ['id', 'title', 'creator', 'category', 'cover_image']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for key, value in representation.items():
            if isinstance(value, ObjectId):
                representation[key] = str(value)
            elif isinstance(value, list):
                representation[key] = [
                    str(item) if isinstance(item, ObjectId) else item 
                    for item in value
                ]
        return representation


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
    episodes = serializers.SerializerMethodField() 
    
    class Meta:
        model = Podcast
        fields = ['id', 'title', 'description', 'category', 'category_id', 'creator',
                'tags', 'tags_ids', 'cover_image', 'is_published', 'episodes', 'created_at', 'updated_at']

    def get_episodes(self, obj):
        from .serializers import EpisodeSerializer 
        episodes = obj.episodes.all() 
        return EpisodeSerializer(episodes, many=True, context=self.context).data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        for key, value in representation.items():
            if isinstance(value, ObjectId):
                representation[key] = str(value)
            elif isinstance(value, list):
                representation[key] = [
                    str(item) if isinstance(item, ObjectId) else item 
                    for item in value
                ]
        return representation


class EpisodeSerializer(serializers.ModelSerializer):
    podcast = SimplePodcastSerializer(read_only=True)
    podcast_id = serializers.PrimaryKeyRelatedField(
        queryset=Podcast.objects.all(), source='podcast', write_only=True
    )
    id = serializers.CharField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = ['id', 'podcast', 'podcast_id', 'title', 'description', 'audio_file', 'duration',
                'file_size', 'transcript', 'episode_number', 'is_explicit', 
                'publish_date', 'listen_count', 'created_at', "comments"]
        read_only_fields = ['duration', 'file_size', 'transcript', 'listen_count']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for key, value in representation.items():
            if isinstance(value, ObjectId):
                representation[key] = str(value)
            elif isinstance(value, list):
                representation[key] = [
                    str(item) if isinstance(item, ObjectId) else item 
                    for item in value
                ]
        return representation