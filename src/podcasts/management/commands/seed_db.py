from django.core.management.base import BaseCommand
from podcasts.factory import seed_database

class Command(BaseCommand):
    help = "Seeds the database with professional, realistic persistent data for PodStream"

    def add_arguments(self, parser):
        parser.add_argument(
            '--podcasts',
            type=int,
            default=6,
            help='Number of podcast shows to create'
        )
        parser.add_argument(
            '--episodes',
            type=int,
            default=3,
            help='Number of episodes per podcast to create'
        )

    def handle(self, *args, **options):
        num_podcasts = options['podcasts']
        num_episodes = options['episodes']
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))
        seed_database(num_podcasts=num_podcasts, num_episodes_per_podcast=num_episodes)
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
