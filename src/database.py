from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    ip_address = Column(String)
    country_code = Column(String)
    abuse_confidence_score = Column(Integer)
    last_reported_at = Column(DateTime)
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine('sqlite:///alerts.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
