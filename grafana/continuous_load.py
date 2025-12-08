#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiohttp",
# ]
# ///
"""
Continuous load generator for Grafana metrics testing.
Generates HTTP requests to all microservices to create metrics.
"""

import asyncio
import random
import aiohttp

SERVICES = {
    "gateway": "http://localhost:8000",
    "user-account": "http://localhost:8001",
    "game-catalog": "http://localhost:8002",
    "booking": "http://localhost:8003",
    "payment": "http://localhost:8004",
    "rent": "http://localhost:8005",
    "rating": "http://localhost:8006",
}

ENDPOINTS = {
    "gateway": ["/", "/health", "/docs"],
    "user-account": ["/health", "/api/v1/users/test-user"],
    "game-catalog": ["/health", "/api/v1/games/test-game"],
    "booking": ["/health", "/api/v1/bookings/test-booking"],
    "payment": ["/health", "/api/v1/payments/test-payment"],
    "rent": ["/health", "/api/v1/orders/test-order"],
    "rating": ["/health", "/api/v1/ratings/test-rating"],
}


async def make_request(session, service_name, base_url, endpoint):
    """Make async HTTP request to a service endpoint."""
    url = f"{base_url}{endpoint}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
            return response.status
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None


async def generate_load(session, service_name, base_url, duration=60, interval=2):
    """Generate continuous load for a service."""
    end_time = asyncio.get_event_loop().time() + duration
    request_count = 0

    print(f"🚀 Starting load generation for {service_name}...")

    while asyncio.get_event_loop().time() < end_time:
        endpoints = ENDPOINTS.get(service_name, ["/health"])
        endpoint = random.choice(endpoints)

        await make_request(session, service_name, base_url, endpoint)
        request_count += 1

        if request_count % 10 == 0:
            print(f"  {service_name}: {request_count} requests made")

        await asyncio.sleep(interval + random.uniform(-0.5, 0.5))

    print(f"✅ {service_name}: Completed {request_count} requests")
    return request_count


async def main():
    """Main function to generate load for all services."""
    duration = 300
    print(f"📊 Starting continuous load generation for {duration} seconds...")
    print("   This will generate metrics visible in Grafana")
    print("   Press Ctrl+C to stop early\n")

    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_load(session, service_name, base_url, duration)
            for service_name, base_url in SERVICES.items()
        ]

        try:
            results = await asyncio.gather(*tasks)
            total_requests = sum(results)
            print(f"\n✅ Load generation complete! Total requests: {total_requests}")
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping load generation...")
            for task in tasks:
                task.cancel()

    print("\n📈 Check Grafana at http://localhost:3000")
    print("   Dashboard: Microservices Overview")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
