import random
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Category, Tags, Podcast, Episode
from interactions.models import Subscription, Playlist, Comment, Reply

User = get_user_model()

# ==========================================
# CURATED REALISTIC DATA SEEDS
# ==========================================

REAL_CATEGORIES = [
    {"name": "Technology & AI", "description": "Latest trends in software development, AI, cloud computing, and cybersecurity."},
    {"name": "Business & Startups", "description": "Entrepreneurship, venture capital, growth strategies, and leadership insights."},
    {"name": "Science & Innovation", "description": "Exploring deep tech, physics, biology, space exploration, and discoveries."},
    {"name": "Health & Mindset", "description": "Biohacking, mental health, fitness routines, and personal development."},
    {"name": "Society & Culture", "description": "In-depth conversations on history, philosophy, modern culture, and human stories."},
    {"name": "True Crime & Mystery", "description": "Investigative storytelling, unsolved mysteries, and criminal psychology."},
]

REAL_TAGS = [
    "Python", "Django", "Machine Learning", "Artificial Intelligence",
    "Cloud Native", "MongoDB", "DevOps", "Startups", "Leadership",
    "Productivity", "Neuroscience", "Mental Health", "Web3", "Cybersecurity"
]

PODCAST_SHOWS = [
    {
        "title": "The Tech Horizon",
        "description": "Deep dives into modern software architecture, backend engineering, cloud platforms, and cutting-edge artificial intelligence.",
        "category": "Technology & AI",
        "tags": ["Python", "Django", "Cloud Native", "DevOps"]
    },
    {
        "title": "AI & The Future",
        "description": "Conversations with researchers, founders, and engineers building LLMs, autonomous agents, and neural networks.",
        "category": "Technology & AI",
        "tags": ["Artificial Intelligence", "Machine Learning", "Python"]
    },
    {
        "title": "Startup Founders Uncut",
        "description": "Behind-the-scenes stories of building high-growth startups, raising seed funding, scaling teams, and navigating market pivots.",
        "category": "Business & Startups",
        "tags": ["Startups", "Leadership", "Productivity"]
    },
    {
        "title": "Mind & Muscle",
        "description": "Actionable science-backed routines for optimizing mental clarity, physical endurance, sleep hygiene, and overall longevity.",
        "category": "Health & Mindset",
        "tags": ["Mental Health", "Productivity", "Neuroscience"]
    },
    {
        "title": "Cosmic Frontiers",
        "description": "Exploring quantum mechanics, astrophysics, space exploration missions, and the mysteries of the universe.",
        "category": "Science & Innovation",
        "tags": ["Neuroscience", "Artificial Intelligence"]
    },
    {
        "title": "Deep Code Discussions",
        "description": "Technical insights on microservices, database optimizations, API design patterns, and asynchronous programming in Python.",
        "category": "Technology & AI",
        "tags": ["Python", "Django", "MongoDB"]
    }
]

EPISODE_TITLES = [
    "Building Scalable Async APIs with Python & Django",
    "Demystifying Large Language Models: From Architecture to Deployment",
    "How to Scale Microservices to 1 Million Active Users",
    "The Psychology of High-Performing Engineering Teams",
    "Optimizing Database Queries: Lessons Learned in Production",
    "Biohacking Your Sleep for Maximum Cognitive Performance",
    "Navigating Seed Round Fundraising in a Competitive Market",
    "The Evolution of Cloud Infrastructure & Kubernetes",
    "Designing Secure Systems in the Era of Zero Trust",
    "Deep Dive into Vector Databases & Semantic Search"
]

SAMPLE_TRANSCRIPTS = [
    "Welcome back to the podcast. Today we are joined by lead engineers to discuss building resilient backend architectures...",
    "In this episode, we break down how transformer models operate, attention mechanisms, and fine-tuning techniques for custom datasets...",
    "Join us as we explore effective strategies for managing database indexing, connection pooling, and caching with Redis...",
    "We sit down with a veteran founder to discuss fundraising strategies, hiring key talent, and avoiding early startup pitfalls..."
]

SAMPLE_COMMENTS = [
    "This was an incredibly insightful episode! Loved the explanation of query optimization.",
    "Great discussion on LLM deployment. Would love a follow-up episode on RAG architectures!",
    "Super practical advice. Added this podcast to my favorites list immediately.",
    "Very informative discussion on async Python. Thanks for sharing these production tips!"
]

SAMPLE_REPLIES = [
    "Totally agree! The query optimization section was gold.",
    "Thanks for tuning in! A follow-up episode is already in production.",
    "Appreciate the feedback! Glad you found the tips helpful."
]


# ==========================================
# FACTORY BOY DEFINITIONS
# ==========================================

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@podstream.io")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = User.Role.PODCASTER
    bio = factory.Faker("paragraph", nb_sentences=2)
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "PodStream123#"
        self.set_password(password)
        if create:
            self.save()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: REAL_CATEGORIES[n % len(REAL_CATEGORIES)]["name"])
    description = factory.Sequence(lambda n: REAL_CATEGORIES[n % len(REAL_CATEGORIES)]["description"])


class TagsFactory(DjangoModelFactory):
    class Meta:
        model = Tags
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: REAL_TAGS[n % len(REAL_TAGS)])


