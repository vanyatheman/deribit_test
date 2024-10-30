from sqlalchemy import Column, String, Float, Integer, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TickerData(Base):
    __tablename__ = "ticker_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
