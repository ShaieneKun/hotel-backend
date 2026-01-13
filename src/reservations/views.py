from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Room, Reservation, Profile
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    RoomSerializer,
    ReservationSerializer,
)
from .tasks import send_reservation_confirmation


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
        return (permissions.IsAdminUser(),)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("guest", "room").all()
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return (permissions.IsAuthenticated(),)
        return (permissions.IsAuthenticated(),)

    def perform_create(self, serializer):
        reservation = serializer.save()
        # dispatch async email
        send_reservation_confirmation.delay(reservation.id)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != "reserved":
            return Response({"detail": "Cannot cancel"}, status=status.HTTP_400_BAD_REQUEST)
        reservation.status = "cancelled"
        reservation.save()
        return Response({"status": "cancelled"})
