"""SQLAlchemy models for Ahrie AI database."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()


class User(Base):
    """User model for storing Telegram user information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="en")
    phone_number = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON, default=dict)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


class Conversation(Base):
    """Conversation model for tracking chat sessions."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    context = Column(JSON, default=dict)
    status = Column(String(50), default="active")  # active, archived, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_chat", "user_id", "chat_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Message(Base):
    """Message model for storing conversation messages."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"


class Clinic(Base):
    """Clinic model for storing medical clinic information."""
    
    __tablename__ = "clinics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    name_ko = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    description_ko = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    district = Column(String(100), nullable=True)
    city = Column(String(100), default="Seoul")
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    specialties = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    languages_supported = Column(JSON, default=list)
    halal_friendly = Column(Boolean, default=False)
    arabic_support = Column(Boolean, default=False)
    female_staff_available = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    price_range = Column(String(50), nullable=True)  # $, $$, $$$, $$$$
    operating_hours = Column(JSON, default=dict)
    images = Column(JSON, default=list)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    procedures = relationship("ClinicProcedure", back_populates="clinic")
    reviews = relationship("Review", back_populates="clinic")
    
    def __repr__(self) -> str:
        return f"<Clinic(id={self.id}, name={self.name}, rating={self.rating})>"


class Procedure(Base):
    """Procedure model for storing medical procedure information."""
    
    __tablename__ = "procedures"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    name_ar = Column(String(255), nullable=True)
    name_ko = Column(String(255), nullable=True)
    category = Column(String(100), nullable=False)  # face, body, skin, etc.
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    description_ko = Column(Text, nullable=True)
    duration_min = Column(Integer, nullable=True)  # in minutes
    duration_max = Column(Integer, nullable=True)
    recovery_days_min = Column(Integer, nullable=True)
    recovery_days_max = Column(Integer, nullable=True)
    anesthesia_type = Column(String(100), nullable=True)
    price_range_min = Column(Integer, nullable=True)  # in USD
    price_range_max = Column(Integer, nullable=True)
    risks = Column(JSON, default=list)
    benefits = Column(JSON, default=list)
    preparation_steps = Column(JSON, default=list)
    aftercare_steps = Column(JSON, default=list)
    images = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    clinics = relationship("ClinicProcedure", back_populates="procedure")
    reviews = relationship("Review", back_populates="procedure")
    
    def __repr__(self) -> str:
        return f"<Procedure(id={self.id}, name={self.name}, category={self.category})>"


class ClinicProcedure(Base):
    """Association table for clinics and procedures with pricing."""
    
    __tablename__ = "clinic_procedures"
    
    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    price_min = Column(Integer, nullable=True)
    price_max = Column(Integer, nullable=True)
    special_notes = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    clinic = relationship("Clinic", back_populates="procedures")
    procedure = relationship("Procedure", back_populates="clinics")
    
    # Indexes
    __table_args__ = (
        Index("idx_clinic_procedure", "clinic_id", "procedure_id"),
    )


class Review(Base):
    """Review model for storing user reviews of clinics and procedures."""
    
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=True)
    rating = Column(Float, nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)
    youtube_video_id = Column(String(50), nullable=True)
    youtube_channel = Column(String(255), nullable=True)
    source = Column(String(50), default="direct")  # direct, youtube, imported
    language = Column(String(10), default="en")
    sentiment_score = Column(Float, nullable=True)
    helpful_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    clinic = relationship("Clinic", back_populates="reviews")
    procedure = relationship("Procedure", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index("idx_clinic_rating", "clinic_id", "rating"),
        Index("idx_procedure_rating", "procedure_id", "rating"),
    )
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, rating={self.rating}, user_id={self.user_id})>"


class HalalPlace(Base):
    """Model for storing halal restaurants and facilities."""
    
    __tablename__ = "halal_places"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)  # restaurant, market, mosque
    cuisine = Column(String(100), nullable=True)
    certification = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    district = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    operating_hours = Column(JSON, default=dict)
    delivery_available = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_from_gangnam = Column(Float, nullable=True)  # in km
    rating = Column(Float, default=0.0)
    price_range = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self) -> str:
        return f"<HalalPlace(id={self.id}, name={self.name}, type={self.type})>"


class TranslationCache(Base):
    """Cache for storing translations to reduce API calls."""
    
    __tablename__ = "translation_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    translation_service = Column(String(50), default="google")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_translation_lookup", "source_language", "target_language", "source_text"),
    )
    
    def __repr__(self) -> str:
        return f"<TranslationCache(id={self.id}, {self.source_language}->{self.target_language})>"