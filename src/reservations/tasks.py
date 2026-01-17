from .models import Reservation, Room
from datetime import timedelta
from django.utils import timezone
from celery import shared_task


from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_test_email_task():
    subject = 'Test Email from Django via Celery'
    message = 'This is a test email sent from a Celery task.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['test@localhost']
    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)
    return True


@shared_task
def send_reservation_confirmation(reservation_id: int):
    """Send confirmation email after successful reservation creation."""
    try:
        reservation = Reservation.objects.select_related(
            "guest", "room").get(id=reservation_id)
    except Reservation.DoesNotExist:
        return False

    subject = f"Reservation Confirmation #{reservation.pk}"
    body = (
        f"Hello {reservation.guest.first_name or reservation.guest.username},\n\n"
        f"Your reservation has been confirmed!\n\n"
        f"Room: {reservation.room.number} ({reservation.room.room_type})\n"
        f"Check-in: {reservation.check_in.strftime('%Y-%m-%d %H:%M')}\n"
        f"Check-out: {reservation.check_out.strftime('%Y-%m-%d %H:%M')}\n"
        f"Price per night: ${reservation.room.price}\n\n"
        f"Reservation ID: {reservation.pk}\n"
        f"Status: {reservation.get_status_display()}\n\n"
        "Thank you for choosing our hotel!\n"
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [reservation.guest.email],
        fail_silently=False
    )
    return True


@shared_task
def send_checkin_reminder(reservation_id: int):
    """Send check-in reminder 24 hours before the reservation."""
    try:
        reservation = Reservation.objects.select_related(
            "guest", "room").get(id=reservation_id)
    except Reservation.DoesNotExist:
        return False

    subject = f"Reminder: Check-in Tomorrow - Reservation #{reservation.pk}"
    body = (
        f"Hello {reservation.guest.first_name or reservation.guest.username},\n\n"
        f"This is a friendly reminder that you have a reservation starting tomorrow!\n\n"
        f"Room: {reservation.room.number} ({reservation.room.room_type})\n"
        f"Check-in: {reservation.check_in.strftime('%Y-%m-%d %H:%M')}\n"
        f"Check-out: {reservation.check_out.strftime('%Y-%m-%d %H:%M')}\n\n"
        "Please arrive at least 15 minutes early for check-in.\n"
        "Thank you!\n"
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [reservation.guest.email],
        fail_silently=False
    )
    return True


@shared_task
def cleanup_expired_reservations():
    """
    Daily cleanup task that:
    1. Marks reservations as checked_out if checkout date has passed
    2. Updates room status to cleaning if reservation is checking out today
    3. Handles no-shows for reservations that should have started yesterday
    """
    now = timezone.now()
    updated_count = 0

    # Handle no-shows: reservations that should have checked in yesterday but are still confirmed
    yesterday = now - timedelta(days=1)
    no_shows = Reservation.objects.filter(
        status="confirmed",
        check_in__lt=yesterday
    )
    for reservation in no_shows:
        reservation.status = "no_show"
        reservation.save()
        # Release the room back to available
        reservation.room.status = "available"
        reservation.room.save()
        updated_count += 1

    # Mark as checked out and set room to cleaning if checkout date has passed
    checked_out = Reservation.objects.filter(
        status__in=["confirmed", "checked_in"],
        check_out__lt=now
    )
    for reservation in checked_out:
        reservation.status = "checked_out"
        reservation.save()
        # Set room to cleaning status
        reservation.room.status = "cleaning"
        reservation.room.save()
        updated_count += 1

    return {"no_shows_handled": no_shows.count(), "checked_out": checked_out.count(), "total_updated": updated_count}


@shared_task
def mark_rooms_available_after_cleaning():
    """
    Reset rooms from cleaning status back to available after a cleaning period.
    This can be called after a specific time (e.g., 3 hours after checkout).
    """
    rooms = Room.objects.filter(status="cleaning")
    count = rooms.update(status="available")
    return count
