
# Rubika Login Example

This is a simple example showing how to use the `rulog` Python library to:

1. Send a verification code to a phone number.
2. Login to Rubika using the received code.
3. Register the device.

---

## Installation

Make sure you have installed the `rulog` library:

```bash
pip install rulog
```

---

## Example Code

```python
from rulog import Client

# Create a Client instance
Client = Client()

# ===== Send code =====
def send_code(phone):
    try:
        # Try sending via Android platform with send_type=True
        response = Client.sendCode("android", phone, send_type=True)
        return response['data']['phone_code_hash']
    except Exception as e:
        print("❌ Android send failed. Trying Web...")
        try:
            response = Client.sendCode("web", phone)
            return response['data']['phone_code_hash']
        except Exception as e:
            print("❌ Sending code failed:", e)
            return None

# ===== Login =====
def login(phone, hash_code, code):
    try:
        response = Client.signIn("android", phone, hash_code, code)
        print("✅ Login successful.")
        return response
    except Exception as e:
        print("❌ Login failed:", e)
        return None

# ===== Register device =====
def register(auth, key):
    try:
        result = Client.register(platform="android", auths=auth, keys=key)
        if result:
            print("✅ Registration successful.")
            return True
        else:
            print("❌ Registration failed.")
            return False
    except Exception as e:
        print("❌ Registration error:", e)
        return False

# ===== Main execution =====
if __name__ == "__main__":
    phone = input("📱 Enter your phone number (e.g., 9891...): ").strip()

    hash_code = send_code(phone)
    if not hash_code:
        print("🚫 Code sending failed. Exiting.")
        exit()

    code = input("🔢 Enter the received code: ").strip()
    login_response = login(phone, hash_code, code)

    if login_response:
        register(login_response['Auth'], login_response['Key'])
```

---

### How it works

1. **Send code**: Sends a verification code to the phone using Android first, then Web if failed.
2. **Login**: Signs in using the phone number, hash code, and received code.
3. **Register**: Registers the device using the authentication keys received after login.

---

### Notes

- Ensure your phone number format is correct.
- The script handles simple retries for sending codes.
- The library `rulog` must be installed.