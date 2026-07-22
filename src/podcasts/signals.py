from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from .models import Podcast, Episode
from common.services.audio_processing import run_audio_processing_in_background
from common.services.chroma_service import chroma_service


# ==================== (post_delete) ====================

@receiver(post_delete, sender=Podcast)
def delete_podcast_cover_image(sender, instance, **kwargs):
    if instance.cover_image:
        instance.cover_image.delete(save=False)


@receiver(post_delete, sender=Episode)
def delete_episode_file(sender, instance, **kwargs):
    if instance.audio_file:
        instance.audio_file.delete(save=False)

# ========================================

def delete_old_file_on_change(model_class, instance, file_field_name):
    if not instance.pk:
        return

    try:
        old_instance = model_class.objects.get(pk=instance.pk)
    except model_class.DoesNotExist:
        return

    old_file = getattr(old_instance, file_field_name)
    new_file = getattr(instance, file_field_name)

    if old_file and old_file != new_file:
        old_file.delete(save=False)


# ==================== (pre_save) ====================

@receiver(pre_save, sender=Podcast)
def auto_delete_old_cover_on_change(sender, instance, **kwargs):
    delete_old_file_on_change(Podcast, instance, 'cover_image')


@receiver(pre_save, sender=Episode)
def auto_delete_old_audio_on_change(sender, instance, **kwargs):
    delete_old_file_on_change(Episode, instance, 'audio_file')


# ==================== (post_save audio processing) ====================

@receiver(post_save, sender=Episode)
def trigger_audio_processing(sender, instance, created, **kwargs):
    if created and instance.audio_file:
        run_audio_processing_in_background(instance.id)


# ==================== (chroma_service) ====================
@receiver(post_save, sender=Episode)
def sync_episode_to_chroma(sender, instance, created, **kwargs):
    if instance.transcript:
        try:
            chroma_service.sync_episode_transcript(instance)
        except Exception as e:
            print(f"ChromaDB Sync Error (Episode): {e}")

@receiver(post_delete, sender=Episode)
def delete_episode_from_chroma(sender, instance, **kwargs):
    try:
        chroma_service.delete_episode_transcript(instance.id)
    except Exception as e:
        print(f"ChromaDB Delete Error (Episode): {e}")


@receiver(post_save, sender=Podcast)
def sync_podcast_to_chroma(sender, instance, created, **kwargs):
    document_text = f"{instance.title} - {instance.description}"
    try:
        chroma_service.podcasts_collection.upsert(
            documents=[document_text],
            metadatas=[{
                "title": instance.title,
                "django_id": str(instance.id)
            }],
            ids=[f"podcast_{instance.id}"]
        )
    except Exception as e:
        print(f"ChromaDB Sync Error (Podcast): {e}")

@receiver(post_delete, sender=Podcast)
def delete_podcast_from_chroma(sender, instance, **kwargs):
    try:
        chroma_service.podcasts_collection.delete(ids=[f"podcast_{instance.id}"])
    except Exception as e:
        print(f"ChromaDB Delete Error (Podcast): {e}")