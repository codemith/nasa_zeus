#!/usr/bin/env python3

import sys
sys.path.append('.')

from auth.jwt_handler import get_password_hash, verify_password

def test_password_hashing():
    # Test passwords
    test_passwords = [
        "password123",
        "ZeusApp2024!",
        "testuser123"
    ]
    
    for password in test_passwords:
        print(f"\nTesting password: '{password}'")
        print(f"Length: {len(password)} characters, {len(password.encode('utf-8'))} bytes")
        
        try:
            # Hash the password
            hashed = get_password_hash(password)
            print(f"Hashed successfully: {hashed[:50]}...")
            
            # Verify the password
            is_valid = verify_password(password, hashed)
            print(f"Verification result: {is_valid}")
            
            # Test wrong password
            wrong_valid = verify_password("wrongpassword", hashed)
            print(f"Wrong password verification: {wrong_valid}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_password_hashing()