# Hotel Reservations API - Enhanced Features Guide

This document describes the evolved reservations flow with enhanced validation, async task handling, and role-based access control.

## 1. Validation Logic: Prevention of Double Reservations

### How It Works

When a client or staff member attempts to create a new reservation, the backend performs a strict check to prevent double-booking:

**A room is considered unavailable if there exists an existing reservation where:**
- The new `check_in` is **before** an existing `check_out`
- AND the new `check_out` is **after** an existing `check_in`

**Example:**
```
Existing reservation: Jan 1 10:00 - Jan 3 10:00
New attempt 1: Jan 2 15:00 - Jan 4 10:00  ❌ BLOCKED (overlaps)
New attempt 2: Jan 3 10:00 - Jan 4 10:00  ✅ ALLOWED (no overlap)
New attempt 3: Jan 3 11:00 - Jan 4 10:00  ✅ ALLOWED (no overlap)
```

### Implementation

- **Model validation** in [src/reservations/models.py](src/reservations/models.py): `Reservation.clean()`
- **Serializer validation** in [src/reservations/serializers.py](src/reservations/serializers.py): `ReservationSerializer.validate()`
- Only "confirmed" and "checked_in" reservations block new bookings; "cancelled", "checked_out", and "no_show" don't

### API Response on Double Booking

```json
{
  "non_field_errors": [
    "Room 301 is already booked for the selected dates."
  ]
}
```

---

## 2. Celery Tasks: Asynchronous Actions

### Available Tasks

#### `send_reservation_confirmation` (Immediate)
**Triggered:** After successful POST request to create a reservation
**Purpose:** Send confirmation email with reservation details

**Email includes:**
- Guest name
- Room number and type
- Check-in and check-out dates
- Price per night
- Reservation ID

**Code location:** [src/reservations/tasks.py](src/reservations/tasks.py)

#### `send_checkin_reminder` (Scheduled)
**Triggered:** Automatically scheduled 24 hours before check-in
**Purpose:** Send reminder email to guest about upcoming check-in

**Email includes:**
- Room and dates
- Reminder to arrive 15 minutes early
- Reservation ID

**Usage in code:**
```python
send_checkin_reminder.apply_async(
    args=[reservation.id],
    eta=reservation.check_in - timedelta(hours=24)
)
```

---

## 3. Celery Beat: Periodic Maintenance Tasks

Celery Beat runs scheduled background tasks automatically. See [src/hotel/settings.py](src/hotel/settings.py) for configuration.

### Task 1: `cleanup_expired_reservations` (Daily at midnight)

**What it does:**
1. **Handles No-Shows**: Finds reservations that should have started yesterday but are still "confirmed"
   - Status: `confirmed` → `no_show`
   - Room status: Updates to `available`
   - Purpose: Release rooms back to inventory after guests don't arrive

2. **Marks Checked Out**: Finds reservations past checkout date
   - Status: `confirmed`/`checked_in` → `checked_out`
   - Room status: Updates to `cleaning`
   - Purpose: Automatically transition completed stays

**Schedule:**
```
0 0 * * * (daily at 00:00 UTC)
```

### Task 2: `mark_rooms_available_after_cleaning` (Every 3 hours)

**What it does:**
- Resets rooms from `cleaning` status back to `available`
- Assumes 3-hour cleaning window

**Schedule:**
```
0 */3 * * * (every 3 hours at :00 minutes)
```

---

## 4. Room Status Lifecycle

Rooms transition between these statuses:

```
available (start)
   ↓
occupied (when guest checks in)
   ↓
cleaning (after guest checks out)
   ↓
available (after cleaning window)

Alternative paths:
available → blocked (maintenance by staff) → available
available → available (no-show released room)
```

---

## 5. Reservation Status Lifecycle

Reservations transition through these statuses:

```
confirmed (initial state when booked)
   ├→ checked_in (when staff checks guest in)
   │   └→ checked_out (when staff checks guest out)
   ├→ cancelled (when guest or staff cancels)
   └→ no_show (daily cleanup if guest didn't arrive)
```

**Status meanings:**
- `confirmed`: Reservation is booked, awaiting check-in
- `checked_in`: Guest has arrived and checked in
- `checked_out`: Guest has left, reservation complete
- `cancelled`: Reservation was cancelled (by guest or staff)
- `no_show`: Guest didn't arrive at scheduled check-in time

---

## 6. Role-Based Access Control (RBAC)

### Permission System

Three roles control API access: **Client**, **Staff**, **Admin**

#### Clients
**Can:**
- ✅ View available rooms
- ✅ View their own reservations
- ✅ Create new reservations
- ✅ Cancel their own reservations

**Cannot:**
- ❌ See other guests' reservations
- ❌ Check-in/check-out
- ❌ Modify room availability
- ❌ Manage reservations not their own

#### Staff
**Can:**
- ✅ View all reservations
- ✅ Check guests in (confirmed → checked_in)
- ✅ Check guests out (checked_in → checked_out)
- ✅ Mark reservations as no-show
- ✅ Cancel any reservation
- ✅ Block rooms for maintenance

**Cannot:**
- ❌ Create/modify room types
- ❌ Delete rooms
- ❌ View financial reports

