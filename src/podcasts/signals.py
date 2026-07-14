from django.db.models.signals import post_delete, pre_save ,post_save
from django.dispatch import receiver
from .models import Podcast, Episode
from common.services.audio_processing import run_audio_processing_in_background


@receiver(post_delete, sender=Podcast)
def delete_podcast_cover_image(sender, instance, **kwargs):
    if instance.cover_image:
        instance.cover_image.delete(save=False)

@receiver(post_delete, sender=Episode)
def delete_episode_file(sender, instance, **kwargs):
    if instance.audio_file:
        instance.audio_file.delete(save=False)

@receiver(pre_save, sender=Podcast)
def auto_delete_old_cover_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_podcast = Podcast.objects.get(pk=instance.pk)
    except Podcast.DoesNotExist:
        return False
    old_cover = old_podcast.cover_image
    new_cover = instance.cover_image
    if old_cover and old_cover != new_cover:
        old_cover.delete(save=False)

@receiver(pre_save, sender=Episode)
def auto_delete_old_audio_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False 
    try:
        old_episode = Episode.objects.get(pk=instance.pk)
    except Episode.DoesNotExist:
        return False
    old_audio = old_episode.audio_file
    new_audio = instance.audio_file
    if old_audio and old_audio != new_audio:
        old_audio.delete(save=False)


@receiver(post_save, sender=Episode)
def trigger_audio_processing(sender, instance, created, **kwargs):
    if created and instance.audio_file:
        run_audio_processing_in_background(instance.id)