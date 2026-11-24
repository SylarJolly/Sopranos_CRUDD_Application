from sqlalchemy import Column, Integer, String

from app.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    actor = Column(String, index=True)
    role = Column(Integer)
    status = Column(String)
    first_season = Column(Integer)
    last_season = Column(Integer)