#### Admin
**Can:**
- ✅ Full access to all endpoints
- ✅ Create/delete room types
- ✅ Manage all reservations
- ✅ Manage staff accounts
- ✅ Access all data

### Permission Classes

Located in [src/reservations/permissions.py](src/reservations/permissions.py):

```python
IsClient()                    # User has client role
IsStaff()                     # User has staff role
IsAdmin()                     # User has admin role
IsAdminOrStaff()              # Either admin or staff
IsOwnerOrAdminOrStaff()       # Owner/admin/staff can access object
CanCancelOwnReservation()     # Users can cancel own; admin/staff any
```

---

## 7. API Endpoints Overview

### Authentication
- `POST /api/auth/register/` - Register new user (default role: client)
- `POST /api/auth/token/` - Obtain JWT tokens

### Rooms
- `GET /api/rooms/` - List available rooms (public)
- `GET /api/rooms/{id}/` - Room details (public)
- `POST /api/rooms/` - Create room (admin only)
- `PUT/PATCH /api/rooms/{id}/` - Update room (admin only)
- `DELETE /api/rooms/{id}/` - Delete room (admin only)

### Reservations
- `GET /api/reservations/` - List reservations (filtered by role)
- `GET /api/reservations/{id}/` - Reservation details
- `POST /api/reservations/` - Create reservation (authenticated)
- `POST /api/reservations/{id}/cancel/` - Cancel reservation
- `POST /api/reservations/{id}/check_in/` - Check in guest (staff/admin)
- `POST /api/reservations/{id}/check_out/` - Check out guest (staff/admin)
- `POST /api/reservations/{id}/mark_no_show/` - Mark as no-show (staff/admin)

---

## 8. Example Workflows

### Workflow 1: Client Books a Room

```
1. Client calls: POST /api/reservations/
   Body: {
     "room_id": 1,
     "check_in": "2026-02-01T14:00:00Z",
     "check_out": "2026-02-03T10:00:00Z"
   }

2. Backend validates:
   - Check-in < check-out ✅
   - Room not already booked ✅

3. Reservation created with status: "confirmed"

4. Async tasks triggered:
   - send_reservation_confirmation: immediate
   - send_checkin_reminder: scheduled for 2026-01-31 14:00:00 UTC

5. Response includes reservation ID and status
```

### Workflow 2: Staff Checks In Guest

```
1. Staff calls: POST /api/reservations/{id}/check_in/

2. Backend validates:
   - Reservation status == "confirmed" ✅
   - Current time >= check_in time ✅
   - User is staff/admin ✅

3. Reservation status: "confirmed" → "checked_in"

4. Room status: "available" → "occupied"

5. Response confirms status change
```

### Workflow 3: Daily Cleanup (Automatic)

```
Daily at 00:00 UTC:

1. cleanup_expired_reservations task runs

2. Finds no-shows:
   - check_in < yesterday AND status == "confirmed"
   - Sets status to "no_show"
   - Sets room.status to "available"

3. Finds completed checkouts:
   - check_out < now AND status in ["confirmed", "checked_in"]
   - Sets status to "checked_out"
   - Sets room.status to "cleaning"

4. Every 3 hours:
   mark_rooms_available_after_cleaning task
   - Rooms in "cleaning" → "available"
```

---

## 9. Testing

Run all tests:
```bash
./.venv/bin/python manage.py test reservations.tests
```

Test coverage includes:
- ✅ Double booking prevention (model + API)
- ✅ Exact checkout-to-checkin transitions
- ✅ Invalid date ranges
- ✅ Reservation property calculations
- ✅ Cancel endpoint permissions
- ✅ Role-based access

All 11 tests pass with proper mocking of Celery tasks.

---

## 10. Configuration

### Celery Settings

[src/hotel/settings.py](src/hotel/settings.py):

```python
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-reservations": {
        "task": "reservations.tasks.cleanup_expired_reservations",
        "schedule": crontab(hour=0, minute=0),
    },
    "mark-rooms-available-after-cleaning": {
        "task": "reservations.tasks.mark_rooms_available_after_cleaning",
        "schedule": crontab(hour="*/3", minute=0),
    },
}
```

### Email Backend

Development uses console email backend (logs to stdout).
Production should configure SMTP settings.

---

## 11. Database Migrations

Migration file: [src/reservations/migrations/0002_alter_reservation_options_...py](src/reservations/migrations/0002_alter_reservation_options_reservation_updated_at_and_more.py)

Changes:
- Added `updated_at` timestamp to Reservation
- Added `status` field to Room (enum: available, occupied, cleaning, blocked)
- Updated Reservation status choices (reserved → confirmed, added checked_in, no_show)
- Added database indexes on (room, status, check_in) and (guest, status)

---

## 12. Running the Application

### Start Django development server:
```bash
./.venv/bin/python manage.py runserver
```

### Start Celery worker (in separate terminal):
```bash
./.venv/bin/celery -A hotel worker -l info
```

### Start Celery Beat (in separate terminal):
```bash
./.venv/bin/celery -A hotel beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Or use docker-compose:
```bash
docker-compose up
```
