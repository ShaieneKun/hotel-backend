from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Reservation


@shared_task
def send_reservation_confirmation(reservation_id: int):
    try:
        reservation = Reservation.objects.select_related(
            "guest", "room").get(id=reservation_id)
    except Reservation.DoesNotExist:
        return False
    subject = f"Reservation Confirmation #{reservation.id}"
    body = (
        f"Hello {reservation.guest.first_name or reservation.guest.username},\n\n"
        f"Your reservation for room {reservation.room.number} from {reservation.check_in} to {reservation.check_out} is confirmed.\n\n"
        "Thank you for choosing our hotel.\n"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
              [reservation.guest.email])
    return True


@shared_task
def release_expired_reservations():
    now = timezone.now()
    expired = Reservation.objects.filter(status="reserved", check_out__lt=now)
    count = 0
    for r in expired:
        r.status = "checked_out"
        r.save()
        count += 1
    return count
