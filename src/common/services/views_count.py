from podcasts.models import Episode
from django.db.models import F


def increment_listen_count(request, episode_id):
    session_key = f'viewed_user_{episode_id}'
    
    if not request.session.get(session_key, False):
        Episode.objects.filter(pk=episode_id).update(listen_count=F('listen_count') + 1)
        request.session[session_key] = True