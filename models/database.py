from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import uuid

# SQLite database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./nasa_zeus.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    alerts = relationship("UserAlert", back_populates="user")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    health_profile = Column(String, default="general")  # general, sensitive, high_risk
    alert_threshold = Column(Integer, default=3)  # AQI level 1-5
    location_lat = Column(Float, default=33.7490)  # Atlanta coordinates
    location_lon = Column(Float, default=-84.3880)
    email_notifications = Column(Boolean, default=True)
    
    # Relationship
    user = relationship("User", back_populates="preferences")

class UserAlert(Base):
    __tablename__ = "user_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # current, sustained, rapid_change
    severity = Column(String, nullable=False)  # info, warning, danger
    message = Column(Text, nullable=False)
    aqi_data = Column(Text)  # JSON string of AQI data
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="alerts")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)