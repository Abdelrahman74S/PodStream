from celery import shared_task
from common.services.audio_processing import process_audio_task

@shared_task
def process_audio_in_celery(episode_id):
    process_audio_task(episode_id)