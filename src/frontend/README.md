# Hotel Reservations Frontend

React-based frontend application for the Hotel Reservations management system.

## Features

- **Authentication & Authorization**: Login, register, and role-based access control
- **Client Role**: Browse rooms, create reservations, manage their bookings
- **Staff Role**: View all reservations, check-in/check-out guests, manage room status
- **Admin Role**: Complete system management - rooms, reservations, user management

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

```bash
cd src/frontend
npm install
```

### Running the Application

```bash
npm start
```

The application will open at `http://localhost:3000`

### Backend Requirements

The frontend expects the Django backend to be running at `http://localhost:8000`

### Build for Production

```bash
npm build
```

## Project Structure

```
src/
├── api/
│   ├── axiosConfig.js       # Axios configuration with interceptors
│   ├── authService.js        # Authentication API calls
│   ├── roomService.js        # Room management API calls
│   └── reservationService.js # Reservation API calls
├── components/
│   ├── Navigation.js         # Main navigation component
│   ├── ProtectedRoute.js     # Route protection with role checking
│   └── *.css                 # Component styles
├── pages/
│   ├── LoginPage.js          # Login page
│   ├── RegisterPage.js       # Registration page
│   ├── ClientDashboard.js    # Client dashboard
│   ├── StaffDashboard.js     # Staff dashboard
│   ├── AdminDashboard.js     # Admin dashboard
│   ├── RoomsPage.js          # Rooms listing
│   ├── RoomDetailPage.js     # Room details and editing
│   ├── CreateRoomPage.js     # Create new room
│   ├── ReservationsPage.js   # Reservations listing
│   ├── ReservationDetailPage.js  # Reservation details
│   ├── CreateReservationPage.js  # Create new reservation
│   └── *.css                 # Page styles
├── App.js                    # Main app component with routing
├── index.js                  # React entry point
└── index.css                 # Global styles
```

## API Integration

All API calls are made through service files in the `api/` directory. The `axiosConfig.js` automatically:
- Adds Bearer token to all requests
- Handles token refresh on 401 responses
- Redirects to login on auth failure

## Role-Based Features

### Client
- Browse available rooms
- Create reservations
- View and cancel their own reservations
- Track active and completed bookings

### Staff
- View all reservations
- Check-in guests
- Check-out guests
- View all rooms and their status
- See pending and checked-in reservations

### Admin
- Create, edit, and delete rooms
- Manage all reservations
- View system statistics
- See occupancy rates and room summaries

## Styling

Global styles are defined in `index.css` with component-specific styles in their respective CSS files. The application uses:
- CSS Grid and Flexbox for layouts
- Responsive design for mobile compatibility
- Color scheme: Blues (#2c3e50, #667eea) and accent colors for status indicators

## Demo Credentials

Test accounts are available on the login page:
- Client: `client1` / `password123`
- Staff: `staff1` / `password123`
- Admin: `admin` / `password123`
