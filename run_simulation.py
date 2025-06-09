import asyncio
import os
import sys

from simulator.simulator import CustomerSimulator


async def run_simulation(api_url: str, starting_customer_id: int, post_requests_count: int, get_requests_count: int):
    print("🎯 Customer API Load Testing Simulator")
    print("=" * 60)
    print(f"Target API: {api_url}")
    print("=" * 60)

    try:
        async with CustomerSimulator(base_url=api_url, starting_customer_id=starting_customer_id) as simulator:
            await simulator.run_simulation(post_requests_count=post_requests_count, get_request_count=get_requests_count)
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    starting_customer_id = int(os.environ.get("STARTING_CUSTOMER_ID", "1"))
    post_requests_count = int(os.environ.get("POST_REQUESTS_COUNT", "3"))
    get_requests_count = int(os.environ.get("GET_REQUESTS_COUNT", "2"))
    exit_code = asyncio.run(run_simulation(api_url, starting_customer_id, post_requests_count, get_requests_count))
    sys.exit(exit_code)