from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    piles = relationship("Pile", back_populates="warehouse", cascade="all, delete-orphan")

class Pile(Base):
    __tablename__ = "piles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"))
    description = Column(String, nullable=True)
    
    warehouse = relationship("Warehouse", back_populates="piles")
    pickets = relationship("Picket", back_populates="pile", cascade="all, delete-orphan")
    temperatures = relationship("Temperature", back_populates="pile", cascade="all, delete-orphan")

class Picket(Base):
    __tablename__ = "pickets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    pile_id = Column(Integer, ForeignKey("piles.id", ondelete="CASCADE"))
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    
    pile = relationship("Pile", back_populates="pickets")
    temperatures = relationship("Temperature", back_populates="picket", cascade="all, delete-orphan")

class Temperature(Base):
    __tablename__ = "temperatures"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"))
    pile_id = Column(Integer, ForeignKey("piles.id", ondelete="CASCADE"))
    picket_id = Column(Integer, ForeignKey("pickets.id", ondelete="CASCADE"), nullable=True)
    value = Column(Float)
    date = Column(Date, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    pile = relationship("Pile", back_populates="temperatures")
    picket = relationship("Picket", back_populates="temperatures", nullable=True)

class Fire(Base):
    __tablename__ = "fires"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"))
    pile_id = Column(Integer, ForeignKey("piles.id", ondelete="CASCADE"))
    status = Column(String, index=True)  # fire, risk, safe
    date = Column(Date, index=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    warehouse = relationship("Warehouse")
    pile = relationship("Pile")

class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Supply(Base):
    __tablename__ = "supplies"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"))
    date = Column(Date, index=True)
    quantity = Column(Float)
    supplier = Column(String, nullable=True)
    coal_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    warehouse = relationship("Warehouse") 