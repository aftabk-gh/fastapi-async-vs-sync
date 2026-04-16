import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/async-blocking/")
async def async_blocking():
    time.sleep(3)
    return {"message": "blocking call inside async def"}


@app.get("/blocking/")
def blocking():
    time.sleep(3)
    return {"message": "blocking call inside def"}


@app.get("/async/")
async def async_non_blocking():
    await asyncio.sleep(3)
    return {"message": "non-blocking async"}
