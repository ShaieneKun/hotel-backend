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
        # Profile may already be created by signal; update role if needed
        profile, _ = Profile.objects.get_or_create(
            user=user, defaults={"role": role})
        if profile.role != role:
            profile.role = role
            profile.save()
        return user


class RoomSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ("id", "number", "room_type",
                  "capacity", "price", "is_active", "status", "is_available")
        read_only_fields = ("is_available",)

    def get_is_available(self, obj):
        return obj.is_available


class ReservationSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        source="room", queryset=Room.objects.filter(is_active=True), write_only=True
    )
    is_past_checkin = serializers.SerializerMethodField()
    is_past_checkout = serializers.SerializerMethodField()

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
            "total_price",
            "created_at",
            "updated_at",
            "is_past_checkin",
            "is_past_checkout",
        )
        read_only_fields = ("status", "total_price", "created_at", "updated_at",
                            "is_past_checkin", "is_past_checkout")

    def get_is_past_checkin(self, obj):
        return obj.is_past_checkin

    def get_is_past_checkout(self, obj):
        return obj.is_past_checkout

    def validate(self, data):
        """Validate the reservation dates and double-booking."""
        check_in = data.get("check_in")
        check_out = data.get("check_out")
        room = data.get("room")

        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError(
                    "Check-in must be before check-out."
                )

            # Check for conflicts
            conflicting = Reservation.objects.filter(
                room=room,
                status__in=["confirmed", "checked_in"],
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            if conflicting.exists():
                raise serializers.ValidationError(
                    f"Room {room.number} is already booked for the selected dates."
                )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["guest"] = user
        return super().create(validated_data)