class PodcastFactory(DjangoModelFactory):
    class Meta:
        model = Podcast

    title = factory.Sequence(lambda n: PODCAST_SHOWS[n % len(PODCAST_SHOWS)]["title"])
    description = factory.Sequence(lambda n: PODCAST_SHOWS[n % len(PODCAST_SHOWS)]["description"])
    category = factory.SubFactory(CategoryFactory)
    creator = factory.SubFactory(UserFactory)
    is_published = True

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)
        else:
            all_tags = list(Tags.objects.all())
            if all_tags:
                selected_tags = random.sample(all_tags, min(2, len(all_tags)))
                self.tags.add(*selected_tags)


class EpisodeFactory(DjangoModelFactory):
    class Meta:
        model = Episode

    podcast = factory.SubFactory(PodcastFactory)
    title = factory.Sequence(lambda n: EPISODE_TITLES[n % len(EPISODE_TITLES)])
    description = factory.Faker("paragraph", nb_sentences=3)
    audio_file = factory.django.FileField(filename="sample_episode.mp3", data=b"dummy audio stream content")
    duration = factory.LazyFunction(lambda: random.randint(300, 3600))
    file_size = factory.LazyFunction(lambda: random.randint(5000000, 50000000))
    transcript = factory.Sequence(lambda n: SAMPLE_TRANSCRIPTS[n % len(SAMPLE_TRANSCRIPTS)])
    episode_number = factory.Sequence(lambda n: n + 1)
    is_explicit = False
    publish_date = factory.LazyFunction(timezone.now)
    listen_count = factory.LazyFunction(lambda: random.randint(50, 10000))


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory, role=User.Role.LISTENER)
    podcast = factory.SubFactory(PodcastFactory)
    notify_new_episodes = True


class PlaylistFactory(DjangoModelFactory):
    class Meta:
        model = Playlist

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"My Favorite Episodes Vol. {n + 1}")
    description = "A curated collection of top podcast episodes."
    is_public = True

    @factory.post_generation
    def episodes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.episodes.add(*extracted)
        else:
            all_episodes = list(Episode.objects.all())
            if all_episodes:
                selected_episodes = random.sample(all_episodes, min(3, len(all_episodes)))
                self.episodes.add(*selected_episodes)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    episode = factory.SubFactory(EpisodeFactory)
    user = factory.SubFactory(UserFactory, role=User.Role.LISTENER)
    text = factory.Sequence(lambda n: SAMPLE_COMMENTS[n % len(SAMPLE_COMMENTS)])

    @factory.post_generation
    def replies(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.replies = extracted
        else:
            sample_reply = Reply(
                username="podstream_listener",
                text=random.choice(SAMPLE_REPLIES)
            )
            self.replies = [sample_reply]


# ==========================================
# DATABASE SEEDER HELPER FUNCTION
# ==========================================

def seed_database(num_podcasts=6, num_episodes_per_podcast=3):
    """
    Seeds the database with professional, realistic, persistent data for PodStream.
    """
    print("Seeding PodStream database with professional persistent data...")

    # 1. Seed Categories & Tags
    categories = [CategoryFactory(name=cat["name"], description=cat["description"]) for cat in REAL_CATEGORIES]
    tags = [TagsFactory(name=tag) for tag in REAL_TAGS]
    print(f"[+] Created {len(categories)} categories and {len(tags)} tags.")

    # 2. Seed Podcasters
    podcasters = [
        UserFactory(
            username=f"podcaster_{i+1}",
            email=f"podcaster{i+1}@podstream.io",
            first_name=f"Host",
            last_name=f"User {i+1}",
            role=User.Role.PODCASTER,
            bio=f"Podcast host & creator on PodStream."
        )
        for i in range(3)
    ]
    print(f"[+] Created {len(podcasters)} podcaster users.")

    # 3. Seed Podcasts
    podcasts = []
    for i, show in enumerate(PODCAST_SHOWS):
        cat = Category.objects.filter(name=show["category"]).first() or categories[0]
        creator = podcasters[i % len(podcasters)]
        p = PodcastFactory(
            title=show["title"],
            description=show["description"],
            category=cat,
            creator=creator,
            is_published=True
        )
        show_tags = Tags.objects.filter(name__in=show["tags"])
        p.tags.add(*show_tags)
        podcasts.append(p)

    print(f"[+] Created {len(podcasts)} podcast shows with tags.")

    # 4. Seed Episodes
    episodes = []
    for podcast in podcasts:
        for ep_num in range(1, num_episodes_per_podcast + 1):
            ep = EpisodeFactory(
                podcast=podcast,
                title=f"{podcast.title} - Episode #{ep_num}: {random.choice(EPISODE_TITLES)}",
                episode_number=ep_num
            )
            episodes.append(ep)

    print(f"[+] Created {len(episodes)} episodes.")

    # 5. Seed Listener Users, Subscriptions, Playlists & Comments
    listeners = [
        UserFactory(
            username=f"listener_{i+1}",
            email=f"listener{i+1}@podstream.io",
            first_name=f"Listener",
            last_name=f"User {i+1}",
            role=User.Role.LISTENER
        )
        for i in range(5)
    ]

    for listener in listeners:
        subscribed_podcasts = random.sample(podcasts, 2)
        for p in subscribed_podcasts:
            SubscriptionFactory(user=listener, podcast=p)

        PlaylistFactory(
            user=listener,
            title=f"{listener.username}'s Daily Mix",
            episodes=random.sample(episodes, 3)
        )

        commented_episodes = random.sample(episodes, 2)
        for ep in commented_episodes:
            CommentFactory(user=listener, episode=ep)

    print("[+] Created listeners, subscriptions, playlists, and comments.")
    print("[SUCCESS] Database seeding completed successfully!")
