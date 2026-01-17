# Quick Start Guide - Hotel Frontend

## ⚡ 30-Second Setup

```bash
# 1. Go to frontend directory
cd src/frontend

# 2. Install packages
npm install

# 3. Start the app
npm start
```

That's it! App opens at `http://localhost:3000` ✅

## 🔑 Demo Login Credentials

```
Client   → username: client1    password: password123
Staff    → username: staff1     password: password123
Admin    → username: admin      password: password123
```

## 📍 What Each Role Can Do

### 👤 Client
```
✅ Browse rooms
✅ Make reservations
✅ View my reservations
✅ Cancel my reservations
```

### 👨‍💼 Staff
```
✅ View all reservations
✅ Check-in guests
✅ Check-out guests
✅ Manage rooms
```

### 🔐 Admin
```
✅ Create new rooms
✅ Edit/delete rooms
✅ Manage all reservations
✅ View system statistics
```

## 🗂️ File Guide

| File | Purpose |
|------|---------|
| `App.js` | Main app & routes |
| `api/authService.js` | Login/logout |
| `api/roomService.js` | Room operations |
| `api/reservationService.js` | Reservation operations |
| `pages/` | Page components |
| `components/Navigation.js` | Header/menu |
| `index.css` | Global styles |

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Cannot connect to backend" | Make sure Django runs on `:8000` |
| "Port 3000 in use" | Kill process: `lsof -i :3000` |
| "Module not found" | Run `npm install` again |
| "Blank page" | Check browser console (F12) |
| "401 errors" | Clear localStorage and login again |

## 🌐 API Base URL

**Default**: `http://localhost:8000/api`

**Change in**: `src/api/axiosConfig.js`
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## 📱 Responsive?

Yes! Works on:
- 📱 Mobile
- 📱 Tablet
- 💻 Desktop
- 🖥️ Large screens

## 🔒 How Security Works

1. User logs in
2. Backend gives JWT token
3. Token stored in localStorage
4. All requests include token
5. Token auto-refreshes
6. Auto-logout on expiration

## 💾 Build for Production

```bash
npm run build
```

Creates optimized `build/` folder for deployment.

## 📚 File Structure

```
src/frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/              (API calls)
│   ├── components/       (UI components)
│   ├── pages/            (Page components)
│   ├── App.js           (Main routing)
│   ├── index.js         (Entry point)
│   └── index.css        (Global styles)
└── package.json         (Dependencies)
```

## ✨ Available Scripts

```bash
npm start     # Dev server (localhost:3000)
npm build     # Production build
npm test      # Run tests
npm eject     # Advanced setup (⚠️ not reversible)
```

## 🎯 Next Steps

1. ✅ Run `npm install`
2. ✅ Run `npm start`
3. ✅ Try logging in
4. ✅ Test different roles
5. ✅ Explore features
6. ✅ Customize as needed

## 📞 Need Help?

Check these files:
- **Setup issues?** → Read `SETUP.md`
- **Features overview?** → Read `README.md`
- **Implementation details?** → Read `IMPLEMENTATION.md`
- **Backend problems?** → Check Django logs
- **JS errors?** → Open DevTools (F12)

## 🎉 You're All Set!

Your hotel management frontend is ready to go! 🏨

Questions? Check the documentation or Django backend logs.
