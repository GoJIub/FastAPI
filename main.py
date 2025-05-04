from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import pandas as pd
from pydantic import BaseModel
from table_for_predicting import processing_work_table

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://web-production-da33.up.railway.app"],  # Укажи домен фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL базы данных (из Railway)
DATABASE_URL = "postgresql://postgres:ZEcOwNDTbOQDjLHchZKyhEOeEOfnEcFW@switchyard.proxy.rlwy.net:44380/railway"  # Замени на свои данные

# Твои функции
def save_dataframe_to_db(csv_file_path, table_name, db_url):
    df = pd.read_csv(csv_file_path)
    engine = create_engine(db_url)
    df.to_sql(table_name, engine, if_exists='replace', index=False)

def create_work_table(db_url):
    engine = create_engine(db_url)
    df = processing_work_table(engine)
    df = df.astype(str)
    table_name = 'working_table'
    with engine.connect() as connection:
        connection.execute(text(f'DROP TABLE IF EXISTS {table_name};'))
    df.to_sql(table_name, engine, if_exists='replace', index=False)

# Pydantic модель для валидации
class CsvInput(BaseModel):
    table_name: str

# Эндпоинт для получения прогнозов
@app.get("/api/forecast")
async def get_forecast(warehouse_id: int = None, pile_id: int = None):
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM working_table"
        conditions = []
        if warehouse_id:
            conditions.append(f"warehouse_id = {warehouse_id}")
        if pile_id:
            conditions.append(f"pile_id = {pile_id}")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        df = pd.read_sql(query, engine)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

# Эндпоинт для создания working_table
@app.post("/api/create-work-table")
async def create_work_table_endpoint():
    try:
        create_work_table(DATABASE_URL)
        return {"message": "Working table created successfully"}
    except Exception as e:
        return {"error": str(e)}

# Эндпоинт для загрузки CSV
@app.post("/api/upload-csv")
async def upload_csv(table_name: str, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        engine = create_engine(DATABASE_URL)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        return {"message": f"CSV uploaded to {table_name} successfully"}
    except Exception as e:
        return {"error": str(e)}

# Эндпоинт для получения складов и штабелей
@app.get("/api/warehouses")
async def get_warehouses():
    try:
        engine = create_engine(DATABASE_URL)
        # Предполагаем, что есть таблица warehouses с полями id, name
        warehouses_df = pd.read_sql("SELECT id, name FROM warehouses", engine)
        warehouses = warehouses_df.to_dict(orient="records")
        # Для каждого склада добавляем штабели
        for warehouse in warehouses:
            piles_df = pd.read_sql(f"SELECT id, name FROM piles WHERE warehouse_id = {warehouse['id']}", engine)
            warehouse["piles"] = piles_df.to_dict(orient="records")
        return warehouses
    except Exception as e:
        return {"error": str(e)}

# Тестовый эндпоинт
@app.get("/")
async def root():
    return {"message": "FastAPI backend is running"}