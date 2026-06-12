from sqlalchemy import Column, DateTime, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Star(Base):
    __tablename__ = 'stars'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    snippet_id = Column(UUID(as_uuid=True), ForeignKey("snippets.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=text("NOW()"))

    user = relationship("User", back_populates="stars")
    snippet = relationship("Snippet", back_populates="stars")

    __table_args__ = (
        UniqueConstraint('user_id', 'snippet_id', name='uix_user_snippet_star'),
    )
