# Evolution Summary: Hotel Reservations System

## Overview
The hotel reservations system has been significantly enhanced with comprehensive validation, asynchronous task handling, and role-based access control to manage the complete reservation lifecycle professionally.

## Key Changes

### 1. **Models** ([src/reservations/models.py](src/reservations/models.py))

#### Profile Model Enhancements
- Added helper methods: `is_admin()`, `is_staff()`, `is_client()` for RBAC checks

#### Room Model Enhancements
- Added `status` field with choices: `available`, `occupied`, `cleaning`, `blocked`
- Added `is_available` property that checks both status and is_active

#### Reservation Model Enhancements
- Updated status choices:
  - `reserved` → `confirmed` (more semantic)
  - Added `checked_in` (when guest arrives)
  - Added `no_show` (for no-shows)
  - Kept `checked_out`, `cancelled`

- Added fields:
  - `updated_at`: Track when reservation was last modified
  - Meta ordering by `-created_at`
  - Database indexes on (room, status, check_in) and (guest, status)

- Added validation:
  - `clean()` method that validates check-in < check-out
  - Double-booking prevention: checks for overlapping confirmed/checked_in reservations
  - Overridden `save()` to call `clean()`

- Added properties:
  - `is_past_checkin`: Check if we're past check-in time
  - `is_past_checkout`: Check if we're past checkout time

### 2. **Celery Tasks** ([src/reservations/tasks.py](src/reservations/tasks.py))

#### Enhanced Existing Tasks
- **`send_reservation_confirmation`**: Improved with hotel details, price, and reservation ID
- Renamed `release_expired_reservations` → `cleanup_expired_reservations` for clarity

#### New Tasks
- **`send_checkin_reminder`**: Sends email 24 hours before check-in
- **`cleanup_expired_reservations`**: Enhanced with:
  - No-show handling (marks past reservations as no-show)
  - Room status transitions (cleaning after checkout)
  - Returns detailed stats

- **`mark_rooms_available_after_cleaning`**: Resets rooms from cleaning to available

### 3. **Settings** ([src/hotel/settings.py](src/hotel/settings.py))

Updated Celery Beat schedule:
```python
CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-reservations": {
        "task": "reservations.tasks.cleanup_expired_reservations",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "mark-rooms-available-after-cleaning": {
        "task": "reservations.tasks.mark_rooms_available_after_cleaning",
        "schedule": crontab(hour="*/3", minute=0),  # Every 3 hours
    },
}
```

### 4. **Permissions** ([src/reservations/permissions.py](src/reservations/permissions.py) - NEW)

Created comprehensive permission classes:
- `IsClient`: Users with client role
- `IsStaff`: Users with staff role
- `IsAdmin`: Users with admin role
- `IsAdminOrStaff`: Either admin or staff
- `IsOwnerOrAdminOrStaff`: Owner, admin, or staff can access object
- `CanCancelOwnReservation`: Users can cancel own; admin/staff can cancel any

### 5. **Serializers** ([src/reservations/serializers.py](src/reservations/serializers.py))

#### RoomSerializer
- Added `status` field
- Added `is_available` computed field
- Shows rooms' current availability status

#### ReservationSerializer
- Added `updated_at` field
- Added computed fields: `is_past_checkin`, `is_past_checkout`
- Enhanced `validate()` method:
  - Checks check_in < check_out
  - Validates no double-booking (serializer-level)
  - Returns clear error messages

### 6. **Views** ([src/reservations/views.py](src/reservations/views.py))

#### RoomViewSet
- Refined permissions for list/retrieve (public) vs create/update (admin)
- Clients see only active rooms; staff/admin see all

#### ReservationViewSet
- **Complete RBAC implementation:**
  - Clients: See/create only their own reservations
  - Staff: See all, can manage status
  - Admin: Full access

- **New action endpoints:**
  - `/check_in/`: Check in guest (confirmed → checked_in, room available → occupied)
  - `/check_out/`: Check out guest (checked_in → checked_out, room → cleaning)
  - `/mark_no_show/`: Mark as no-show (confirmed → no_show, room → available)
  - `/cancel/`: Cancel reservation with proper permission checks

- **Async integration:**
  - `send_reservation_confirmation`: Immediate on create
  - `send_checkin_reminder`: Scheduled for 24hrs before check-in

### 7. **Tests** ([src/reservations/tests.py](src/reservations/tests.py))

Added 11 comprehensive tests:

**Model Tests:**
- Profile creation and role helpers
- Double booking prevention (overlapping dates)
- Exact checkout-to-checkin transitions (no overlap)
- Invalid check-in/checkout times
- Reservation status properties

