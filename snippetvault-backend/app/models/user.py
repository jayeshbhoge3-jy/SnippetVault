from sqlalchemy import Column, String, Integer, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    github_id = Column(String, unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255))
    avatar_url = Column(String)
    bio = Column(String)
    plan = Column(String(20), server_default='free')
    snippets_count = Column(Integer, server_default='0')
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"), onupdate=text("NOW()"))

    snippets = relationship("Snippet", back_populates="user", cascade="all, delete-orphan")
    stars = relationship("Star", back_populates="user", cascade="all, delete-orphan")
