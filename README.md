# FastAPI: async vs sync with real numbers

A minimal demo that shows the practical difference between `async def`, `def`, and the most common async mistake in FastAPI with load test results to prove it.

## Three Endpoints

```python
# Worst: blocking call inside async def
@app.get("/async-blocking/")
async def async_blocking():
    time.sleep(3)  # this will freeze the entire event loop
    return {"message": "blocking call inside async def"}

# Acceptable: blocking call inside def
@app.get("/blocking/")
def blocking():
    time.sleep(3)  # FastAPI runs this in a threadpool
    return {"message": "blocking call inside def"}

# Best: non-blocking async
@app.get("/async/")
async def async_non_blocking():
    await asyncio.sleep(3)  # yields control back to event loop
    return {"message": "non-blocking async"}
```

## Load Test Results (100 concurrent users)

| Endpoint | RPS | Avg Response | Max Response | Requests Served | Full Report |
|---|---|---|---|---|---|
| `/async-blocking/` | 0.33 | 171s | 351s | 117 | [Locust HTML report](./docs/reports/async_blocking_report.html) |
| `/blocking/` | 13.27 | 7s | 9s | 640 | [Locust HTML report](./docs/reports/blocking_report.html) |
| `/async/` | **33.14** | **3s** | **3.1s** | **2000** | [Locust HTML report](./docs/reports/async_report.html) |


## What This Proves

**`async def` + `time.sleep()` (blocking call)**  freezes the event loop. Every request queues up serially. 100 users waiting = last user waits 351 seconds. This is worse than plain `def`.

**`def` + `time.sleep()` (sync endpoint)** FastAPI automatically runs `def` endpoints in a threadpool (~40 threads). Requests run concurrently up to thread limit, then queue. Acceptable for most use cases.

**`async def` + `await asyncio.sleep()` (non-blocking)** event loop handles all 100 users simultaneously. Every user gets a response in exactly 3 seconds regardless of concurrency. Best performance, zero degradation.

## The Rule

> Use `async def` only when every slow operation inside it is awaitable (`await db.query()`, `await httpx.get()`, etc.).
> If you have any blocking call, use `def` and let FastAPI's threadpool handle it.

---

## Setup

```bash
git clone https://github.com/aftabk-gh/fastapi-async-vs-sync.git
cd fastapi-async-vs-sync

# install uv if you don't have it
pip install uv

uv venv
source .venv/bin/activate
uv pip install fastapi uvicorn locust
```
### Run the server

```bash
uvicorn main:app --reload
```

## Run load tests

```bash
locust -f locustfile.py
```

Open `http://localhost:8089`, set host to `http://127.0.0.1:8000`, 100 users, ramp up 100.

Change the endpoint in `locustfile.py` to test each scenario.
