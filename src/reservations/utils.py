"""
Utility functions for the reservations app.
"""
from django.contrib.auth import get_user_model


# Sample users configuration for testing and initial setup
SAMPLE_USERS = [
    {
        'username': 'admin',
        'email': 'admin@hotel.local',
        'first_name': 'Admin',
        'last_name': 'User',
        'password': '123',
        'role': 'admin',
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'username': 'staff',
        'email': 'staff@hotel.local',
        'first_name': 'Staff',
        'last_name': 'Member',
        'password': '123',
        'role': 'staff',
        'is_superuser': False,
        'is_staff': True,
    },
    {
        'username': 'client',
        'email': 'client@hotel.local',
        'first_name': 'Client',
        'last_name': 'Guest',
        'password': '123',
        'role': 'client',
        'is_superuser': False,
        'is_staff': False,
    },
]


def create_sample_users():
    """
    Create sample users for testing and development.
    This function is idempotent - it will not create duplicate users.

    Returns:
        list: A list of status messages for each user operation.
    """
    User = get_user_model()
    messages = []

    for user_data in SAMPLE_USERS:
        username = user_data['username']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_superuser': user_data['is_superuser'],
                'is_staff': user_data['is_staff'],
            }
        )

        if created:
            user.set_password(user_data['password'])
            user.save()
            messages.append(f"Created user: {username} ({user_data['role']})")
        else:
            # Update existing user fields if needed
            updated = False
            if not user.email:
                user.email = user_data['email']
                updated = True
            if not user.first_name:
                user.first_name = user_data['first_name']
                updated = True
            if not user.last_name:
                user.last_name = user_data['last_name']
                updated = True
            if updated:
                user.save()
                messages.append(f"Updated user: {username}")
            else:
                messages.append(f"User already exists: {username}")

        # Set role on profile (idempotent)
        if hasattr(user, 'profile'):
            user.profile.role = user_data['role']
            user.profile.save()

    messages.append("Sample users setup complete.")
    return messages
