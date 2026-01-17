from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates admin, staff, and client users with specific roles.'

    def handle(self, *args, **options):
        User = get_user_model()

        # Create superuser
        admin, created = User.objects.get_or_create(
            username='admin', defaults={'is_superuser': True, 'is_staff': True})
        if created:
            admin.set_password('123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
        else:
            self.stdout.write('Superuser admin already exists')

        # Create staff user
        staff, created = User.objects.get_or_create(
            username='staff', defaults={'is_staff': True})
        if created:
            staff.set_password('123')
            staff.save()
            self.stdout.write(self.style.SUCCESS('Created staff user: staff'))
        else:
            self.stdout.write('Staff user already exists')

        # Create client user
        client, created = User.objects.get_or_create(username='client')
        if created:
            client.set_password('123')
            client.save()
            self.stdout.write(self.style.SUCCESS(
                'Created client user: client'))
        else:
            self.stdout.write('Client user already exists')

        # Set roles on profile
        admin.profile.role = 'admin'
        admin.profile.save()
        staff.profile.role = 'staff'
        staff.profile.save()
        client.profile.role = 'client'
        client.profile.save()
        self.stdout.write(self.style.SUCCESS('Roles set on user profiles.'))
