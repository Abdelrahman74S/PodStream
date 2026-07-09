from django.apps import AppConfig

class PodcastsConfig(AppConfig):
    name = 'podcasts'

    def ready(self):
        import podcasts.signals