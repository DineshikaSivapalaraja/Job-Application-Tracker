import secrets

# This file use to generate a 32-byte (64-character hex) secure random key
secret_key = secrets.token_hex(32)
print(secret_key)