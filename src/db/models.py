from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

from src.db.base import Base

class FilterGroup(Base):
    __tablename__ = "filter_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    keywords = relationship(
        "FilterKeyword",
        back_populates="group",
        cascade="all, delete-orphan",
    )

class FilterKeyword(Base):
    __tablename__ = "filter_keywords"

    id = Column(Integer, primary_key=True)
    group_id = Column(
        Integer,
        ForeignKey("filter_groups.id", ondelete="CASCADE"),
    )
    value = Column(String, nullable=False)

    group = relationship("FilterGroup", back_populates="keywords")

class MinusKeyword(Base):
    __tablename__ = "minus_keywords"

    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
