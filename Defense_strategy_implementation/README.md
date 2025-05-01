# Security Defense Implementation

A comprehensive security implementation demonstrating various defense mechanisms for web applications, specifically focused on protecting login systems and IoT dashboards.

## Features

### 1. Brute Force Protection
- Strict 3-attempt limit per account/IP combination
- 2-hour lockout period after exceeding attempt limit
- Complete form disable during lockout
- Automatic reset after lockout period

### 2. CSRF Protection
- Token-based CSRF protection
- Unique tokens per session
- Automatic token validation on form submissions
- Protection against cross-site request forgery attacks

### 3. Rate Limiting
- Request rate limiting per IP address
- Configurable window and request limits
- Protection against DoS attacks
- Automatic request tracking and limiting

### 4. Input Sanitization
- HTML escape for all user inputs
- Protection against XSS attacks
- Script tag removal
- Event handler sanitization

### 5. Security Headers
- Content Security Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

### 6. Multi-Factor Authentication (MFA)
- TOTP-based two-factor authentication
- QR code generation for easy setup
- Backup codes for account recovery
- Required for sensitive operations

### 7. JWT Session Management
- Secure session handling with JWT tokens
- Automatic token expiration
- Session validation on protected routes
- Protection against session hijacking

### 8. IoT-Specific Security
- Device authentication system
- Activity monitoring
- Data validation for IoT devices
- Secure device communication

## Technical Implementation

### Core Components

1. **SecurityDefenses Class**
```python
class SecurityDefenses:
    def __init__(self):
        self.failed_attempts = {}    # Track login attempts
        self.lockout_duration = 7200 # 2-hour lockout
        self.max_attempts = 3        # Maximum login attempts
        self.csrf_tokens = {}        # Store CSRF tokens
        self.mfa_secrets = {}        # Store MFA secrets
        self.backup_codes = {}       # Store backup codes
        self.user_sessions = {}      # Track active sessions
        self.session_duration = 3600 # 1-hour session duration
        self.setup_logging()
```

### Key Methods

1. **Brute Force Protection**
```python
def track_failed_attempt(self, username, ip)
def get_remaining_attempts(self, username, ip)
def is_account_locked(self, username, ip)
def get_lockout_time_remaining(self, username, ip)
```

2. **CSRF Protection**
```python
def generate_csrf_token(self)
def verify_csrf_token(self, token)
@csrf_protection  # Decorator
```

3. **Multi-Factor Authentication**
```python
def generate_mfa_secret(self)
def generate_backup_codes(self, count=8)
def get_totp_uri(self, username, secret)
def verify_totp(self, secret, token)
@require_mfa  # Decorator
```

4. **JWT Session Management**
```python
def generate_jwt_token(self, username)
def verify_jwt_token(self, token)
@require_secure_session  # Decorator
def cleanup_sessions(self)
```

## Usage

### Installation
1. Clone the repository
2. Install required dependencies:
```bash
pip install flask pyotp qrcode pyjwt
```

### Running the Application
```bash
python security_defenses_implementation.py
```

The server will start on https://127.0.0.1:5000 (with SSL if pyOpenSSL is installed)

### Demo Credentials
- Username: admin
- Password: SecurePass123!

## Security Features in Detail

### 1. Login Protection
- Tracks failed login attempts per username/IP combination
- Implements progressive security measures:
  1. First 2 attempts: Shows remaining attempts
  2. 3rd attempt: Triggers 2-hour lockout
  3. During lockout: Disables form completely
  4. After lockout: Resets attempt counter

### 2. Form Security
- CSRF token validation on all POST requests
- Input sanitization for all form fields
- Secure session management
- Protection against common web vulnerabilities

### 3. Multi-Factor Authentication
- TOTP-based authentication (compatible with Google Authenticator, Authy)
- QR code scanning for easy setup
- Secret key backup option
- One-time use backup codes for recovery
- Required for accessing protected routes

### 4. Secure Session Management
- JWT token-based authentication
- Automatic session expiration
- Session tracking and validation
- Periodic cleanup of expired sessions

### 5. IoT Device Security
- Unique device authentication tokens
- Activity monitoring and anomaly detection
- Data validation for device inputs
- Secure communication channels

## Implementation Details

### Login Form
```html
<form action="/login" method="POST">
    <input type="hidden" name="csrf_token" value="{csrf_token}">
    <input name="username" value="{username}" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
</form>
```

### Security Headers
```python
response.headers['Content-Security-Policy'] = "default-src 'self'"
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'SAMEORIGIN'
response.headers['X-XSS-Protection'] = '1; mode=block'
```

### MFA Implementation
```python
def setup_mfa():
    if not session.get('logged_in'): return redirect(url_for('index'))
    user = session['username']
    if user not in defenses.mfa_secrets:
        defenses.mfa_secrets[user] = defenses.generate_mfa_secret()
        defenses.backup_codes[user] = defenses.generate_backup_codes()
    secret = defenses.mfa_secrets[user]
    uri = defenses.get_totp_uri(user, secret)
    # Generate QR code and display setup page
```

### JWT Session Management
```python
def generate_jwt_token(self, username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'session_id': secrets.token_hex(16)
    }
    return jwt.encode(payload, app.secret_key, algorithm='HS256')
```

## Error Handling

### Types of Errors
1. **Authentication Errors**
   - Invalid credentials
   - Account lockout
   - Rate limiting
   - CSRF token mismatch
   - MFA verification failure

2. **Security Violations**
   - XSS attempts
   - CSRF attempts
   - Invalid input data
   - Unauthorized access attempts
   - Session manipulation attempts

### Error Messages
- Clear user feedback
- Non-revealing security information
- Proper error codes
- Guided user recovery

## Best Practices Implemented

1. **Password Security**
   - No password exposure in errors
   - Secure credential verification
   - Protection against timing attacks

2. **Session Security**
   - JWT-based secure session handling
   - Session timeout
   - Protection against session hijacking

3. **Input Validation**
   - Server-side validation
   - Input sanitization
   - Protection against injection attacks

4. **Multi-Factor Authentication**
   - TOTP-based verification
   - Backup codes for recovery
   - User-friendly setup process

5. **Security Logging**
   - Security event logging
   - Rotating log files
   - Audit trail of security events

## Testing

### Security Testing
1. Brute force attempt testing
2. CSRF protection testing
3. XSS attempt testing
4. MFA bypass testing
5. JWT token manipulation testing

### Test Cases
```python
# Example test case for brute force protection
def test_brute_force_protection():
    # Attempt login multiple times
    for i in range(4):
        response = client.post('/login', data={
            'username': 'test',
            'password': 'wrong'
        })
        if i < 3:
            assert 'attempts remaining' in response.data
        else:
            assert 'Locked' in response.data
```
