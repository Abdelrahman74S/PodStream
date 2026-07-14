import io
import tempfile
import os
import threading
import mutagen
from google import genai
from django.conf import settings
from podcasts.models import Episode 
import mimetypes  

def get_audio_mime_type(file_ext):
    audio_mime_types = {
        '.m4a': 'audio/mp4',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
    }
    
    if file_ext in audio_mime_types:
        return audio_mime_types[file_ext]
        
    mime_type, _ = mimetypes.guess_type(f"file{file_ext}")
    return mime_type or 'application/octet-stream'

def process_episode_audio(audio_file):
    """
    Processes a Django FieldFile (audio_file), extracts its size and duration (in seconds),
    and uses Gemini 1.5 Flash to transcribe the audio content using the google-genai SDK.
    """
    # 1. Get file size directly from Django FileField
    size_bytes = audio_file.size
    size_bytes = size_bytes / (1024 * 1024)
    # 2. Read bytes to calculate duration
    audio_file.open('rb')
    try:
        audio_bytes = audio_file.read()
    finally:
        audio_file.close()

    # Get original file extension (e.g. '.m4a' or '.mp3')
    file_ext = os.path.splitext(audio_file.name)[1].lower() or '.mp3'
    mime_type = get_audio_mime_type(file_ext)
    
    # 3. Request transcription from Gemini API using the File API (best for audio files)
    tmp_path = None
    duration_seconds = 0.0
    try:
        # Initialize client (will automatically use GEMINI_API_KEY from environment variables)
        client = genai.Client()

        # Save audio temporarily to disk to upload to Gemini File API and calculate duration
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # Calculate duration of the audio file using mutagen.File (supports mp3, m4a, etc.)
        try:
            audio = mutagen.File(tmp_path)
            if audio is not None and audio.info is not None:
                duration_seconds = audio.info.length
        except Exception:
            duration_seconds = 0.0

        # Upload the audio file to Gemini
        gemini_file = client.files.upload(
            file=tmp_path, 
            config={"mime_type": mime_type}
        )

        # Generate transcript using gemini-flash-latest
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[
                gemini_file,
                "Please transcribe this audio file into text. Return only the transcription, without any extra text or conversational response."
            ]
        )
        transcript = response.text

        # Cleanup the file from Gemini's storage
        client.files.delete(name=gemini_file.name)

    except Exception as e:
        # Fallback if Gemini API call fails or key is missing
        transcript = f"Transcription failed: {str(e)}"
    finally:
        # Cleanup temporary local file
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    return {
        "size_bytes": size_bytes,
        "duration_seconds": round(duration_seconds, 2),
        "transcript": transcript,
    }


def process_audio_task(episode_id):
    from django.db import connection
    try:
        episode = Episode.objects.get(id=episode_id)
        
        if not episode.audio_file:
            return

        result = process_episode_audio(episode.audio_file)
        
        episode.file_size = result["size_bytes"]
        episode.duration = int(result["duration_seconds"])
        episode.transcript = result["transcript"]
        
        episode.save()
        print(f"Episode {episode_id} processed successfully.")

    except Exception as e:
        print(f"Error processing episode {episode_id}: {e}")
    finally:
        connection.close()

def run_audio_processing_in_background(episode_id):
    thread = threading.Thread(target=process_audio_task, args=(episode_id,))
    thread.start()
