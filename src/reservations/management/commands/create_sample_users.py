from django.core.management.base import BaseCommand
from reservations.utils import create_sample_users


class Command(BaseCommand):
    help = 'Creates admin, staff, and client users with specific roles.'

    def handle(self, *args, **options):
        results = create_sample_users()
        for message in results:
            self.stdout.write(self.style.SUCCESS(message))
