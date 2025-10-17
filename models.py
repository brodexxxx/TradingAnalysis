from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class TradingRecord(Base):
    __tablename__ = 'trading_records'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    prediction = Column(String(50))  # e.g., 'buy', 'sell', 'hold'
    indicators = Column(String(500))  # JSON string of indicators

# Create engine and session
engine = create_engine('sqlite:///trading_analysis.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
