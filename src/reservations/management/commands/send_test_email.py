from django.core.management.base import BaseCommand

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from reservations.tasks import send_test_email_task




class Command(BaseCommand):
    help = 'Send a test email via Celery task to verify email configuration.'

    def handle(self, *args, **options):
        result = send_test_email_task.delay()
        self.stdout.write('Test email task dispatched to Celery.')
        self.stdout.write(f'Task ID: {result.id}')

