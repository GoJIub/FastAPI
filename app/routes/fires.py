from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime, timedelta
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/fires", response_model=List[schemas.Fire])
def get_fires(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка всех данных о возгораниях."""
    fires = db.query(models.Fire).offset(skip).limit(limit).all()
    return fires

@router.get("/fires/date/{date}", response_model=List[schemas.Fire])
def get_fires_by_date(date: date, db: Session = Depends(get_db)):
    """Получение данных о возгораниях на конкретную дату."""
    fires = db.query(models.Fire).filter(models.Fire.date == date).all()
    for fire in fires:
        # Добавляем названия складов и штабелей
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == fire.warehouse_id).first()
        if warehouse:
            fire.warehouse_name = warehouse.name
        
        pile = db.query(models.Pile).filter(models.Pile.id == fire.pile_id).first()
        if pile:
            fire.pile_name = pile.name
    
    return fires

@router.get("/fires/month/{year}/{month}", response_model=List[schemas.Fire])
def get_fires_by_month(year: int, month: int, db: Session = Depends(get_db)):
    """Получение данных о возгораниях за указанный месяц."""
    # Определяем первый и последний день месяца
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Месяц должен быть от 1 до 12")
    
    start_date = date(year, month, 1)
    # Определяем последний день месяца
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    fires = db.query(models.Fire).filter(
        models.Fire.date >= start_date,
        models.Fire.date <= end_date
    ).all()
    
    for fire in fires:
        # Добавляем названия складов и штабелей
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == fire.warehouse_id).first()
        if warehouse:
            fire.warehouse_name = warehouse.name
        
        pile = db.query(models.Pile).filter(models.Pile.id == fire.pile_id).first()
        if pile:
            fire.pile_name = pile.name
    
    return fires

@router.get("/fires/warehouse/{warehouse_id}", response_model=List[schemas.Fire])
def get_fires_by_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """Получение данных о возгораниях для конкретного склада."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    fires = db.query(models.Fire).filter(models.Fire.warehouse_id == warehouse_id).all()
    
    for fire in fires:
        fire.warehouse_name = warehouse.name
        
        pile = db.query(models.Pile).filter(models.Pile.id == fire.pile_id).first()
        if pile:
            fire.pile_name = pile.name
    
    return fires

@router.post("/fires", response_model=schemas.Fire)
def create_fire(fire: schemas.FireCreate, db: Session = Depends(get_db)):
    """Создание новой записи о возгорании."""
    # Проверяем существование склада и штабеля
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == fire.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {fire.warehouse_id} не найден")
    
    pile = db.query(models.Pile).filter(
        models.Pile.id == fire.pile_id,
        models.Pile.warehouse_id == fire.warehouse_id
    ).first()
    if not pile:
        raise HTTPException(status_code=404, detail=f"Штабель с ID {fire.pile_id} не найден в складе {fire.warehouse_id}")
    
    db_fire = models.Fire(**fire.dict())
    db.add(db_fire)
    db.commit()
    db.refresh(db_fire)
    
    db_fire.warehouse_name = warehouse.name
    db_fire.pile_name = pile.name
    
    return db_fire 