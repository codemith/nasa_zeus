#!/usr/bin/env python3
"""
Quick script to create a test user in the NASA Zeus database
Run this inside the backend container or with access to the database
"""
import sys
sys.path.append('/app')

from models.database import SessionLocal, User, UserPreferences
from auth.jwt_handler import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@nasa-zeus.com").first()
        if existing_user:
            print(f"✅ User already exists: test@nasa-zeus.com (ID: {existing_user.id})")
            return
        
        # Create new user
        user = User(
            email="test@nasa-zeus.com",
            name="Test User",
            password_hash=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Created user: test@nasa-zeus.com (ID: {user.id})")
        
        # Create default preferences for NYC
        preferences = UserPreferences(
            user_id=user.id,
            location_lat=40.7128,
            location_lon=-74.0060,
            health_profile="general",
            alert_threshold=3  # Alert when AQI >= 3 (Unhealthy for Sensitive Groups)
        )
        db.add(preferences)
        db.commit()
        
        print("✅ Created user preferences (NYC, General profile, Threshold: 3)")
        print("\n📋 Login Credentials:")
        print("   Email: test@nasa-zeus.com")
        print("   Password: password123")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
