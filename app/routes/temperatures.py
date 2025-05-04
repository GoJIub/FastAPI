from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/temperatures", response_model=List[schemas.Temperature])
def get_temperatures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка всех данных о температуре угля."""
    temperatures = db.query(models.Temperature).offset(skip).limit(limit).all()
    return temperatures

@router.get("/temperatures/date/{date_str}", response_model=List[schemas.Temperature])
def get_temperatures_by_date(date_str: date, db: Session = Depends(get_db)):
    """Получение данных о температуре угля на конкретную дату."""
    temperatures = db.query(models.Temperature).filter(models.Temperature.date == date_str).all()
    return temperatures

@router.get("/temperatures/warehouse/{warehouse_id}", response_model=List[schemas.Temperature])
def get_temperatures_by_warehouse(
    warehouse_id: int, 
    date_str: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Получение данных о температуре угля для конкретного склада."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    query = db.query(models.Temperature).filter(models.Temperature.warehouse_id == warehouse_id)
    
    if date_str:
        query = query.filter(models.Temperature.date == date_str)
    
    temperatures = query.all()
    return temperatures

@router.get("/temperatures/warehouse/{warehouse_id}/pile/{pile_id}", response_model=List[schemas.Temperature])
def get_temperatures_by_pile(
    warehouse_id: int, 
    pile_id: int,
    date_str: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Получение данных о температуре угля для конкретного штабеля."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    pile = db.query(models.Pile).filter(
        models.Pile.id == pile_id,
        models.Pile.warehouse_id == warehouse_id
    ).first()
    if not pile:
        raise HTTPException(status_code=404, detail=f"Штабель с ID {pile_id} не найден в складе {warehouse_id}")
    
    query = db.query(models.Temperature).filter(
        models.Temperature.warehouse_id == warehouse_id,
        models.Temperature.pile_id == pile_id
    )
    
    if date_str:
        query = query.filter(models.Temperature.date == date_str)
    
    temperatures = query.all()
    return temperatures

@router.post("/temperatures", response_model=schemas.Temperature)
def create_temperature(temperature: schemas.TemperatureCreate, db: Session = Depends(get_db)):
    """Создание новой записи о температуре угля."""
    # Проверяем существование склада и штабеля
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == temperature.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {temperature.warehouse_id} не найден")
    
    pile = db.query(models.Pile).filter(
        models.Pile.id == temperature.pile_id,
        models.Pile.warehouse_id == temperature.warehouse_id
    ).first()
    if not pile:
        raise HTTPException(status_code=404, detail=f"Штабель с ID {temperature.pile_id} не найден в складе {temperature.warehouse_id}")
    
    # Если указан picket_id, проверяем его существование
    if temperature.picket_id:
        picket = db.query(models.Picket).filter(
            models.Picket.id == temperature.picket_id,
            models.Picket.pile_id == temperature.pile_id
        ).first()
        if not picket:
            raise HTTPException(status_code=404, detail=f"Пикет с ID {temperature.picket_id} не найден в штабеле {temperature.pile_id}")
    
    db_temperature = models.Temperature(**temperature.dict())
    db.add(db_temperature)
    db.commit()
    db.refresh(db_temperature)
    
    return db_temperature 