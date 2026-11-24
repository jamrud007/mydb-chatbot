"""
Lightweight local concurrent load test (Day 13 — Uji beban ringan)

Hits unauthenticated endpoints with concurrent async requests and reports
latency percentiles + error rate. Uses httpx.AsyncClient + asyncio.gather —
async I/O generates concurrency far more cheaply than spawning OS threads,
so a modest local machine can still simulate dozens of simultaneous clients.

Usage:
    python scripts/load_test_local.py --base-url http://localhost:8000 --concurrency 20 --requests 200
"""
import argparse
import asyncio
import statistics
import time

import httpx

ENDPOINTS = [
    "/api/health",
    "/api/metrics",
    "/api/cache/stats",
]


async def fire(client: httpx.AsyncClient, url: str) -> tuple[float, int]:
    t0 = time.perf_counter()
    try:
        resp = await client.get(url)
        return (time.perf_counter() - t0) * 1000, resp.status_code
    except httpx.HTTPError:
        return (time.perf_counter() - t0) * 1000, 0


async def run_endpoint(base_url: str, path: str, concurrency: int, total_requests: int):
    url = base_url.rstrip("/") + path
    durations: list[float] = []
    statuses: list[int] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        sem = asyncio.Semaphore(concurrency)

        async def bounded():
            async with sem:
                return await fire(client, url)

        results = await asyncio.gather(*(bounded() for _ in range(total_requests)))

    for dur, status in results:
        durations.append(dur)
        statuses.append(status)
    return durations, statuses


def percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    idx = min(int(len(sorted_values) * pct), len(sorted_values) - 1)
    return sorted_values[idx]


def report(path: str, concurrency: int, durations: list[float], statuses: list[int], wall_seconds: float):
    sorted_durations = sorted(durations)
    ok = sum(1 for s in statuses if 200 <= s < 300)
    errors = len(statuses) - ok
    rps = len(durations) / wall_seconds if wall_seconds > 0 else 0.0

    print(f"\n=== {path}  (concurrency={concurrency}, n={len(durations)}) ===")
    print(f"  wall time      : {wall_seconds:.2f}s")
    print(f"  throughput     : {rps:.1f} req/s")
    print(f"  success/error  : {ok}/{errors}")
    print(f"  avg latency    : {statistics.mean(sorted_durations):.1f} ms")
    print(f"  p50 / p95 / p99: {percentile(sorted_durations, 0.50):.1f} / "
          f"{percentile(sorted_durations, 0.95):.1f} / {percentile(sorted_durations, 0.99):.1f} ms")
    print(f"  min / max      : {min(sorted_durations):.1f} / {max(sorted_durations):.1f} ms")


async def main_async(base_url: str, concurrency: int, total_requests: int):
    print(f"Local concurrent load test — base_url={base_url}, concurrency={concurrency}, requests/endpoint={total_requests}")
    for path in ENDPOINTS:
        t0 = time.perf_counter()
        durations, statuses = await run_endpoint(base_url, path, concurrency, total_requests)
        wall = time.perf_counter() - t0
        report(path, concurrency, durations, statuses, wall)


def main():
    parser = argparse.ArgumentParser(description="Local concurrent load test (Day 13)")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--requests", type=int, default=200, help="total requests fired per endpoint")
    args = parser.parse_args()

    asyncio.run(main_async(args.base_url, args.concurrency, args.requests))


if __name__ == "__main__":
    main()
