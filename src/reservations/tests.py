from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from decimal import Decimal

from .models import Profile, Room, Reservation
from .utils import create_sample_users, SAMPLE_USERS


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


class UtilsTests(APITestCase):
    """Tests for utility functions."""

    def test_create_sample_users_creates_users(self):
        """Test that create_sample_users creates all expected users."""
        messages = create_sample_users()

        self.assertTrue(len(messages) > 0)

        # Verify all users were created
        for user_data in SAMPLE_USERS:
            user = User.objects.get(username=user_data['username'])
            self.assertEqual(user.email, user_data['email'])
            self.assertEqual(user.first_name, user_data['first_name'])
            self.assertEqual(user.last_name, user_data['last_name'])
            self.assertEqual(user.profile.role, user_data['role'])

    def test_create_sample_users_is_idempotent(self):
        """Test that calling create_sample_users twice doesn't create duplicates."""
        create_sample_users()
        initial_count = User.objects.count()

        # Call again
        create_sample_users()
        final_count = User.objects.count()

        self.assertEqual(initial_count, final_count)


class TotalPriceTests(APITestCase):
    """Tests for the total_price field on reservations."""

    def test_total_price_calculated_on_creation(self):
        """Test that total_price is calculated when a reservation is created."""
        room = Room.objects.create(
            number="TP1", room_type="single", capacity=1, price=Decimal("100.00"))
        user = User.objects.create_user(username="tp_user", password="pass")

        now = timezone.now()
        reservation = Reservation.objects.create(
            room=room,
            guest=user,
            check_in=now,
            check_out=now + timezone.timedelta(days=3)
        )

        # 3 days at 100/day = 300
        self.assertEqual(reservation.total_price, Decimal("300.00"))

    def test_total_price_minimum_one_night(self):
        """Test that total_price calculates minimum 1 night for same-day stays."""
        room = Room.objects.create(
            number="TP2", room_type="single", capacity=1, price=Decimal("150.00"))
        user = User.objects.create_user(username="tp_user2", password="pass")

        # Same day check-in and check-out (within hours)
        now = timezone.now()
        reservation = Reservation(
            room=room,
            guest=user,
            check_in=now,
            check_out=now + timezone.timedelta(hours=12)
        )

        # calculate_total_price should return 1 night minimum
        self.assertEqual(reservation.calculate_total_price(),
                         Decimal("150.00"))


class PermissionTests(APITestCase):
    """Tests for permission-based access control."""

    def test_client_cannot_update_reservation_status(self):
        """Test that a client cannot update reservation status directly."""
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"
        rooms_url = "/api/rooms/"
        reservations_url = "/api/reservations/"

        # Create client user
        user_data = {"username": "perm_client", "email": "perm@example.com",
                     "password": "pass", "role": "client"}
        self.client.post(register_url, user_data, format="json")
        r = self.client.post(
            token_url, {"username": "perm_client", "password": "pass"}, format="json")
        token = r.data.get("access")

        # Create room as admin
        admin = User.objects.create_superuser(
            username="perm_admin", email="pa@a.com", password="adminpass")
        self.client.force_authenticate(user=admin)
        self.client.post(rooms_url, {
            "number": "PERM1", "room_type": "single", "capacity": 1, "price": "100.00"}, format="json")
        self.client.force_authenticate(user=None)

        # Get room ID and create reservation
        rooms = self.client.get(rooms_url).data
        room_id = rooms[0]["id"]
        now = timezone.now()

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

        # Try to update status as client (should fail)
        update_url = f"{reservations_url}{res_id}/"
        r = self.client.patch(
            update_url, {"status": "checked_in"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_check_in_guest(self):
        """Test that staff can check in a guest."""
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"
        rooms_url = "/api/rooms/"
        reservations_url = "/api/reservations/"

        # Create client
        client_data = {"username": "checkin_client", "email": "cc@example.com",
                       "password": "pass", "role": "client"}
        self.client.post(register_url, client_data, format="json")
        r = self.client.post(
            token_url, {"username": "checkin_client", "password": "pass"}, format="json")
        client_token = r.data.get("access")

        # Create staff user
        staff_user = User.objects.create_user(
            username="checkin_staff", email="cs@example.com", password="pass")
        staff_user.profile.role = "staff"
        staff_user.profile.save()

        # Create room as admin
        admin = User.objects.create_superuser(
            username="checkin_admin", email="ca@a.com", password="adminpass")
        self.client.force_authenticate(user=admin)
        self.client.post(rooms_url, {
            "number": "CHECKIN1", "room_type": "single", "capacity": 1, "price": "100.00"}, format="json")
        self.client.force_authenticate(user=None)

        # Get room ID and create reservation as client
        rooms = self.client.get(rooms_url).data
        room_id = rooms[0]["id"]
        now = timezone.now()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {client_token}")
        res_payload = {
            "room_id": room_id,
            # Past check-in
            "check_in": (now - timezone.timedelta(hours=1)).isoformat(),
            "check_out": (now + timezone.timedelta(days=1)).isoformat()
        }
        with patch("reservations.tasks.send_reservation_confirmation.delay"):
            with patch("reservations.tasks.send_checkin_reminder.apply_async"):
                r = self.client.post(
                    reservations_url, res_payload, format="json")
        res_id = r.data["id"]

        # Staff checks in the guest
        self.client.force_authenticate(user=staff_user)
        check_in_url = f"{reservations_url}{res_id}/check_in/"
        r = self.client.post(check_in_url, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["status"], "checked_in")


class JWTTokenTests(APITestCase):
    """Tests for JWT token customization."""

    def test_token_contains_user_info(self):
        """Test that JWT token contains username, email, and role."""
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"

        # Register user
        user_data = {
            "username": "jwt_user",
            "email": "jwt@example.com",
            "password": "pass",
            "role": "client",
            "first_name": "JWT",
            "last_name": "User"
        }
        self.client.post(register_url, user_data, format="json")

        # Get token
        r = self.client.post(
            token_url, {"username": "jwt_user", "password": "pass"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        access_token = r.data.get("access")
        self.assertIsNotNone(access_token)

        # Decode token (without verification for testing)
        import jwt
        decoded = jwt.decode(access_token, options={"verify_signature": False})

        self.assertEqual(decoded.get("username"), "jwt_user")
        self.assertEqual(decoded.get("email"), "jwt@example.com")
        self.assertEqual(decoded.get("role"), "client")
