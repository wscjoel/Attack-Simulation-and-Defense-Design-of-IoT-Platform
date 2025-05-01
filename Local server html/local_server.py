import http.server
import socketserver
import os
import json
import random
import time
import uuid
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8000
SECRET_KEY = "your_secret_key_for_jwt_tokens"  # In production, use a proper secret key

# User credentials (for demo purposes only - in production, use a proper database)
USERS = {
    "admin": {
        "password": "password123",  # In production, store password hashes, not plaintext
        "role": "admin"
    },
    "user": {
        "password": "user123",
        "role": "user"
    }
}

# Base values for simulated sensors
base_values = {
    "temperature": 23.0,
    "humidity": 45.0,
    "pressure": 101.3,
    "illuminance": 500.0,
    "mq2": 150.0,
    "mq135": 80.0,
    "external_temp": 18.0
}


def get_random_change(base_value, max_change, min_value, max_value):
    """Generate a random change to a value (for realistic data trending)"""
    change = (random.random() * 2 - 1) * max_change
    new_value = base_value + change
    return max(min_value, min(max_value, new_value))


# Token management
def generate_token(username):
    """Generate a JWT-like token for authentication"""
    # Create a token with expiration time (24 hours)
    expiration = datetime.now() + timedelta(hours=24)
    payload = {
        "username": username,
        "role": USERS[username]["role"],
        "exp": int(expiration.timestamp())
    }

    # Convert payload to JSON and encode
    payload_json = json.dumps(payload)
    payload_b64 = base64.b64encode(payload_json.encode()).decode()

    # Create signature
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    # Return combined token
    return f"{payload_b64}.{signature}"


def verify_token(token):
    """Verify the token and return the payload if valid"""
    try:
        # Split token into parts
        parts = token.split('.')
        if len(parts) != 2:
            return None

        payload_b64, signature = parts

        # Verify signature
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if signature != expected_signature:
            return None

        # Decode payload
        payload_json = base64.b64decode(payload_b64).decode()
        payload = json.loads(payload_json)

        # Check expiration
        if payload.get("exp", 0) < datetime.now().timestamp():
            return None

        return payload
    except:
        return None


def generate_sensor_data():
    """Generate simulated sensor data"""
    global base_values

    # Update all base values with random changes
    base_values["temperature"] = get_random_change(base_values["temperature"], 0.5, 10, 35)
    base_values["humidity"] = get_random_change(base_values["humidity"], 2, 30, 90)
    base_values["pressure"] = get_random_change(base_values["pressure"], 0.2, 95, 105)
    base_values["illuminance"] = get_random_change(base_values["illuminance"], 50, 100, 2000)
    base_values["mq2"] = get_random_change(base_values["mq2"], 20, 50, 500)
    base_values["mq135"] = get_random_change(base_values["mq135"], 15, 30, 300)
    base_values["external_temp"] = get_random_change(base_values["external_temp"], 0.3, 5, 30)

    # Return a copy of the current values
    return dict(base_values)


class IoTServerHandler(http.server.SimpleHTTPRequestHandler):
    def authenticate_request(self):
        """Authenticate a request using token in Authorization header"""
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]  # Remove 'Bearer ' prefix
        return verify_token(token)

    def send_unauthorized(self):
        """Send a 401 Unauthorized response"""
        self.send_response(401)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "success": False,
            "message": "Unauthorized. Please log in."
        }).encode())

    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)

        # API endpoints that require authentication
        if parsed_url.path == '/api/sensor':
            # Check authentication for protected endpoints
            auth_payload = self.authenticate_request()
            if not auth_payload:
                self.send_unauthorized()
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Generate sensor data
            sensor_data = generate_sensor_data()

            # Log request with authenticated user
            print(f"[SENSOR DATA] User {auth_payload['username']} requested sensor data")

            # Send response
            self.wfile.write(json.dumps({
                "body": sensor_data
            }).encode())
            return

        elif self.path == '/':
            # Redirect to the login page
            self.send_response(302)
            self.send_header('Location', '/Login.html')
            self.end_headers()
            return

        # Serve files as usual
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'

        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            data = {}

        parsed_url = urlparse(self.path)

        # Login endpoint (no authentication required)
        if parsed_url.path == '/api/login':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            username = data.get('username', '')
            password = data.get('password', '')

            # Log login attempt (for Wireshark analysis)
            print(f"[LOGIN ATTEMPT] Username: {username}")

            # Check credentials
            if username in USERS and USERS[username]['password'] == password:
                # Generate token
                token = generate_token(username)

                # Log successful login
                print(f"[LOGIN SUCCESS] User {username} logged in")

                # Send success response with token
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "Login successful",
                    "token": token,
                    "username": username,
                    "role": USERS[username]['role']
                }).encode())
            else:
                # Log failed login
                print(f"[LOGIN FAILED] Invalid credentials for {username}")

                # Send error response
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "Invalid username or password"
                }).encode())
            return

        # Protected API endpoints that require authentication
        elif parsed_url.path == '/api/price':
            # Check authentication
            auth_payload = self.authenticate_request()
            if not auth_payload:
                self.send_unauthorized()
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Log the price update with user info
            if 'body' in data:
                try:
                    price_data = json.loads(data['body'])
                    print(
                        f"[PRICE UPDATE] User {auth_payload['username']} set banana price: ${price_data.get('price', 'unknown')}")
                except:
                    pass

            # Send success response
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Price updated successfully"
            }).encode())
            return

        elif parsed_url.path == '/api/buzzer':
            # Check authentication
            auth_payload = self.authenticate_request()
            if not auth_payload:
                self.send_unauthorized()
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Log the buzzer state with user info
            buzzer_state = data.get('buzzer', 'unknown')
            print(f"[BUZZER] User {auth_payload['username']} changed buzzer state to: {buzzer_state}")

            # Send success response
            self.wfile.write(json.dumps({
                "status": "success",
                "message": f"Buzzer turned {buzzer_state}"
            }).encode())
            return

        # Unknown POST endpoint
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "message": "Unknown endpoint"
        }).encode())

    def log_message(self, format, *args):
        """Custom logging with timestamp"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


if __name__ == "__main__":
    # Create the server
    with socketserver.TCPServer(("", PORT), IoTServerHandler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        print(f"Login page: http://localhost:{PORT}/Login.html")
        print(f"Dashboard: http://localhost:{PORT}/LocalDashboard.html (requires login)")
        print(f"API endpoints:")
        print(f"  - POST /api/login (public)")
        print(f"  - GET  /api/sensor (protected)")
        print(f"  - POST /api/price (protected)")
        print(f"  - POST /api/buzzer (protected)")
        print(f"\nTest credentials:")
        print(f"  Username: admin, Password: password123")
        print(f"  Username: user, Password: user123")

        # Serve until keyboard interrupt
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutdown.")
            http