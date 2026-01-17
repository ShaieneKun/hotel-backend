from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import Room, Reservation, Profile
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    RoomSerializer,
    ReservationSerializer,
)
from .permissions import (
    IsAdminOrStaff,
    IsOwnerOrAdminOrStaff,
    CanCancelOwnReservation,
)
from .tasks import send_reservation_confirmation, send_checkin_reminder


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # add custom claims
        token["username"] = user.username
        token["email"] = user.email
        token["role"] = getattr(user.profile, "role", "client")
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return (permissions.AllowAny(),)
        elif self.action == "create":
            return (permissions.IsAdminUser(),)
        else:
            # update, partial_update, destroy require admin
            return (permissions.IsAdminUser(),)

    def get_queryset(self):
        # Clients see only active rooms
        if hasattr(self.request.user, "profile") and self.request.user.profile.is_client():
            return Room.objects.filter(is_active=True)
        # Staff and admins see all rooms
        return Room.objects.all()


class ReservationViewSet(viewsets.ModelViewSet):
    """
    Reservations API endpoint with role-based access control.

    - Clients: Can view/create their own reservations, cancel their own
    - Staff: Can view all reservations, update status (check-in/check-out)
    - Admin: Full access
    """
    serializer_class = ReservationSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Reservation.objects.none()

        # Admin and staff see all reservations
        if hasattr(user, "profile") and user.profile.role in ("admin", "staff"):
            return Reservation.objects.select_related("guest", "room").all()

        # Clients see only their own
        return Reservation.objects.filter(guest=user).select_related("guest", "room")

    def get_permissions(self):
        if self.action == "create":
            return (permissions.IsAuthenticated(),)
        elif self.action in ("list", "retrieve"):
            return (permissions.IsAuthenticated(),)
        elif self.action in ("update", "partial_update"):
            return (IsAdminOrStaff(),)
        elif self.action == "cancel":
            return (permissions.IsAuthenticated(),)
        elif self.action in ("check_in", "check_out"):
            return (IsAdminOrStaff(),)
        else:
            return (permissions.IsAdminUser(),)

    def perform_create(self, serializer):
        """Create reservation and trigger confirmation email."""
        reservation = serializer.save(guest=self.request.user)

        # Send confirmation email asynchronously
        send_reservation_confirmation.delay(reservation.id)

        # Schedule check-in reminder 24 hours before check-in
        eta = reservation.check_in - timedelta(hours=24)
        send_checkin_reminder.apply_async(
            args=[reservation.id],
            eta=eta
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancel a reservation.
        - Clients can only cancel their own reservations
        - Staff/Admin can cancel any reservation
        """
        reservation = self.get_object()

        # Check permissions
        if (
            hasattr(request.user, "profile")
            and request.user.profile.role not in ("admin", "staff")
            and reservation.guest != request.user
        ):
            return Response(
                {"detail": "You can only cancel your own reservations."},
                status=status.HTTP_403_FORBIDDEN
            )

        if reservation.status in ("checked_out", "cancelled"):
            return Response(
                {"detail": f"Cannot cancel a {reservation.get_status_display().lower()} reservation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = "cancelled"
        reservation.save()

        # Release room back to available if it was confirmed
        if reservation.room.status != "available":
            reservation.room.status = "available"
            reservation.room.save()

        # Return full serialized reservation
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrStaff])
    def check_in(self, request, pk=None):
        """
        Check in a guest (staff/admin only).
        Transitions: confirmed -> checked_in, room: available -> occupied
        """
        reservation = self.get_object()

        if reservation.status != "confirmed":
            return Response(
                {"detail": f"Cannot check in a {reservation.get_status_display().lower()} reservation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() < reservation.check_in:
            return Response(
                {"detail": "Guest cannot check in before the scheduled check-in time."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = "checked_in"
        reservation.save()

        # Update room status
        reservation.room.status = "occupied"
        reservation.room.save()

        # Return full serialized reservation
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrStaff])
    def check_out(self, request, pk=None):
        """
        Check out a guest (staff/admin only).
        Transitions: checked_in -> checked_out, room: occupied -> cleaning
        """
        reservation = self.get_object()

        if reservation.status not in ("confirmed", "checked_in"):
            return Response(
                {"detail": f"Cannot check out from {reservation.get_status_display().lower()} reservation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = "checked_out"
        reservation.save()

        # Update room status to cleaning
        reservation.room.status = "cleaning"
        reservation.room.save()

        # Return full serialized reservation
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrStaff])
    def mark_no_show(self, request, pk=None):
        """
        Mark a reservation as no-show (staff/admin only).
        This should be called if the guest didn't arrive.
        """
        reservation = self.get_object()

        if reservation.status != "confirmed":
            return Response(
                {"detail": f"Cannot mark {reservation.get_status_display().lower()} reservation as no-show."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = "no_show"
        reservation.save()

        # Release room back to available
        reservation.room.status = "available"
        reservation.room.save()

        # Return full serialized reservation
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