**API Tests:**
- Complete registration → reservation flow
- Double booking prevention via API (returns 400)
- Reservation cancellation with permissions

All tests mock Celery tasks to avoid Redis dependencies.

### 8. **Database Migration** ([src/reservations/migrations/0002_...py](src/reservations/migrations/0002_alter_reservation_options_reservation_updated_at_and_more.py))

Changes applied:
- Added `updated_at` timestamp to Reservation
- Added `status` field to Room
- Updated Reservation status choices
- Added database performance indexes

---

## Architecture Decisions

### Double-Booking Prevention
- **Where**: Implemented at both model (clean) and serializer levels
- **Why dual**: Model ensures data integrity; serializer provides API-level error handling
- **Logic**: `check_in < existing.check_out AND check_out > existing.check_in`

### Reservation Statuses
```
confirmed (start)
  ├→ checked_in (staff action)
  │   └→ checked_out (staff action)
  ├→ cancelled (client/staff action)
  └→ no_show (automatic cleanup)
```

### Room Status Lifecycle
```
available → occupied → cleaning → available
```
Staff can also mark rooms as "blocked" for maintenance.

### Celery Tasks Timing
- **Immediate**: Confirmation email (needs to send right away)
- **Scheduled**: Reminder email (calculated for 24hrs before)
- **Periodic**: Cleanup tasks (daily + every 3 hours)

### RBAC Strategy
- Database: User.profile.role field (client/staff/admin)
- API: Custom permission classes check role
- Queryset filtering: Different views for different roles

---

## Usage Examples

### Create Reservation (Client)
```bash
POST /api/reservations/
{
  "room_id": 1,
  "check_in": "2026-02-01T14:00:00Z",
  "check_out": "2026-02-03T10:00:00Z"
}
```

Response:
```json
{
  "id": 1,
  "status": "confirmed",
  "room": {...},
  "check_in": "2026-02-01T14:00:00Z",
  "check_out": "2026-02-03T10:00:00Z",
  "created_at": "2026-01-17T...",
  "is_past_checkin": false,
  "is_past_checkout": false
}
```

### Check-in Guest (Staff)
```bash
POST /api/reservations/1/check_in/
```

### Check-out Guest (Staff)
```bash
POST /api/reservations/1/check_out/
```

### Cancel Reservation (Client/Staff/Admin)
```bash
POST /api/reservations/1/cancel/
```

---

## Testing

All 11 tests pass:
```bash
$ ./.venv/bin/python manage.py test reservations.tests
Ran 11 tests in 2.759s
OK
```

Test execution includes:
- Model validation
- API endpoint permissions
- Double booking prevention
- Async task mocking

---

## Running the System

### Development
```bash
# Terminal 1: Django
./.venv/bin/python manage.py runserver

# Terminal 2: Celery Worker
./.venv/bin/celery -A hotel worker -l info

# Terminal 3: Celery Beat
./.venv/bin/celery -A hotel beat -l info \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Docker
```bash
docker-compose up
```

---

## Files Modified/Created

| File | Type | Changes |
|------|------|---------|
| src/reservations/models.py | Modified | Added validation, statuses, properties |
| src/reservations/tasks.py | Modified | Enhanced tasks, added new ones |
| src/hotel/settings.py | Modified | Updated Celery Beat schedule |
| src/reservations/permissions.py | **New** | 6 permission classes for RBAC |
| src/reservations/serializers.py | Modified | Added validation, fields, methods |
| src/reservations/views.py | Modified | Complete RBAC + 4 new endpoints |
| src/reservations/tests.py | Modified | Added 11 comprehensive tests |
| src/reservations/migrations/0002_... | **New** | Database schema updates |
| RESERVATIONS_GUIDE.md | **New** | Complete feature documentation |

---

## Next Steps (Optional Future Enhancements)

1. **Notifications**: Send webhooks to external systems
2. **Analytics**: Track booking patterns and no-show rates
3. **Dynamic Pricing**: Adjust room prices based on occupancy
4. **Reviews**: Let clients rate stays and rooms
5. **Payments**: Integration with Stripe/payment gateway
6. **Multi-language**: Support email templates in multiple languages
7. **SMS Reminders**: Send SMS notifications in addition to email
8. **Cancellation Policies**: Implement refund rules and penalties

---

## Conclusion

The reservations system now provides:
- ✅ **Robust validation** preventing double-bookings
- ✅ **Async automation** for email notifications
- ✅ **Lifecycle management** through defined status transitions
- ✅ **Role-based security** with granular permissions
- ✅ **Comprehensive testing** ensuring reliability
- ✅ **Maintainable code** with clear architecture

The system is production-ready for a small-to-medium hotel with Redis/Celery infrastructure.
