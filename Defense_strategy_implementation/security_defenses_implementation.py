#!/usr/bin/env python3
from flask import Flask, request, make_response, session, redirect, url_for
from functools import wraps
import time
import hmac
import secrets
import pyotp
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timedelta
import jwt
import logging
from logging.handlers import RotatingFileHandler

# --- Security Definitions ---
class SecurityDefenses:
    def __init__(self):
        self.failed_attempts = {}
        self.lockout_duration = 7200  # 2 hours
        self.max_attempts = 3
        self.csrf_tokens = {}
        self.mfa_secrets = {}
        self.backup_codes = {}
        self.user_sessions = {}
        self.session_duration = 3600  # 1 hour
        self.setup_logging()
        self.valid_credentials = {'admin': 'SecurePass123!'}

    def setup_logging(self):
        self.logger = logging.getLogger('security_defenses')
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler('security.log', maxBytes=1e7, backupCount=5)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def track_failed_attempt(self, username, ip):
        key = f"{username}:{ip}"
        self.failed_attempts.setdefault(key, []).append(time.time())

    def get_remaining_attempts(self, username, ip):
        key = f"{username}:{ip}"
        attempts = self.failed_attempts.get(key, [])
        if attempts and time.time() - min(attempts) >= self.lockout_duration:
            self.failed_attempts[key] = []
            return self.max_attempts
        return self.max_attempts - len(attempts)

    def is_account_locked(self, username, ip):
        key = f"{username}:{ip}"
        attempts = self.failed_attempts.get(key, [])
        if len(attempts) < self.max_attempts:
            return False
        if time.time() - min(attempts) < self.lockout_duration:
            return True
        self.failed_attempts[key] = []
        return False

    def get_lockout_time_remaining(self, username, ip):
        key = f"{username}:{ip}"
        attempts = self.failed_attempts.get(key, [])
        if not attempts:
            return 0
        elapsed = time.time() - min(attempts)
        return int(max(0, self.lockout_duration - elapsed))

    def generate_csrf_token(self):
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']

    def verify_csrf_token(self, token):
        stored = session.get('csrf_token')
        return bool(token and stored and hmac.compare_digest(str(token), str(stored)))

    def csrf_protection(self, f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get('logged_in') and request.method == 'POST':
                token = request.form.get('csrf_token')
                if not self.verify_csrf_token(token):
                    return redirect(url_for('index', error='Invalid CSRF token.'))
            return f(*args, **kwargs)
        return wrapped

    def generate_mfa_secret(self):
        return pyotp.random_base32()

    def generate_backup_codes(self, count=8):
        return [secrets.token_hex(4).upper() for _ in range(count)]

    def get_totp_uri(self, username, secret):
        return pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name="IoT Dashboard")

    def verify_totp(self, secret, token):
        return pyotp.TOTP(secret).verify(token)

    def require_mfa(self, f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get('mfa_verified'):
                return redirect(url_for('verify_mfa'))
            return f(*args, **kwargs)
        return wrapped

    def generate_jwt_token(self, username):
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'session_id': secrets.token_hex(16)
        }
        return jwt.encode(payload, app.secret_key, algorithm='HS256')

    def verify_jwt_token(self, token):
        try:
            return jwt.decode(token, app.secret_key, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def require_secure_session(self, f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            token = request.cookies.get('session_token')
            payload = self.verify_jwt_token(token) if token else None
            if not payload or payload['session_id'] not in self.user_sessions:
                return redirect(url_for('index'))
            self.user_sessions[payload['session_id']] = time.time()
            return f(*args, **kwargs)
        return wrapped

    def cleanup_sessions(self):
        now = time.time()
        for sid, ts in list(self.user_sessions.items()):
            if now - ts > self.session_duration:
                del self.user_sessions[sid]

# Flask app setup
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
defenses = SecurityDefenses()

# Index & Login Routes
@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    error = request.args.get('error','')
    username = request.args.get('username','')
    csrf_token = defenses.generate_csrf_token()
    locked = defenses.is_account_locked(username, request.remote_addr) if username else False
    rem = defenses.get_remaining_attempts(username, request.remote_addr) if username else defenses.max_attempts
    lock_time = defenses.get_lockout_time_remaining(username, request.remote_addr) if locked else 0
    h,m = divmod(lock_time,3600)
    return f"""
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><title>Login</title>
<style>
 body{{font-family:sans-serif;background:#f3f4f6;padding:2rem;}}
 .container{{max-width:400px;margin:0 auto;background:#fff;padding:2rem;border-radius:8px;}}
 input{{width:100%;padding:0.5rem;margin-bottom:1rem;border:1px solid #ccc;border-radius:4px;}}
 button{{width:100%;padding:0.75rem;background:#2563eb;color:#fff;border:none;border-radius:4px;font-size:1rem;}}
 .error{{border-color:#dc2626;}}
 .msg-error{{background:#fee2e2;color:#b91c1c;padding:0.75rem;border-radius:4px;}}
 .msg-warning{{background:#fffbeb;color:#92400e;padding:0.75rem;border-radius:4px;}}
</style></head>
<body><div class='container'>
<h2>Login</h2>
<form action='/login' method='POST'>
  <input type='hidden' name='csrf_token' value='{csrf_token}'>
  <input name='username' value='{username}' placeholder='Username' class='{'error' if error else ''}' {'disabled' if locked else ''}>
  <input type='password' name='password' placeholder='Password' class='{'error' if error else ''}' {'disabled' if locked else ''}>
  <button type='submit' {'disabled' if locked else ''}>Login</button>
</form>
{f'<div class="msg-error">{error}</div>' if error else ''}
{f'<div class="msg-warning">{rem} attempts remaining</div>' if rem<defenses.max_attempts else ''}
<p style='margin-top:1rem;color:#6b7280;'>Demo credentials: admin / SecurePass123!</p>
</div></body></html>"""

@app.route('/login', methods=['POST'])
def login():
    username=request.form.get('username'); password=request.form.get('password')
    if not username or not password:
        return redirect(url_for('index', error='Missing credentials.'))
    if defenses.is_account_locked(username, request.remote_addr):
        lt=defenses.get_lockout_time_remaining(username, request.remote_addr);h,m=divmod(lt,3600)
        return redirect(url_for('index', error=f'Locked. Try {h}h {m}m', username=username))
    if defenses.valid_credentials.get(username)!=password:
        defenses.track_failed_attempt(username, request.remote_addr)
        return redirect(url_for('index', error='Invalid credentials', username=username))
    session['logged_in']=True;session['username']=username
    defenses.generate_csrf_token()
    token=defenses.generate_jwt_token(username);payload=defenses.verify_jwt_token(token)
    defenses.user_sessions[payload['session_id']]=time.time()
    return redirect(url_for('setup_mfa'))

# Dashboard Route
@app.route('/dashboard')
@defenses.require_secure_session
@defenses.require_mfa
def dashboard():
    return '<h1>Welcome to your Dashboard</h1>'

# Enhanced Setup MFA Route
@app.route('/setup_mfa')
def setup_mfa():
    if not session.get('logged_in'): return redirect(url_for('index'))
    user=session['username']
    if user not in defenses.mfa_secrets:
        defenses.mfa_secrets[user]=defenses.generate_mfa_secret()
        defenses.backup_codes[user]=defenses.generate_backup_codes()
    secret=defenses.mfa_secrets[user];uri=defenses.get_totp_uri(user,secret)
    qr=qrcode.QRCode(box_size=8,border=2);qr.add_data(uri);qr.make(fit=True)
    img=qr.make_image();buf=BytesIO();img.save(buf,format='PNG');qr_b64=base64.b64encode(buf.getvalue()).decode()
    codes_html=''.join(f'<div class="code">{c}</div>' for c in defenses.backup_codes[user])
    csrf_token=defenses.generate_csrf_token()
    return f"""
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><title>Setup MFA</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  body{{font-family:'Inter',sans-serif;background:#f3f4f6;padding:2rem;}}
  .card{{max-width:600px;margin:0 auto;background:#fff;padding:2rem;border-radius:8px;box-shadow:0 4px 8px rgba(0,0,0,0.05);}}
  .step{{display:flex;align-items:flex-start;margin-bottom:2rem;}}
  .step-number{{background:#2563eb;color:white;width:2rem;height:2rem;border-radius:50%;display:flex;justify-content:center;align-items:center;font-weight:500;margin-right:1rem;flex-shrink:0;}}
  .step-content{{flex:1;}}
  .step-title{{font-weight:500;margin-bottom:0.5rem;}}
  .qr-container{{background:white;padding:1rem;border:1px solid #e5e7eb;border-radius:6px;text-align:center;}}
  .secret{{background:#f9fafb;padding:0.75rem;border:1px dashed #d1d5db;border-radius:4px;margin-top:0.5rem;word-break:break-all;}}
  .backup-codes{{background:#fffbeb;padding:1.5rem;border:1px solid #fcd34d;border-radius:6px;margin:2rem 0;}}
  .backup-codes h3{{margin-top:0;color:#92400e;}}
  .codes-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1rem;}}
  .code{{background:white;padding:0.75rem;border:1px solid #e5e7eb;border-radius:4px;text-align:center;font-family:monospace;}}
  .warning{{background:#fee2e2;color:#b91c1c;padding:1rem;border-radius:6px;display:flex;align-items:center;gap:0.75rem;margin-bottom:2rem;}}
  button{{width:100%;padding:0.875rem;background:#2563eb;color:white;border:none;border-radius:4px;font-size:1rem;font-weight:500;cursor:pointer;}}
</style>
</head>
<body>
  <div class='card'>
    <h1>Setup Two-Factor Authentication</h1>
    <p>Enhance your account security with 2FA</p>

    <div class='step'>
      <div class='step-number'>1</div>
      <div class='step-content'>
        <div class='step-title'>Install an Authenticator App</div>
        <p>Download and install an authenticator app like Google Authenticator or Authy on your mobile device.</p>
      </div>
    </div>

    <div class='step'>
      <div class='step-number'>2</div>
      <div class='step-content'>
        <div class='step-title'>Scan QR Code</div>
        <p>Open your authenticator app and scan the QR code below.</p>
        <div class='qr-container'>
          <img src='data:image/png;base64,{qr_b64}' alt='QR Code'>
        </div>
        <p>Can’t scan the QR code? Use this secret key instead:</p>
        <div class='secret'>{secret}</div>
      </div>
    </div>

    <div class='step'>
      <div class='step-number'>3</div>
      <div class='step-content'>
        <div class='step-title'>Save Backup Codes</div>
        <p>Store these backup codes in a secure place. You’ll need them if you lose access to your authenticator app.</p>
        <div class='backup-codes'>
          <h3>Your Backup Codes</h3>
          <div class='codes-grid'>{codes_html}</div>
        </div>
      </div>
    </div>

    <div class='warning'>
      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8v4m0 4h.01"/><path strokeLinecap="round" strokeLinejoin="round" d="M19.07 4.93a10 10 0 11-14.14 14.14 10 10 0 0114.14-14.14z"/></svg>
      <span><strong>Important:</strong> Save your backup codes now! They won’t be shown again.</span>
    </div>

    <div class='step'>
      <div class='step-number'>4</div>
      <div class='step-content'>
        <div class='step-title'>Verify Setup</div>
        <p>Enter the 6-digit code from your authenticator app to complete the setup.</p>
        <form action='/verify_mfa_setup' method='POST'>
          <input type='hidden' name='csrf_token' value='{csrf_token}'>
          <input type='text' name='token' required pattern='\d{6}' maxlength='6' placeholder='Enter 6-digit code' autocomplete='off'>
          <button type='submit'>Verify and Enable 2FA</button>
        </form>
      </div>
    </div>

  </div>
</body>
</html>
"""

@app.route('/verify_mfa_setup', methods=['POST'])
@defenses.csrf_protection
def verify_mfa_setup():
    if not session.get('logged_in'): return redirect(url_for('index'))
    code = request.form.get('token')
    user = session['username']
    if defenses.verify_totp(defenses.mfa_secrets[user], code):
        session['mfa_verified'] = True
        return redirect(url_for('dashboard'))
    return redirect(url_for('setup_mfa'))

if __name__ == '__main__':
    try:
        import OpenSSL
        app.run(ssl_context='adhoc', host='0.0.0.0', port=5000)
    except ImportError:
        print("Warning: pyOpenSSL not installed; running without SSL")
        app.run(debug=True, host='0.0.0.0', port=5000)
