# Quick Reference: Hotel Reservations API

## Registration & Authentication

### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "client"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com"
}
```

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Use the `access` token in headers:
```bash
-H "Authorization: Bearer <access_token>"
```

---

## Rooms API

### List all available rooms
```bash
curl http://localhost:8000/api/rooms/
```

### Get room details
```bash
curl http://localhost:8000/api/rooms/1/
```

### Create a room (admin only)
```bash
curl -X POST http://localhost:8000/api/rooms/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "301",
    "room_type": "deluxe",
    "capacity": 4,
    "price": "250.00"
  }'
```

---

## Reservations API

### Create a reservation
```bash
curl -X POST http://localhost:8000/api/reservations/ \
  -H "Authorization: Bearer <client_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "check_in": "2026-02-01T14:00:00Z",
    "check_out": "2026-02-03T10:00:00Z"
  }'
```

Response:
```json
{
  "id": 5,
  "guest": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "client"
  },
  "room": {
    "id": 1,
    "number": "301",
    "room_type": "deluxe",
    "capacity": 4,
    "price": "250.00",
    "status": "available",
    "is_available": true
  },
  "check_in": "2026-02-01T14:00:00Z",
  "check_out": "2026-02-03T10:00:00Z",
  "status": "confirmed",
  "created_at": "2026-01-17T10:30:00Z",
  "updated_at": "2026-01-17T10:30:00Z",
  "is_past_checkin": false,
  "is_past_checkout": false
}
```

### List your reservations
```bash
curl http://localhost:8000/api/reservations/ \
  -H "Authorization: Bearer <client_token>"
```

### Get reservation details
```bash
curl http://localhost:8000/api/reservations/5/ \
  -H "Authorization: Bearer <client_token>"
```

### Cancel a reservation
```bash
curl -X POST http://localhost:8000/api/reservations/5/cancel/ \
  -H "Authorization: Bearer <client_token>"
```

Response:
```json
{
  "id": 5,
  "status": "cancelled",
  "message": "Reservation cancelled successfully"
}
```

---

## Staff Operations

### Check in a guest (staff/admin only)
```bash
curl -X POST http://localhost:8000/api/reservations/5/check_in/ \
  -H "Authorization: Bearer <staff_token>"
```

Response:
```json
{
  "id": 5,
  "status": "checked_in",
  "room_status": "occupied",
  "message": "Guest checked in successfully"
}
```

### Check out a guest (staff/admin only)
```bash
curl -X POST http://localhost:8000/api/reservations/5/check_out/ \
  -H "Authorization: Bearer <staff_token>"
```

Response:
```json
{
  "id": 5,
  "status": "checked_out",
  "room_status": "cleaning",
  "message": "Guest checked out successfully"
}
```

### Mark as no-show (staff/admin only)
```bash
curl -X POST http://localhost:8000/api/reservations/5/mark_no_show/ \
  -H "Authorization: Bearer <staff_token>"
```

Response:
```json
{
  "id": 5,
  "status": "no_show",
  "room_status": "available",
  "message": "Reservation marked as no-show"
}
```

---

## Error Responses

### Double Booking Error
```json
{
  "non_field_errors": [
    "Room 301 is already booked for the selected dates."
  ]
}
```

### Invalid Date Range
```json
{
  "non_field_errors": [
    "Check-in must be before check-out."
  ]
}
```

### Permission Denied
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not Found
```json
{
  "detail": "Not found."
}
```

---

## Status Lifecycle

### Reservation Statuses
- `confirmed` → Initial state after booking
- `checked_in` → Guest arrived and checked in
- `checked_out` → Guest left (checkout complete)
- `cancelled` → Reservation was cancelled
- `no_show` → Guest didn't arrive (automatic)

### Room Statuses
- `available` → Ready for booking
- `occupied` → Guest is checked in
- `cleaning` → Room is being cleaned
- `blocked` → Room is blocked (maintenance, etc.)

---

## Role-Based Access

| Action | Client | Staff | Admin |
|--------|--------|-------|-------|
| List rooms | ✅ | ✅ | ✅ |
| Book room | ✅ | ✅ | ✅ |
| View own reservations | ✅ | - | - |
| View all reservations | - | ✅ | ✅ |
| Check in guest | - | ✅ | ✅ |
| Check out guest | - | ✅ | ✅ |
| Cancel own reservation | ✅ | ✅ | ✅ |
| Cancel any reservation | - | ✅ | ✅ |
| Create room | - | - | ✅ |
| Update room | - | - | ✅ |
| Delete room | - | - | ✅ |

---

## Example Workflows

### Workflow 1: Complete Stay
```bash
# 1. Client creates reservation
POST /api/reservations/ → status: confirmed

# 2. Day before: Client receives reminder email (automatic)

# 3. Check-in day: Staff checks guest in
POST /api/reservations/{id}/check_in/ → status: checked_in, room: occupied

# 4. Check-out day: Staff checks guest out
POST /api/reservations/{id}/check_out/ → status: checked_out, room: cleaning

# 5. After cleanup period: Room becomes available (automatic)
```

### Workflow 2: Cancellation
```bash
# 1. Client creates reservation
POST /api/reservations/ → status: confirmed

# 2. Client cancels
POST /api/reservations/{id}/cancel/ → status: cancelled, room: available
```

### Workflow 3: No-Show
```bash
# 1. Client creates reservation
POST /api/reservations/ → status: confirmed

# 2. Check-in day passes, guest doesn't arrive

# 3. Daily cleanup task runs at midnight (automatic)
# → Marks as: status: no_show, room: available
```

---

## Testing

### Run all tests
```bash
./.venv/bin/python manage.py test reservations.tests
```

### Run specific test
```bash
./.venv/bin/python manage.py test reservations.tests.APITests.test_double_booking_api
```

### Run with coverage
```bash
./.venv/bin/coverage run --source='.' manage.py test reservations.tests
./.venv/bin/coverage report
```

---

## Troubleshooting

### Celery tasks not running
1. Ensure Redis is running: `redis-cli ping` should return `PONG`
2. Start Celery worker: `./.venv/bin/celery -A hotel worker -l info`
3. Start Celery Beat: `./.venv/bin/celery -A hotel beat -l info`

### Emails not sending
1. Check Django settings for EMAIL_BACKEND
2. Development: Emails logged to console
3. Production: Configure SMTP in settings

### Database migrations issues
```bash
# Check migration status
./.venv/bin/python manage.py showmigrations

# Apply migrations
./.venv/bin/python manage.py migrate

# Create new migration after model changes
./.venv/bin/python manage.py makemigrations
```

---

## Resources

- [RESERVATIONS_GUIDE.md](RESERVATIONS_GUIDE.md) - Complete feature documentation
- [EVOLUTION_SUMMARY.md](EVOLUTION_SUMMARY.md) - Development summary
- [src/reservations/tests.py](src/reservations/tests.py) - Test examples
- [src/reservations/models.py](src/reservations/models.py) - Data models
- [src/reservations/views.py](src/reservations/views.py) - API endpoints
