from sqlalchemy import Column, String, Integer, DateTime, Boolean, text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class Snippet(Base):
    __tablename__ = 'snippets'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    code = Column(String, nullable=False)
    language = Column(String(50), nullable=False)
    description = Column(String)
    tags = Column(ARRAY(String), server_default='{}')
    is_public = Column(Boolean, server_default=text("false"))
    share_id = Column(String(12), unique=True, nullable=False)
    view_count = Column(Integer, server_default='0')
    star_count = Column(Integer, server_default='0')
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"), onupdate=text("NOW()"))

    user = relationship("User", back_populates="snippets")
    stars = relationship("Star", back_populates="snippet", cascade="all, delete-orphan")

# Add the GIN index for full-text search
Index(
    'snippets_search_idx',
    text("to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || code)"),
    postgresql_using='gin'
)
