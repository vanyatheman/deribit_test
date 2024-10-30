import aiohttp
import asyncio
import time
import ssl
import certifi
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TickerData

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

ssl_context = ssl.create_default_context(cafile=certifi.where())

async def fetch_price(session: aiohttp.ClientSession, ticker):
    url = f"https://deribit.com/api/v2/public/get_index_price?index_name={ticker}"
    async with session.get(url, ssl=ssl_context) as response:
        data = await response.json()
        return data['result']['index_price']


async def save_price(ticker, price):
    async with SessionLocal() as session:
        async with session.begin():
            session.add(TickerData(
                ticker=ticker,
                price=price,
                timestamp=int(time.time())
            ))


async def fetch_and_save_prices():
    async with aiohttp.ClientSession() as session:
        while True:
            for ticker in ["btc_usd", "eth_usd"]:
                price = await fetch_price(session, ticker)
                print(price, ticker)
                await save_price(ticker, price)
            await asyncio.sleep(10)


async def get_prices(ticker):
    async with aiohttp.ClientSession() as session:
        url = f"https://deribit.com/api/v2/public/get_index_price?index_name={ticker}"
        async with session.get(url, ssl=ssl_context) as response:
            ticker_json = await response.json()
            print(f"{ticker}: {ticker_json['result']['index_price']}")

async def main(tickers_):
    tasks = []
    for ticker in tickers_:
        tasks.append(asyncio.create_task(get_prices(ticker)))

    for task in tasks:
        await task


if __name__ == "__main__":
    tickers = ["btc_usd", "eth_usd"]
    asyncio.run(fetch_and_save_prices())
