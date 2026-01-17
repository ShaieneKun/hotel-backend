Frontend - Hotel Reservations System
=====================================

Complete File Structure & Overview

📁 src/frontend/
│
├── 📄 package.json              - Project dependencies
├── 📄 README.md                 - Frontend overview
├── 📄 SETUP.md                  - Detailed setup guide
├── 📄 QUICKSTART.md             - Quick reference
├── 📄 IMPLEMENTATION.md         - Implementation summary
├── 📄 .env.example              - Environment template
├── 📄 .gitignore                - Git ignore rules
│
├── 📁 public/
│   └── 📄 index.html            - HTML template
│
└── 📁 src/
    │
    ├── 📄 index.js              - React entry point
    ├── 📄 index.css             - Global styles (colors, buttons, grids, etc.)
    ├── 📄 App.js                - Main app with routing
    │
    ├── 📁 api/                  - API Integration Layer
    │   ├── 📄 axiosConfig.js    - HTTP client setup, JWT handling, interceptors
    │   ├── 📄 authService.js    - Login, register, logout, token management
    │   ├── 📄 roomService.js    - Room CRUD operations
    │   └── 📄 reservationService.js - Reservation CRUD & actions
    │
    ├── 📁 components/           - Reusable UI Components
    │   ├── 📄 Navigation.js      - Header/navbar with role-based menu
    │   ├── 📄 Navigation.css     - Navbar styling
    │   ├── 📄 ProtectedRoute.js  - Route protection with role checking
    │   ├── 📄 AuthPages.css      - Auth pages styling (login/register)
    │   └── 📄 ErrorPages.css     - Error pages styling (403, etc)
    │
    └── 📁 pages/                - Page Components
        │
        ├── 📄 LoginPage.js              - Login form with credentials
        ├── 📄 RegisterPage.js           - Registration form
        ├── 📄 UnauthorizedPage.js       - 403 error page
        ├── 📄 AuthPages.css             - Styling for auth pages
        │
        ├── 📄 ClientDashboard.js        - Client dashboard & stats
        ├── 📄 StaffDashboard.js         - Staff dashboard & check-in/out
        ├── 📄 AdminDashboard.js         - Admin dashboard & analytics
        ├── 📄 DashboardPages.css        - Dashboard styling
        │
        ├── 📄 RoomsPage.js              - Rooms listing with filtering
        ├── 📄 RoomDetailPage.js         - Room details & edit (admin)
        ├── 📄 CreateRoomPage.js         - Create new room form (admin)
        ├── 📄 RoomPages.css             - Rooms styling
        │
        ├── 📄 ReservationsPage.js       - Reservations listing
        ├── 📄 ReservationDetailPage.js  - Reservation details & actions
        ├── 📄 CreateReservationPage.js  - Create reservation form
        └── 📄 ReservationPages.css      - Reservations styling


=== KEY FEATURES ===

🔐 Authentication
  • JWT-based login/registration
  • Token auto-refresh
  • Role-based access control
  • Auto-logout on expiration

👥 Three Roles
  📱 Client     - Browse rooms, make reservations
  👨‍💼 Staff     - Manage check-in/check-out, view reservations
  🔐 Admin      - Manage rooms and system

🏨 Room Management
  • Browse available rooms
  • Create/edit/delete rooms (admin)
  • Filter by status
  • Room details and capacity

📅 Reservation Management
  • Create reservations
  • Check-in/check-out guests (staff)
  • Cancel reservations
  • View reservation details

📊 Dashboards
  • Role-specific stats
  • Quick actions
  • System overview
  • Real-time data


=== API ENDPOINTS ===

Authentication:
  POST   /auth/register/
  POST   /auth/token/
  POST   /auth/token/refresh/

Rooms:
  GET    /rooms/
  GET    /rooms/{id}/
  POST   /rooms/
  PUT    /rooms/{id}/
  DELETE /rooms/{id}/

Reservations:
  GET    /reservations/
  GET    /reservations/{id}/
  POST   /reservations/
  POST   /reservations/{id}/check_in/
  POST   /reservations/{id}/check_out/
  POST   /reservations/{id}/cancel/


=== STYLING ===

Global Colors:
  Primary: #2c3e50 (dark blue)
  Accent:  #667eea (purple)
  Success: #27ae60 (green)
  Warning: #f39c12 (orange)
  Danger:  #e74c3c (red)

Responsive Breakpoints:
  Mobile:    320px - 767px
  Tablet:    768px - 1023px
  Desktop:   1024px+

Components:
  Cards, buttons, forms, tables, badges, alerts, grids


=== QUICK COMMANDS ===

Setup:
  cd src/frontend
  npm install
  npm start

Development:
  npm start           - Start dev server
  npm test            - Run tests
  npm run build       - Production build

Testing Accounts:
  Client   → client1 / password123
  Staff    → staff1 / password123
  Admin    → admin / password123


=== TROUBLESHOOTING ===

Port 3000 in use:
  lsof -i :3000
  kill -9 <PID>

Backend not connecting:
  • Ensure Django runs on :8000
  • Check CORS settings
  • Check API URL in axiosConfig.js

Module errors:
  rm -rf node_modules package-lock.json
  npm install

Clear cache:
  • LocalStorage: localStorage.clear()
  • Browser cache: Ctrl+Shift+Delete
  • React cache: npm cache clean --force


=== PRODUCTION ===

Build:
  npm run build

Deploy:
  • Upload 'build/' folder
  • Set backend URL
  • Configure CORS headers


=== FILES BY ROLE ===

CLIENT Features (ClientDashboard.js):
  ✅ View stats
  ✅ Browse rooms (RoomsPage.js)
  ✅ Make reservations (CreateReservationPage.js)
  ✅ View my reservations (ReservationsPage.js)
  ✅ Cancel reservations (ReservationDetailPage.js)

STAFF Features (StaffDashboard.js):
  ✅ View all reservations (ReservationsPage.js)
  ✅ Check-in guests (ReservationDetailPage.js)
  ✅ Check-out guests (ReservationDetailPage.js)
  ✅ View room status (RoomsPage.js)

ADMIN Features (AdminDashboard.js):
  ✅ View analytics
  ✅ Create rooms (CreateRoomPage.js)
  ✅ Edit rooms (RoomDetailPage.js)
  ✅ Delete rooms (RoomDetailPage.js)
  ✅ Manage reservations (ReservationsPage.js)


Ready to use! 🚀🏨
