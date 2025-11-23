from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    museum_theme = Column(String, default="starry") # Personal museum theme
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    artifacts = relationship("Artifact", back_populates="creator")
    comments = relationship("Comment", back_populates="user")

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    short_description = Column(String)
    long_description = Column(Text)
    year = Column(String, nullable=True) # e.g. "1990", "Renaissance", "2025"
    era = Column(String, index=True, default="Modern") # Ancient, Medieval, Industrial, Modern, Future
    category = Column(String, index=True) # e.g. "Art", "Science"
    tags = Column(String, nullable=True) # Comma-separated tags
    media_type = Column(String) # "image", "video", "3d_model"
    media_url = Column(String) # URL or file path
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    
    # Personal Museum Placement
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=2.0)
    pos_z = Column(Float, default=0.0)
    rot_y = Column(Float, default=0.0)
    is_placed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="artifacts")
    comments = relationship("Comment", back_populates="artifact")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    artifact = relationship("Artifact", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"), primary_key=True)

