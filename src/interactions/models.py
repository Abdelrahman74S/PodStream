from django.db import models
from django.conf import settings
from django_mongodb_backend.models import EmbeddedModel
from django_mongodb_backend.fields import EmbeddedModelArrayField
from podcasts.models import Podcast, Episode

class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
        related_name="subscribers"
    )

    subscribed_at = models.DateTimeField(auto_now_add=True)
    notify_new_episodes = models.BooleanField(default=False)

    class Meta:
        db_table = "subscriptions"
        unique_together = ("user", "podcast")

    def __str__(self):
        return f"{self.user} - {self.podcast.title}"


class Playlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="playlists"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    episodes = models.ManyToManyField(
        Episode,
        related_name="playlists",
        blank=True
    )

    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "playlists"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Reply(EmbeddedModel):
    username = models.CharField(
    max_length=150,
    blank=True,
    null=True
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    text = models.TextField()

    replies = EmbeddedModelArrayField(
        embedded_model=Reply,
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.episode}"