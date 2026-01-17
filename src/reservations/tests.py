from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from .models import Profile, Room, Reservation


class ModelTests(APITestCase):
    def test_profile_created_on_user_creation(self):
        u = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass")
        self.assertTrue(hasattr(u, "profile"))
        self.assertEqual(u.profile.role, "client")

    def test_profile_role_helpers(self):
        """Test the role helper methods."""
        client_user = User.objects.create_user(
            username="client", password="pass")
        client_user.profile.role = "client"
        client_user.profile.save()

        self.assertTrue(client_user.profile.is_client())
        self.assertFalse(client_user.profile.is_staff())
        self.assertFalse(client_user.profile.is_admin())

    def test_room_and_reservation_creation(self):
        room = Room.objects.create(
            number="101", room_type="single", capacity=1, price=100.0)
        u = User.objects.create_user(username="bob", password="pass")
        now = timezone.now()
        res = Reservation.objects.create(
            room=room, guest=u, check_in=now, check_out=now + timezone.timedelta(days=1))
        self.assertEqual(res.status, "confirmed")
        self.assertEqual(res.room.number, "101")

    def test_room_status_available_property(self):
        """Test the is_available property."""
        room = Room.objects.create(
            number="102", room_type="double", capacity=2, price=150.0,
            is_active=True, status="available"
        )
        self.assertTrue(room.is_available)

        # When room is not available
        room.status = "occupied"
        self.assertFalse(room.is_available)

        # When room is inactive
        room.is_active = False
        room.status = "available"
        self.assertFalse(room.is_available)

    def test_double_booking_prevention(self):
        """Test that overlapping reservations are prevented."""
        room = Room.objects.create(
            number="103", room_type="single", capacity=1, price=100.0)
        user1 = User.objects.create_user(username="guest1", password="pass")
        user2 = User.objects.create_user(username="guest2", password="pass")

        now = timezone.now()
        # First reservation: Jan 1-3
        res1 = Reservation.objects.create(
            room=room,
            guest=user1,
            check_in=now,
            check_out=now + timezone.timedelta(days=2)
        )

        # Attempt to create overlapping reservation: Jan 2-4 (should fail)
        res2 = Reservation(
            room=room,
            guest=user2,
            check_in=now + timezone.timedelta(days=1),
            check_out=now + timezone.timedelta(days=3)
        )
        with self.assertRaises(ValidationError):
            res2.clean()

    def test_exact_checkout_checkin_allowed(self):
        """Test that exact checkout-to-checkin times are allowed (no overlap)."""
        room = Room.objects.create(
            number="104", room_type="single", capacity=1, price=100.0)
        user1 = User.objects.create_user(username="guest3", password="pass")
        user2 = User.objects.create_user(username="guest4", password="pass")

        now = timezone.now()
        base_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # First reservation: Jan 1 00:00 - Jan 2 00:00
        res1 = Reservation.objects.create(
            room=room,
            guest=user1,
            check_in=base_time,
            check_out=base_time + timezone.timedelta(days=1)
        )

        # Second reservation starting exactly when first ends: Jan 2 00:00 - Jan 3 00:00
        res2 = Reservation(
            room=room,
            guest=user2,
            check_in=base_time + timezone.timedelta(days=1),
            check_out=base_time + timezone.timedelta(days=2)
        )
        # This should be allowed (no overlap)
        res2.clean()  # Should not raise

    def test_invalid_checkin_checkout(self):
        """Test that check_in >= check_out is rejected."""
        room = Room.objects.create(
            number="105", room_type="single", capacity=1, price=100.0)
        user = User.objects.create_user(username="guest5", password="pass")

        now = timezone.now()

        # Check-in after check-out
        res = Reservation(
            room=room,
            guest=user,
            check_in=now + timezone.timedelta(days=1),
            check_out=now
        )
        with self.assertRaises(ValidationError):
            res.clean()

    def test_reservation_properties(self):
        """Test is_past_checkin and is_past_checkout properties."""
        room = Room.objects.create(
            number="106", room_type="single", capacity=1, price=100.0)
        user = User.objects.create_user(username="guest6", password="pass")

        now = timezone.now()
        future_res = Reservation.objects.create(
            room=room,
            guest=user,
            check_in=now + timezone.timedelta(days=1),
            check_out=now + timezone.timedelta(days=2)
        )
        self.assertFalse(future_res.is_past_checkin)
        self.assertFalse(future_res.is_past_checkout)

        # Create a past reservation
        past_res = Reservation.objects.create(
            room=room,
            guest=user,
            check_in=now - timezone.timedelta(days=2),
            check_out=now - timezone.timedelta(days=1)
        )
        self.assertTrue(past_res.is_past_checkin)
        self.assertTrue(past_res.is_past_checkout)


