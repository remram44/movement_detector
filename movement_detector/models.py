from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Float, Integer, String, DateTime


Base = declarative_base()


class Detection(Base):
    __tablename__ = 'detections'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    deviation = Column(Float, nullable=True)
    changes = Column(Integer, nullable=True)
    image = Column(String, nullable=True)
    location = Column(String, nullable=True)
