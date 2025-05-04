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
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],  # Укажи домен фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL базы данных (возьми из Railway)
DATABASE_URL = "postgresql://user:password@host:port/dbname"  # Замени на свои данные

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
async def get_forecast():
    try:
        engine = create_engine(DATABASE_URL)
        df = pd.read_sql("SELECT * FROM working_table", engine)
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

# Эндпоинт для загрузки CSV-файла
@app.post("/api/upload-csv")
async def upload_csv(table_name: str, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        engine = create_engine(DATABASE_URL)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        return {"message": f"CSV uploaded to {table_name} successfully"}
    except Exception as e:
        return {"error": str(e)}

# Тестовый эндпоинт
@app.get("/")
async def root():
    return {"message": "FastAPI backend is running"}