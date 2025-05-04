from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Базовые схемы

class WarehouseBase(BaseModel):
    name: str
    description: Optional[str] = None

class PileBase(BaseModel):
    name: str
    description: Optional[str] = None

class PicketBase(BaseModel):
    name: str
    position_x: Optional[float] = None
    position_y: Optional[float] = None

class TemperatureBase(BaseModel):
    value: float
    date: date
    
class FireBase(BaseModel):
    status: str
    date: date
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None

class WeatherBase(BaseModel):
    date: date
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    precipitation: Optional[float] = None

class SupplyBase(BaseModel):
    date: date
    quantity: float
    supplier: Optional[str] = None
    coal_type: Optional[str] = None

# Схемы для создания объектов

class WarehouseCreate(WarehouseBase):
    pass

class PileCreate(PileBase):
    warehouse_id: int

class PicketCreate(PicketBase):
    pile_id: int

class TemperatureCreate(TemperatureBase):
    warehouse_id: int
    pile_id: int
    picket_id: Optional[int] = None

class FireCreate(FireBase):
    warehouse_id: int
    pile_id: int

class WeatherCreate(WeatherBase):
    pass

class SupplyCreate(SupplyBase):
    warehouse_id: int

# Схемы для возврата объектов

class Picket(PicketBase):
    id: int
    pile_id: int
    
    class Config:
        orm_mode = True

class Pile(PileBase):
    id: int
    warehouse_id: int
    pickets: List[Picket] = []
    
    class Config:
        orm_mode = True

class Warehouse(WarehouseBase):
    id: int
    piles: List[Pile] = []
    
    class Config:
        orm_mode = True

class Temperature(TemperatureBase):
    id: int
    warehouse_id: int
    pile_id: int
    picket_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class Fire(FireBase):
    id: int
    warehouse_id: int
    pile_id: int
    warehouse_name: Optional[str] = None
    pile_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class Weather(WeatherBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class Supply(SupplyBase):
    id: int
    warehouse_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True 