import json
import os
import threading
from app.models import Customer


class CustomerStorage:
    def __init__(self, data_file: str = "data/customers.json"):
        self.data_file = data_file
        self.customers: list[dict] = []
        self.used_ids: set[int] = set()
        self._lock = threading.Lock()
        self._ensure_data_dir()
        self._load_data()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def _load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.customers = data.get("customers", [])
                    self.used_ids = {customer["id"] for customer in self.customers}

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            self.customers = []
            self.used_ids = set()

    def _save_data(self):
        with open(self.data_file, "w") as f:
            json.dump({"customers": self.customers}, f, indent=2)

    def _find_insertion_position(self, customer: dict) -> int:
        """
        Find the correct position to insert customer to maintain sort order, using binary search.
        Sort by lastName first, then by firstName.
        """
        left, right = 0, len(self.customers)

        while left < right:
            mid = (left + right) // 2
            mid_customer = self.customers[mid]

            if (customer["lastName"] < mid_customer["lastName"] or
                (customer["lastName"] == mid_customer["lastName"] and
                 customer["firstName"] < mid_customer["firstName"])):
                right = mid
            else:
                left = mid + 1

        return left

    def validate_unique_ids(self, customers: list[Customer]) -> list[int]:
        conflicts = []
        new_ids = set()

        for customer in customers:
            if customer.id in self.used_ids or customer.id in new_ids:
                conflicts.append(customer.id)
            new_ids.add(customer.id)

        return conflicts

    def add_customers(self, customers: list[Customer]) -> bool:
        """
        Add multiple customers maintaining sort order.
        Returns True if successful, False if there are ID conflicts.
        """
        with self._lock:
            conflicts = self.validate_unique_ids(customers)
            if conflicts:
                raise ValueError(f"Duplicate IDs found: {conflicts}")

            for customer in customers:
                customer_dict = customer.model_dump()
                position = self._find_insertion_position(customer_dict)
                self.customers.insert(position, customer_dict)
                self.used_ids.add(customer.id)

            self._save_data()
            return True

    def get_all_customers(self) -> list[dict]:
        """Return all customers (already sorted)"""
        with self._lock:
            return self.customers.copy()

    def get_customer_count(self) -> int:
        return len(self.customers)


storage = CustomerStorage()