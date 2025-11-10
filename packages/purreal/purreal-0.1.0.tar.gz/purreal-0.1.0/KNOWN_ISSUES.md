# Known Issues

## Critical: Burst Load > max_connections Causes Timeouts

**Status:** Identified, Not Fixed  
**Severity:** High  
**Affects:** v0.1.0  

### Description

When burst load exceeds `max_connections` (e.g., 100 concurrent requests with 50 max connections), exactly `max_connections` tasks succeed and the rest timeout after `acquisition_timeout`.

### Symptoms

```
Burst: 100 concurrent queries, max_connections=50
Result: 50 succeed, 50 timeout after 30s
```

**Debug output:**
```
POOL DEBUG: Task Task-xxx TIMEOUT acquiring connection after 30.00s
```

### Root Cause

Waiter notification mechanism has a race condition when many tasks are waiting. Connections are released but waiting tasks are not properly notified, causing them to timeout instead of acquiring the released connections.

**Location:** `purreal/pooler.py` lines 526-531
```python
# Notify one waiter if any exist *after* pool state is updated
if self._connection_waiters:
    waiter_to_notify = self._connection_waiters.popleft()
    if not waiter_to_notify.done():
        waiter_to_notify.set_result(None)
```

### Workaround

**Option 1: Size pool for peak load**
```python
pool = SurrealDBConnectionPool(
    max_connections=100,  # Set to peak burst size
    ...
)
```

**Option 2: Limit concurrent requests**
```python
# Use semaphore to limit concurrency
semaphore = asyncio.Semaphore(50)  # Match max_connections

async def rate_limited_query():
    async with semaphore:
        async with pool.acquire() as conn:
            await conn.query(...)
```

**Option 3: Batch requests**
```python
# Instead of 100 concurrent
for batch in chunks(requests, 50):
    await asyncio.gather(*batch)
```

### Impact

- ✅ **Sustained load:** Works fine (continuous workers)
- ✅ **Moderate bursts:** OK if burst ≤ max_connections
- ❌ **Large bursts:** Fails if burst > max_connections
- ✅ **Sequential batches:** Works fine

### Scenarios Affected

1. API endpoints receiving sudden traffic spikes > pool size
2. Background job processing with large queue dumps
3. Load testing with concurrency > max_connections

### Scenarios NOT Affected

1. Web servers with gradual ramp-up
2. Continuous background workers
3. RPC services with connection limits
4. Applications using semaphores for rate limiting

### Recommended Configuration

```python
# For production, set max_connections to expected peak + 20%
expected_peak = 100
pool = SurrealDBConnectionPool(
    max_connections=int(expected_peak * 1.2),  # 120
    acquisition_timeout=15.0,  # Reduce timeout
    ...
)
```

### Fix Plan

1. Investigate waiter notification timing
2. Consider notifying ALL waiters instead of one
3. Add tests for burst > max_connections
4. Validate fix with burst_size=200, max_connections=50

### Testing

To reproduce:
```bash
# This will fail
python -c "
from purreal import SurrealDBConnectionPool
import asyncio

async def test():
    pool = SurrealDBConnectionPool(
        uri='ws://localhost:8000/rpc',
        credentials={'username': 'root', 'password': 'root'},
        namespace='test',
        database='test',
        max_connections=50,
        acquisition_timeout=30.0,
    )
    await pool.initialize()
    
    async def query(i):
        async with pool.acquire() as conn:
            await conn.query('RETURN 1')
    
    # 100 concurrent (2x pool size) - 50 will timeout
    tasks = [query(i) for i in range(100)]
    await asyncio.gather(*tasks, return_exceptions=True)
    await pool.close()

asyncio.run(test())
"
```

---

**Reported:** 2025-11-09  
**Tracked:** https://github.com/dyleeeeeeee/purreal/issues/XXX
