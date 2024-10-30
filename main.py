import asyncio
import uvicorn
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import TickerData
from schemas import TickerDataSchema
from deribit_client import SessionLocal, fetch_and_save_prices

from typing import List, Optional

app = FastAPI()

async def get_db():
    async with SessionLocal() as session:
        yield session

# @app.get("/prices", response_model=List[TickerDataSchema])
# async def get_prices(ticker: str = None, db: AsyncSession = Depends(get_db)):
#     query = select(TickerData)
#     if ticker:
#         query = query.filter(TickerData.ticker == ticker)
#     result = await db.execute(query)
#     return result.scalars().all()

# Получение всех сохраненных данных по указанной валюте
@app.get("/prices/all", response_model=List[TickerDataSchema])
async def get_all_prices(
    ticker: str = Query(..., description="Обязательный параметр тикера"),
    db: AsyncSession = Depends(get_db)
):
    query = select(TickerData).where(TickerData.ticker == ticker)
    result = await db.execute(query)
    prices = result.scalars().all()
    if not prices:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    return prices

# Получение последней цены валюты
@app.get("/prices/latest", response_model=TickerDataSchema)
async def get_latest_price(
    ticker: str = Query(..., description="Обязательный параметр тикера"),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(TickerData)
        .where(TickerData.ticker == ticker)
        .order_by(TickerData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(query)
    latest_price = result.scalar_one_or_none()
    if latest_price is None:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    return latest_price

# Получение цены валюты с фильтром по дате
@app.get("/prices/by_date", response_model=List[TickerDataSchema])
async def get_prices_by_date(
    ticker: str = Query(..., description="Обязательный параметр тикера"),
    start_date: Optional[int] = Query(None, description="Начальная дата в формате timestamp"),
    end_date: Optional[int] = Query(None, description="Конечная дата в формате timestamp"),
    db: AsyncSession = Depends(get_db)
):
    query = select(TickerData).where(TickerData.ticker == ticker)
    if start_date is not None:
        query = query.where(TickerData.timestamp >= start_date)
    if end_date is not None:
        query = query.where(TickerData.timestamp <= end_date)
    result = await db.execute(query)
    prices = result.scalars().all()
    if not prices:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    return prices

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
    asyncio.run(fetch_and_save_prices())
