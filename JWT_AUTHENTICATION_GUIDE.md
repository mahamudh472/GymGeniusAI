# JWT Authentication Guide

## Overview
This project now uses JWT (JSON Web Token) authentication with refresh token support and token blacklisting for secure logout functionality.

## Key Features Implemented

### 1. **Long-lived Refresh Tokens**
- Access tokens are valid for **60 minutes**
- Refresh tokens are valid for **30 days**
- Users stay logged in on their device until they explicitly logout

### 2. **Token Blacklisting**
- Tokens are blacklisted when users logout
- Old refresh tokens are automatically blacklisted when rotated
- Prevents replay attacks and unauthorized access

### 3. **Automatic Token Rotation**
- New refresh tokens are generated on each refresh
- Old tokens are automatically blacklisted for security

## API Endpoints

### Login
**Endpoint:** `POST /accounts/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Usage:**
- Store both tokens securely on the client (e.g., in secure storage, not localStorage for production)
- Use the `access` token in the Authorization header for API requests
- Use the `refresh` token to get new access tokens when they expire

---

### Refresh Token
**Endpoint:** `POST /accounts/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // New refresh token
}
```

**Usage:**
- Call this endpoint when the access token expires (401 Unauthorized)
- Store the new tokens returned
- The old refresh token is automatically blacklisted

---

### Logout
**Endpoint:** `POST /accounts/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

**Usage:**
- Send the refresh token in the request body
- The refresh token will be blacklisted and cannot be used again
- Clear stored tokens from the client

---

## Making Authenticated Requests

For all protected endpoints, include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Example with curl:
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     http://localhost:8000/accounts/profile/
```

Example with JavaScript (fetch):
```javascript
fetch('http://localhost:8000/accounts/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

---

## Client-Side Implementation Guide

### 1. **Login Flow**
```javascript
async function login(email, password) {
  const response = await fetch('/accounts/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Store tokens securely
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}
```

### 2. **Auto-Refresh on Token Expiry**
```javascript
async function makeAuthenticatedRequest(url, options = {}) {
  let accessToken = localStorage.getItem('access_token');
  
  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  };
  
  let response = await fetch(url, options);
  
  // If token expired, refresh it
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const refreshResponse = await fetch('/accounts/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (refreshResponse.ok) {
      const tokens = await refreshResponse.json();
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      // Retry original request with new token
      options.headers['Authorization'] = `Bearer ${tokens.access}`;
      response = await fetch(url, options);
    } else {
      // Refresh token invalid, redirect to login
      logout();
      window.location.href = '/login';
    }
  }
  
  return response;
}
```

### 3. **Logout Flow**
```javascript
async function logout() {
  const refreshToken = localStorage.getItem('refresh_token');
  const accessToken = localStorage.getItem('access_token');
  
  try {
    await fetch('/accounts/logout/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear tokens regardless of success
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
```

---

## Configuration Details

### JWT Settings (in `settings.py`)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),    # 30 days
    'ROTATE_REFRESH_TOKENS': True,                   # New token on refresh
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklist old token
    'UPDATE_LAST_LOGIN': True,                       # Update last_login field
}
```

**Customization:**
- Increase `REFRESH_TOKEN_LIFETIME` for longer sessions (e.g., 90 days)
- Decrease `ACCESS_TOKEN_LIFETIME` for more security (e.g., 15 minutes)
- Set `ROTATE_REFRESH_TOKENS` to `False` if you don't want token rotation

---

## Security Best Practices

### For Production:
1. **Store tokens securely:**
   - Mobile apps: Use secure storage (Keychain on iOS, KeyStore on Android)
   - Web apps: Use httpOnly cookies instead of localStorage to prevent XSS attacks

2. **Enable HTTPS:** Always use HTTPS in production to prevent token interception

3. **Implement CSRF protection** if using cookies

4. **Set shorter token lifetimes** for sensitive applications

5. **Monitor blacklisted tokens** and implement rate limiting on login/refresh endpoints

6. **Implement proper error handling** on the client to handle expired/invalid tokens

---

## Testing the Implementation

### 1. Test Login
```bash
curl -X POST http://localhost:8000/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/accounts/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### 3. Test Token Refresh
```bash
curl -X POST http://localhost:8000/accounts/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### 4. Test Logout
```bash
curl -X POST http://localhost:8000/accounts/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

---

## Troubleshooting

### Token Expired Error
**Error:** `Token is invalid or expired`
**Solution:** Use the refresh token endpoint to get a new access token

### Blacklisted Token Error
**Error:** `Token is blacklisted`
**Solution:** User has logged out. They need to login again

### Invalid Token Error
**Error:** `Given token not valid for any token type`
**Solution:** 
- Check if token is correctly formatted
- Ensure token hasn't been tampered with
- Verify the token hasn't expired

### Refresh Token Not Found
**Error:** `Token not found`
**Solution:** The refresh token may have expired (after 30 days). User needs to login again

---

## Migration Commands (Already Applied)

The following migrations have been applied to support token blacklisting:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates two new tables:
- `token_blacklist_outstandingtoken` - Tracks all issued tokens
- `token_blacklist_blacklistedtoken` - Stores blacklisted tokens

---

## Summary

✅ Users stay logged in for 30 days (or until they logout)
✅ Access tokens expire after 1 hour and auto-refresh transparently
✅ Logout properly blacklists tokens, preventing reuse
✅ Token rotation provides additional security
✅ Works seamlessly across devices when implemented correctly

For questions or issues, refer to the [Simple JWT documentation](https://django-rest-framework-simplejwt.readthedocs.io/).
