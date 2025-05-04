from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/weather", response_model=List[schemas.Weather])
def get_all_weather(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка всех погодных данных."""
    weather_data = db.query(models.Weather).offset(skip).limit(limit).all()
    return weather_data

@router.get("/weather/date/{date_str}", response_model=schemas.Weather)
def get_weather_by_date(date_str: date, db: Session = Depends(get_db)):
    """Получение погодных данных на конкретную дату."""
    weather_data = db.query(models.Weather).filter(models.Weather.date == date_str).first()
    if not weather_data:
        raise HTTPException(status_code=404, detail=f"Погодные данные на дату {date_str} не найдены")
    return weather_data

@router.get("/weather/month/{year}/{month}", response_model=List[schemas.Weather])
def get_weather_by_month(year: int, month: int, db: Session = Depends(get_db)):
    """Получение погодных данных за указанный месяц."""
    # Определяем первый и последний день месяца
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Месяц должен быть от 1 до 12")
    
    start_date = date(year, month, 1)
    # Определяем последний день месяца
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    weather_data = db.query(models.Weather).filter(
        models.Weather.date >= start_date,
        models.Weather.date <= end_date
    ).all()
    
    return weather_data

@router.get("/weather/range", response_model=List[schemas.Weather])
def get_weather_by_range(start: date, end: date, db: Session = Depends(get_db)):
    """Получение погодных данных за указанный период."""
    weather_data = db.query(models.Weather).filter(
        models.Weather.date >= start,
        models.Weather.date <= end
    ).all()
    
    return weather_data

@router.post("/weather", response_model=schemas.Weather)
def create_weather(weather: schemas.WeatherCreate, db: Session = Depends(get_db)):
    """Создание новой записи о погоде."""
    # Проверяем, нет ли уже данных на эту дату
    existing_weather = db.query(models.Weather).filter(models.Weather.date == weather.date).first()
    if existing_weather:
        raise HTTPException(status_code=400, detail=f"Погодные данные на дату {weather.date} уже существуют")
    
    db_weather = models.Weather(**weather.dict())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    
    return db_weather 