class APITests(APITestCase):
    def test_register_and_token_and_create_reservation(self):
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"
        rooms_url = "/api/rooms/"
        reservations_url = "/api/reservations/"

        # register
        data = {"username": "carol", "email": "carol@example.com",
                "password": "pass", "role": "client"}
        r = self.client.post(register_url, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # obtain token
        r = self.client.post(
            token_url, {"username": "carol", "password": "pass"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        access = r.data.get("access")
        self.assertIsNotNone(access)

        # create a room as admin user (create superuser directly)
        admin = User.objects.create_superuser(
            username="admin", email="a@a.com", password="adminpass")
        self.client.force_authenticate(user=admin)
        room = self.client.post(rooms_url, {
                                "number": "200", "room_type": "double", "capacity": 2, "price": "150.00"}, format="json")
        self.assertIn(room.status_code,
                      (status.HTTP_201_CREATED, status.HTTP_200_OK))
        self.client.force_authenticate(user=None)

        # create reservation as carol
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        # get room id
        rooms = self.client.get(rooms_url).data
        room_id = rooms[0]["id"]
        now = timezone.now()
        res_payload = {"room_id": room_id, "check_in": now.isoformat(
        ), "check_out": (now + timezone.timedelta(days=1)).isoformat()}
        # Avoid contacting Redis/Celery broker during tests by patching the task's delay
        with patch("reservations.tasks.send_reservation_confirmation.delay") as mock_delay:
            with patch("reservations.tasks.send_checkin_reminder.apply_async") as mock_reminder:
                r = self.client.post(
                    reservations_url, res_payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_double_booking_api(self):
        """Test that double booking is prevented via API."""
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"
        rooms_url = "/api/rooms/"
        reservations_url = "/api/reservations/"

        # Create two users
        user1_data = {"username": "user1", "email": "user1@example.com",
                      "password": "pass", "role": "client"}
        user2_data = {"username": "user2", "email": "user2@example.com",
                      "password": "pass", "role": "client"}
        self.client.post(register_url, user1_data, format="json")
        self.client.post(register_url, user2_data, format="json")

        # Get tokens
        r = self.client.post(
            token_url, {"username": "user1", "password": "pass"}, format="json")
        token1 = r.data.get("access")
        r = self.client.post(
            token_url, {"username": "user2", "password": "pass"}, format="json")
        token2 = r.data.get("access")

        # Create room as admin
        admin = User.objects.create_superuser(
            username="admin", email="a@a.com", password="adminpass")
        self.client.force_authenticate(user=admin)
        self.client.post(rooms_url, {
            "number": "300", "room_type": "single", "capacity": 1, "price": "100.00"}, format="json")
        self.client.force_authenticate(user=None)

        # Get room ID
        rooms = self.client.get(rooms_url).data
        room_id = rooms[0]["id"]
        now = timezone.now()

        # User1 creates a reservation
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        res_payload = {
            "room_id": room_id,
            "check_in": now.isoformat(),
            "check_out": (now + timezone.timedelta(days=2)).isoformat()
        }
        with patch("reservations.tasks.send_reservation_confirmation.delay"):
            with patch("reservations.tasks.send_checkin_reminder.apply_async"):
                r = self.client.post(
                    reservations_url, res_payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # User2 tries to create overlapping reservation
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        res_payload = {
            "room_id": room_id,
            "check_in": (now + timezone.timedelta(days=1)).isoformat(),
            "check_out": (now + timezone.timedelta(days=3)).isoformat()
        }
        with patch("reservations.tasks.send_reservation_confirmation.delay"):
            with patch("reservations.tasks.send_checkin_reminder.apply_async"):
                r = self.client.post(
                    reservations_url, res_payload, format="json")
        # Should return 400 Bad Request
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_reservation(self):
        """Test cancelling a reservation."""
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"
        rooms_url = "/api/rooms/"
        reservations_url = "/api/reservations/"

        # Register user
        user_data = {"username": "canceller", "email": "cancel@example.com",
                     "password": "pass", "role": "client"}
        self.client.post(register_url, user_data, format="json")

        # Get token
        r = self.client.post(
            token_url, {"username": "canceller", "password": "pass"}, format="json")
        token = r.data.get("access")

        # Create room as admin
        admin = User.objects.create_superuser(
            username="admin2", email="a2@a.com", password="adminpass")
        self.client.force_authenticate(user=admin)
        self.client.post(rooms_url, {
            "number": "400", "room_type": "single", "capacity": 1, "price": "100.00"}, format="json")
        self.client.force_authenticate(user=None)

        # Get room ID
        rooms = self.client.get(rooms_url).data
        room_id = rooms[0]["id"]
        now = timezone.now()

        # Create reservation
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res_payload = {
            "room_id": room_id,
            "check_in": now.isoformat(),
            "check_out": (now + timezone.timedelta(days=1)).isoformat()
        }
        with patch("reservations.tasks.send_reservation_confirmation.delay"):
            with patch("reservations.tasks.send_checkin_reminder.apply_async"):
                r = self.client.post(
                    reservations_url, res_payload, format="json")
        res_id = r.data["id"]

        # Cancel reservation
        cancel_url = f"{reservations_url}{res_id}/cancel/"
        r = self.client.post(cancel_url, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["status"], "cancelled")
