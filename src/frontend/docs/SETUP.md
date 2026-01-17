# Hotel Frontend Setup & Installation Guide

This guide will help you set up and run the React frontend for the Hotel Reservations system.

## 📋 Prerequisites

- **Node.js** (v14 or higher) - [Download](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Backend running** at `http://localhost:8000` (Django development server)

## 🚀 Quick Start

### Step 1: Navigate to Frontend Directory

```bash
cd src/frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install all required packages listed in `package.json`:
- React 18.3.1
- React Router DOM 6.22.0
- Axios 1.6.5
- date-fns 3.0.0
- React Scripts 5.0.1

### Step 3: Start Development Server

```bash
npm start
```

The application will automatically open at `http://localhost:3000`

## 🔧 Configuration

### Backend URL

By default, the frontend connects to `http://localhost:8000/api`. If your backend runs on a different URL, update the API base URL in:

**File:** `src/api/axiosConfig.js`
```javascript
const API_BASE_URL = 'http://localhost:8000/api'; // Change this if needed
```

Or create a `.env` file:
```
REACT_APP_API_URL=http://your-backend-url/api
```

## 📝 Available Scripts

```bash
# Start development server (watches for changes)
npm start

# Create production build
npm run build

# Run tests
npm test

# Eject configuration (⚠️ irreversible)
npm run eject
```

## 🔐 Authentication

The frontend uses JWT (JSON Web Tokens) for authentication:

1. **Login/Register** at the auth pages
2. **Token Storage**: Access token stored in `localStorage`
3. **Auto Token Refresh**: Automatically refreshes expired tokens
4. **Auto Logout**: Redirects to login on token expiration

### Demo Accounts

Use these credentials to test different roles:

| Role | Username | Password |
|------|----------|----------|
| Client | client1 | password123 |
| Staff | staff1 | password123 |
| Admin | admin | password123 |

## 🎯 Features by Role

### Client Dashboard
- Browse available rooms
- Create reservations
- View and manage their reservations
- Cancel bookings
- Track booking history

### Staff Dashboard
- View all reservations
- Check-in guests
- Check-out guests
- Monitor room status
- See pending check-ins

### Admin Dashboard
- Full system overview
- Room management (create, edit, delete)
- Reservation management
- Occupancy analytics
- System statistics

## 📂 Project Structure

```
src/frontend/
├── public/
│   └── index.html              # HTML entry point
├── src/
│   ├── api/
│   │   ├── axiosConfig.js      # HTTP client setup
│   │   ├── authService.js      # Auth API
│   │   ├── roomService.js      # Room API
│   │   └── reservationService.js  # Reservation API
│   ├── components/
│   │   ├── Navigation.js       # Header/nav
│   │   ├── ProtectedRoute.js   # Route protection
│   │   └── *.css
│   ├── pages/
│   │   ├── LoginPage.js
│   │   ├── ClientDashboard.js
│   │   ├── StaffDashboard.js
│   │   ├── AdminDashboard.js
│   │   ├── RoomsPage.js
│   │   ├── ReservationsPage.js
│   │   └── *.css
│   ├── App.js                  # Main app & routing
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
├── package.json                # Dependencies
├── .env.example                # Environment template
└── README.md                   # Frontend README
```

## 🌐 API Endpoints Used

The frontend communicates with these backend endpoints:

**Authentication:**
- `POST /auth/register/` - Register new user
- `POST /auth/token/` - Get JWT tokens
- `POST /auth/token/refresh/` - Refresh access token

**Rooms:**
- `GET /rooms/` - List all rooms
- `GET /rooms/{id}/` - Room details
- `POST /rooms/` - Create room (admin only)
- `PUT /rooms/{id}/` - Update room (admin only)
- `DELETE /rooms/{id}/` - Delete room (admin only)

**Reservations:**
- `GET /reservations/` - List reservations
- `GET /reservations/{id}/` - Reservation details
- `POST /reservations/` - Create reservation
- `POST /reservations/{id}/check_in/` - Check-in (staff/admin)
- `POST /reservations/{id}/check_out/` - Check-out (staff/admin)
- `POST /reservations/{id}/cancel/` - Cancel (client/staff/admin)

## 🎨 Styling

The application uses:
- **CSS Grid & Flexbox** for layouts
- **Responsive design** for mobile/tablet/desktop
- **Color scheme**: Professional blues with status indicators
- **Global styles** in `index.css`
- **Component styles** in individual CSS files

## 🚨 Troubleshooting

### Issue: "Cannot connect to backend"
**Solution**: Ensure Django backend is running on `http://localhost:8000`
```bash
# In backend directory
./.venv/bin/python manage.py runserver
```

### Issue: "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org/

### Issue: Port 3000 already in use
**Solution**: The app will prompt you to use a different port, or kill the process:
```bash
# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: "Module not found" errors
**Solution**: Reinstall dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: 401 Unauthorized errors
**Solution**: This might happen after token expiration. The app auto-redirects to login. If persistent:
1. Clear browser localStorage: `localStorage.clear()` in console
2. Log back in

## 📦 Building for Production

Create an optimized production build:

```bash
npm run build
```

This creates a `build/` directory with:
- Minified JavaScript
- Optimized assets
- Static HTML

Deploy the `build/` folder to your hosting service.

## 🔗 Running Frontend & Backend Together

**Terminal 1 - Backend:**
```bash
cd /workspaces/hotel-backend
./install.sh
./.venv/bin/python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd /workspaces/hotel-backend/src/frontend
npm install
npm start
```

Both should now be running:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [React Router Docs](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)
- [JWT Introduction](https://jwt.io/introduction)

## 💡 Tips

1. **Use React Developer Tools** browser extension for debugging
2. **Check Network tab** in DevTools to inspect API calls
3. **Test with multiple roles** to see different features
4. **Responsive testing** using DevTools device emulation
5. **Clear cache** with Ctrl+Shift+Delete if styles aren't updating

## 🐛 Need Help?

- Check the backend logs for API errors
- Open browser console (F12) for JavaScript errors
- Network tab to see API request/response details
- Ensure `CORS` is properly configured in Django settings
