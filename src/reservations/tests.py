from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
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

    def test_room_and_reservation_creation(self):
        room = Room.objects.create(
            number="101", room_type="single", capacity=1, price=100.0)
        u = User.objects.create_user(username="bob", password="pass")
        now = timezone.now()
        res = Reservation.objects.create(
            room=room, guest=u, check_in=now, check_out=now + timezone.timedelta(days=1))
        self.assertEqual(res.status, "reserved")
        self.assertEqual(res.room.number, "101")


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
            r = self.client.post(reservations_url, res_payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
