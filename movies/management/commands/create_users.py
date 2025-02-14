import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from movies.models import Movie, UserPreference, UserRating


class Command(BaseCommand):
    help = 'Create 50 users with username and password as UserNumber<index> and assign random favorite movies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--movies-only',
            action='store_true',
            help='If set, only movies will be saved, not users'
        )

    def handle(self, *args, **kwargs):
        movies_only = kwargs['movies_only']

        if not movies_only:
            users = []
            for i in range(1, 51):
                username = f'User{i}'
                password = username
                email = f'{username}@example.com'

                user = User(
                    username=username,
                    email=email
                )
                user.set_password(password)
                users.append(user)

                self.stdout.write(self.style.SUCCESS(f'Created user {username}'))

            User.objects.bulk_create(users)
            self.stdout.write(self.style.SUCCESS('Successfully created 50 users'))

        movies = list(Movie.objects.all())
        user_ids = list(User.objects.values_list('id', flat=True))

        preferences = []

        for user_id in tqdm(user_ids, total=len(user_ids)):
            if not movies:
                self.stdout.write(self.style.WARNING(f'No movies available for user {user_id}'))
                continue

            num_movies = len(movies)
            num_ratings = random.randint(0, min(30000, num_movies))
            num_preferences = random.randint(0, min(1000, num_movies))

            shuffled_movies = random.sample(movies, num_movies)
            rating_movies = shuffled_movies[:num_ratings]
            preference_movies = shuffled_movies[:num_preferences]

            # Add preferences
            for movie in preference_movies:
                if not UserPreference.objects.filter(user_id=user_id, movie=movie).exists():
                    preferences.append(UserPreference(user_id=user_id, movie=movie))

            # Add or update ratings
            for movie in rating_movies:
                rating = random.randint(1, 10)
                UserRating.objects.update_or_create(
                    user_id=user_id,
                    movie=movie,
                    defaults={'rating': rating}
                )

        if preferences:
            UserPreference.objects.bulk_create(preferences)
            self.stdout.write(self.style.SUCCESS('Successfully added preferences'))

        self.stdout.write(self.style.SUCCESS('Successfully updated ratings'))
