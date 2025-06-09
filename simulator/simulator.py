import asyncio
import httpx
import random
import time
import os


MINIMUM_SIMULATION_AGE = 10
MAXIMUM_SIMULATION_AGE = 90


class CustomerSimulator:
    """Simulator for testing the customers API with parallel requests"""

    FIRST_NAMES = ["Leia", "Sadie", "Jose", "Sara", "Frank", "Dewey", "Tomas", "Joel", "Lukas", "Carlos"]
    LAST_NAMES = ["Liberty", "Ray", "Harrison", "Ronan", "Drew", "Powell", "Larsen", "Chan", "Anderson", "Lane"]

    def __init__(self, base_url: str, starting_customer_id: int = 1):
        self.base_url = base_url
        self.current_customer_id = starting_customer_id
        self.session = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    def generate_random_customers(self, count: int) -> list[dict]:
        customers = []
        for _ in range(count):
            customer = {
                "firstName": random.choice(self.FIRST_NAMES),
                "lastName": random.choice(self.LAST_NAMES),
                "age": random.randint(MINIMUM_SIMULATION_AGE, MAXIMUM_SIMULATION_AGE),
                "id": self.current_customer_id
            }
            customers.append(customer)
            self.current_customer_id += 1

        return customers

    async def post_customers(self, customers: list[dict]) -> tuple[bool, dict]:
        try:
            response = await self.session.post(
                f"{self.base_url}/customers",
                json=customers
            )
            return response.status_code == 201, response.json()
        except Exception as e:
            return False, {"error": str(e)}

    async def get_customers(self) -> tuple[bool, dict]:
        try:
            response = await self.session.get(f"{self.base_url}/customers")
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, {"error": str(e)}

    async def run_simulation(self, post_requests_count: int = 5, get_request_count: int = 3):
        print(f"🚀 Starting simulation with {post_requests_count} POST and {get_request_count} GET requests")
        print(f"📡 API Base URL: {self.base_url}")
        print("-" * 60)

        try:
            response = await self.session.get(f"{self.base_url}/")
            if response.status_code != 200:
                print(f"⚠️  Warning: API health check failed (status: {response.status_code})")
        except Exception:
            print("⚠️  Warning: Could not connect to API for health check")

        # Generate tasks for parallel execution
        tasks = []

        # Create POST requests
        for i in range(post_requests_count):
            number_of_customers = random.randint(2, 5)
            customers = self.generate_random_customers(number_of_customers)
            task = asyncio.create_task(
                self.post_customers(customers),
                name=f"POST-{i+1}"
            )
            tasks.append(("POST", f"POST-{i+1}", task, len(customers)))

        # Create GET requests
        for i in range(get_request_count):
            task = asyncio.create_task(
                self.get_customers(),
                name=f"GET-{i+1}"
            )
            tasks.append(("GET", f"GET-{i+1}", task, 0))

        start_time = time.time()
        results = []

        print("⏳ Executing requests in parallel...")
        for request_type, name, task, customer_count in tasks:
            try:
                success, response = await task
                results.append({
                    "type": request_type,
                    "name": name,
                    "success": success,
                    "response": response,
                    "customer_count": customer_count
                })
            except Exception as e:
                results.append({
                    "type": request_type,
                    "name": name,
                    "success": False,
                    "response": {"error": str(e)},
                    "customer_count": customer_count
                })

        end_time = time.time()

        # Display results
        self.display_results(results, end_time - start_time)

        # Final GET to show all customers
        print("\n" + "="*60)
        print("📋 FINAL STATE - All customers in the system:")
        print("="*60)

        success, final_response = await self.get_customers()
        if success:
            customers = final_response.get("customers", [])
            print(f"Total customers: {final_response.get('total', 0)}")
            print("\nCustomers (sorted by lastName, then firstName):")
            for i, customer in enumerate(customers, 1):
                print(f"{i:2d}. {customer['lastName']}, {customer['firstName']} "
                      f"(age: {customer['age']}, id: {customer['id']})")
        else:
            print("❌ Failed to retrieve final customer list")

    def display_results(self, results: list[dict], total_time: float):
        """Display simulation results"""
        print(f"\n✅ Simulation completed in {total_time:.2f} seconds")
        print("=" * 60)

        post_results = [r for r in results if r["type"] == "POST"]
        get_results = [r for r in results if r["type"] == "GET"]

        # POST results
        print("📤 POST Results:")
        successful_posts = 0
        total_customers_added = 0

        for result in post_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['name']}: ", end="")

            if result["success"]:
                successful_posts += 1
                customers_added = result["customer_count"]
                total_customers_added += customers_added
                print(f"Added {customers_added} customers")
            else:
                error_msg = result["response"].get("detail", result["response"].get("error", "Unknown error"))
                print(f"Failed - {error_msg}")

        print(f"  📊 POST Summary: {successful_posts}/{len(post_results)} successful, "
              f"{total_customers_added} total customers added")

        # GET results
        print("\n📥 GET Results:")
        successful_gets = 0

        for result in get_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['name']}: ", end="")

            if result["success"]:
                successful_gets += 1
                total = result["response"].get("total", 0)
                print(f"Retrieved {total} customers")
            else:
                error_msg = result["response"].get("detail", result["response"].get("error", "Unknown error"))
                print(f"Failed - {error_msg}")

        print(f"  📊 GET Summary: {successful_gets}/{len(get_results)} successful")


async def main(base_url: str, starting_customer_id: int):
    """Main function to run the simulation"""
    print("Customer API Simulator")
    print("=" * 60)

    async with CustomerSimulator(base_url, starting_customer_id) as simulator:
        await simulator.run_simulation(post_requests_count=3, get_request_count=2)


if __name__ == "__main__":
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    starting_customer_id = int(os.getenv("STARTING_CUSTOMER_ID", "1"))
    post_requests_count = int(os.getenv("POST_REQUESTS_COUNT", "3"))
    get_request_count = int(os.getenv("GET_REQUESTS_COUNT", "2"))

    async def configured_main():
        async with CustomerSimulator(base_url, starting_customer_id) as simulator:
            await simulator.run_simulation(post_requests_count=post_requests_count, get_request_count=get_request_count)

    asyncio.run(configured_main())