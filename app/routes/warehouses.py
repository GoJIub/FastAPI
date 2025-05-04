from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/warehouses", response_model=List[schemas.Warehouse])
def get_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка всех складов."""
    warehouses = db.query(models.Warehouse).offset(skip).limit(limit).all()
    return warehouses

@router.get("/warehouses/{warehouse_id}", response_model=schemas.Warehouse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """Получение информации о конкретном складе."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    return warehouse

@router.post("/warehouses", response_model=schemas.Warehouse)
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    """Создание нового склада."""
    # Проверяем, нет ли склада с таким именем
    existing_warehouse = db.query(models.Warehouse).filter(models.Warehouse.name == warehouse.name).first()
    if existing_warehouse:
        raise HTTPException(status_code=400, detail=f"Склад с именем '{warehouse.name}' уже существует")
    
    db_warehouse = models.Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    
    return db_warehouse

@router.get("/warehouses/{warehouse_id}/piles", response_model=List[schemas.Pile])
def get_piles_by_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """Получение списка всех штабелей для склада."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    piles = db.query(models.Pile).filter(models.Pile.warehouse_id == warehouse_id).all()
    return piles

@router.get("/warehouses/{warehouse_id}/piles/{pile_id}", response_model=schemas.Pile)
def get_pile(warehouse_id: int, pile_id: int, db: Session = Depends(get_db)):
    """Получение информации о конкретном штабеле."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    pile = db.query(models.Pile).filter(
        models.Pile.id == pile_id,
        models.Pile.warehouse_id == warehouse_id
    ).first()
    if not pile:
        raise HTTPException(status_code=404, detail=f"Штабель с ID {pile_id} не найден в складе {warehouse_id}")
    
    return pile

@router.post("/warehouses/{warehouse_id}/piles", response_model=schemas.Pile)
def create_pile(warehouse_id: int, pile: schemas.PileCreate, db: Session = Depends(get_db)):
    """Создание нового штабеля."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    # Проверяем, совпадает ли warehouse_id в URL и в данных
    if pile.warehouse_id != warehouse_id:
        raise HTTPException(status_code=400, detail=f"ID склада в URL ({warehouse_id}) не соответствует ID в данных ({pile.warehouse_id})")
    
    db_pile = models.Pile(**pile.dict())
    db.add(db_pile)
    db.commit()
    db.refresh(db_pile)
    
    return db_pile

@router.get("/warehouses/{warehouse_id}/piles/{pile_id}/pickets", response_model=List[schemas.Picket])
def get_pickets_by_pile(warehouse_id: int, pile_id: int, db: Session = Depends(get_db)):
    """Получение списка всех пикетов для штабеля."""
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    
    pile = db.query(models.Pile).filter(
        models.Pile.id == pile_id,
        models.Pile.warehouse_id == warehouse_id
    ).first()
    if not pile:
        raise HTTPException(status_code=404, detail=f"Штабель с ID {pile_id} не найден в складе {warehouse_id}")
    
    pickets = db.query(models.Picket).filter(models.Picket.pile_id == pile_id).all()
    return pickets 