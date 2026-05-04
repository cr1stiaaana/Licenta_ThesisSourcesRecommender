# Authentication Implementation

## Overview

Added optional user authentication that allows users to save their data persistently across sessions while still allowing guest usage.

## Features

### Guest Mode (Default)
- Users can search and browse without logging in
- Saved items stored in localStorage (browser-specific)
- Full functionality available without account

### Authenticated Mode
- Users can register/login to save data on server
- Saved items persist across devices and browsers
- Automatic migration of localStorage items to server after login
- Session-based authentication with Flask sessions

## Implementation Details

### Backend (Already Existed)
- `app/auth/user_store.py` - User management with SQLite
- Authentication routes:
  - `POST /auth/register` - Create new account
  - `POST /auth/login` - Login
  - `POST /auth/logout` - Logout
  - `GET /auth/me` - Check auth status
- Saved items routes:
  - `GET /saved` - Get user's saved items
  - `POST /saved` - Save an item
  - `DELETE /saved/<item_id>` - Remove saved item

### Frontend (New)

#### JavaScript (`static/app.js`)
- `checkAuthStatus()` - Check if user is logged in on page load
- `updateAuthUI()` - Show/hide login button vs user info
- `getSavedItems()` - Fetch from server if logged in, localStorage if guest
- `saveItem()` - Save to server if logged in, localStorage if guest
- `unsaveItem()` - Remove from server if logged in, localStorage if guest
- `migrateSavedItems()` - Move localStorage items to server after login
- Authentication modal handlers for login/register forms

#### HTML (`static/index.html`)
- Authentication button in header
- User info display (username + logout button)
- Authentication modal with:
  - Login form (username, password)
  - Register form (username, email, password)
  - Switch between login/register

#### CSS (`static/style.css`)
- Styles for auth buttons
- User info display
- Auth modal and forms
- Dark mode support for auth UI

## User Flow

### Guest User
1. Visit site → Can search immediately
2. Click "Save" on article → Saved to localStorage
3. Refresh page → Saved items still there (same browser)
4. Different browser → Saved items not available

### Registered User
1. Visit site → Can search immediately (no login required)
2. Click "Autentificare" → Login/Register modal appears
3. Register or login
4. Click "Save" on article → Saved to server
5. Refresh page → Saved items loaded from server
6. Different browser → Login → Saved items available

### Migration Flow
1. Guest saves 3 articles to localStorage
2. User registers/logs in
3. System automatically migrates 3 articles to server
4. localStorage cleared
5. All future saves go to server

## Security

- Passwords hashed with SHA-256 (backend)
- Session-based authentication with Flask sessions
- CSRF protection via Flask
- No sensitive data in localStorage
- Server validates all requests

## Database

### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
)
```

### Saved Items Table
```sql
CREATE TABLE saved_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    item_data TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, item_id)
)
```

## i18n Support

Added translations for:
- `btn_login` - "Autentificare" / "Login"
- `btn_register` - "Înregistrare" / "Register"
- `btn_logout` - "Deconectare" / "Logout"
- `login_title` - "Autentificare" / "Login"
- `register_title` - "Înregistrare" / "Register"
- `label_username` - "Nume utilizator" / "Username"
- `label_email` - "Email" / "Email"
- `label_password` - "Parolă" / "Password"
- `no_account` - "Nu ai cont?" / "Don't have an account?"
- `have_account` - "Ai deja cont?" / "Already have an account?"
- `register_link` - "Înregistrează-te" / "Register"
- `login_link` - "Autentifică-te" / "Login"

## Testing

### Manual Testing Steps

1. **Guest Mode**:
   - Search for "spec driven dev"
   - Save 2 articles
   - Refresh page → Articles still saved
   - Close browser → Reopen → Articles still saved

2. **Registration**:
   - Click "Autentificare"
   - Click "Înregistrează-te"
   - Fill form: username, email, password
   - Submit → Should see username in header

3. **Login**:
   - Logout
   - Click "Autentificare"
   - Enter credentials
   - Submit → Should see username in header

4. **Migration**:
   - Logout
   - Save 2 articles as guest (localStorage)
   - Login
   - Check saved items → Should see 2 articles
   - Logout and login again → Articles still there

5. **Cross-Device**:
   - Login on browser A
   - Save 3 articles
   - Login on browser B (same account)
   - Check saved items → Should see 3 articles

## Future Enhancements

- Password reset functionality
- Email verification
- Social login (Google, GitHub)
- User profile page
- Export saved items
- Collections/folders for saved items
- Sharing saved collections
- Search history (for logged-in users)
