from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import fires, temperatures, weather, warehouses
from app.database import Base, engine

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coal Calendar API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшне замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(fires.router, prefix="/api", tags=["fires"])
app.include_router(temperatures.router, prefix="/api", tags=["temperatures"])
app.include_router(weather.router, prefix="/api", tags=["weather"])
app.include_router(warehouses.router, prefix="/api", tags=["warehouses"])

@app.get("/api/test")
def test_api():
    return {"status": "ok", "message": "API работает корректно"}