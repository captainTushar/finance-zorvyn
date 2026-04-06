from app.services.auth_service import hash_password, verify_password

password = "Admin@123"
hashed = hash_password(password)
print(f"Original: {password}")
print(f"Hashed: {hashed}")
print(f"Verify result: {verify_password(password, hashed)}")
