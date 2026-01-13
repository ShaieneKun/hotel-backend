from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Room, Reservation, Profile


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=Profile.ROLE_CHOICES, default="client", write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password",
                  "first_name", "last_name", "role")

    def create(self, validated_data):
        role = validated_data.pop("role", "client")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        # signals may already create a Profile; avoid duplicate unique constraint
        Profile.objects.get_or_create(user=user, defaults={"role": role})
        return user


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "number", "room_type",
                  "capacity", "price", "is_active")


class ReservationSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        source="room", queryset=Room.objects.filter(is_active=True), write_only=True
    )

    class Meta:
        model = Reservation
        fields = (
            "id",
            "guest",
            "room",
            "room_id",
            "check_in",
            "check_out",
            "status",
            "created_at",
        )
        read_only_fields = ("status", "created_at")

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["guest"] = user
        return super().create(validated_data)
