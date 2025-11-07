"""
Data service for managing company API access with cachedx intelligent caching
"""

import os
from datetime import timedelta

from cachedx.httpcache import CacheConfig, CachedClient, CacheStrategy, EndpointConfig
from cachedx.mirror import hybrid_cache


class CompanyDataService:
    """Service to manage access to company APIs with intelligent caching"""

    def __init__(self):
        # Configure caching for different API patterns
        self.cache_config = CacheConfig(
            default_ttl=timedelta(minutes=5),
            enable_logging=True,
            endpoints={
                # User data - moderate caching
                "/users/*": EndpointConfig(
                    strategy=CacheStrategy.CACHED,
                    ttl=timedelta(minutes=15),
                ),
                # Orders - short caching (data changes frequently)
                "/orders/*": EndpointConfig(
                    strategy=CacheStrategy.CACHED,
                    ttl=timedelta(minutes=2),
                ),
                # Inventory - very short caching (critical accuracy)
                "/inventory/*": EndpointConfig(
                    strategy=CacheStrategy.CACHED,
                    ttl=timedelta(seconds=30),
                ),
                # Product catalog - long caching (rarely changes)
                "/products/*": EndpointConfig(
                    strategy=CacheStrategy.CACHED,
                    ttl=timedelta(hours=2),
                ),
            },
        )

        self.client = None

    async def __aenter__(self):
        api_base_url = os.getenv("COMPANY_API_BASE_URL", "https://api.company.com")
        api_token = os.getenv("COMPANY_API_TOKEN", "demo-token")

        self.client = CachedClient(
            base_url=api_base_url,
            cache_config=self.cache_config,
            headers={"Authorization": f"Bearer {api_token}"},
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    # Mock data for demo purposes
    def _get_mock_data(self, endpoint: str, user_id: str = None):
        """Generate mock data for demo purposes"""

        mock_users = {
            "user123": {
                "id": "user123",
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "status": "active",
                "created_at": "2023-01-15T10:30:00Z",
                "phone": "+1-555-0123",
                "address": "123 Main St, Anytown, USA",
            },
            "user456": {
                "id": "user456",
                "name": "Bob Smith",
                "email": "bob@example.com",
                "status": "active",
                "created_at": "2023-02-20T14:22:00Z",
                "phone": "+1-555-0456",
                "address": "456 Oak Ave, Somewhere, USA",
            },
        }

        mock_orders = {
            "user123": [
                {
                    "id": "12345",
                    "user_id": "user123",
                    "status": "delivered",
                    "total": 89.99,
                    "items": [{"name": "Wireless Headphones", "price": 89.99, "qty": 1}],
                    "created_at": "2024-01-20T10:00:00Z",
                    "delivered_at": "2024-01-22T15:30:00Z",
                },
                {
                    "id": "12346",
                    "user_id": "user123",
                    "status": "in_transit",
                    "total": 45.00,
                    "items": [{"name": "Laptop Stand", "price": 45.00, "qty": 1}],
                    "created_at": "2024-01-21T14:00:00Z",
                    "expected_delivery": "2024-01-25T12:00:00Z",
                },
                {
                    "id": "12347",
                    "user_id": "user123",
                    "status": "processing",
                    "total": 12.99,
                    "items": [{"name": "USB Cable", "price": 12.99, "qty": 1}],
                    "created_at": "2024-01-23T09:30:00Z",
                },
            ]
        }

        mock_products = [
            {
                "id": "prod1",
                "name": "iPhone 15 Pro",
                "category": "electronics",
                "price": 999.99,
                "description": "Latest iPhone with advanced features",
                "variants": [
                    {"storage": "128GB", "color": "Natural Titanium"},
                    {"storage": "256GB", "color": "Natural Titanium"},
                    {"storage": "512GB", "color": "Natural Titanium"},
                ],
            },
            {
                "id": "prod2",
                "name": "Wireless Headphones",
                "category": "electronics",
                "price": 89.99,
                "description": "Premium wireless headphones with noise cancellation",
            },
            {
                "id": "prod3",
                "name": "Laptop Stand",
                "category": "accessories",
                "price": 45.00,
                "description": "Adjustable aluminum laptop stand",
            },
        ]

        mock_inventory = [
            {
                "product_id": "prod1",
                "product_name": "iPhone 15 Pro",
                "quantity": 12,
                "status": "in_stock",
            },
            {
                "product_id": "prod2",
                "product_name": "Wireless Headphones",
                "quantity": 25,
                "status": "in_stock",
            },
            {
                "product_id": "prod3",
                "product_name": "Laptop Stand",
                "quantity": 8,
                "status": "low_stock",
            },
        ]

        # Return appropriate mock data based on endpoint
        if "/users/" in endpoint:
            if user_id and user_id in mock_users:
                return mock_users[user_id]
            return list(mock_users.values())
        elif "/orders/" in endpoint:
            if user_id and user_id in mock_orders:
                return mock_orders[user_id]
            return []
        elif "/products" in endpoint:
            return mock_products
        elif "/inventory" in endpoint:
            return mock_inventory
        else:
            return {"error": "Unknown endpoint"}

    # Register schema mappings for complex queries
    @hybrid_cache(resource="orders", auto_register=True)
    async def get_user_orders(self, user_id: str):
        """Get user orders with automatic mirroring"""
        # In real implementation, this would make actual API call
        # return await self.client.get(f"/orders/user/{user_id}")

        # For demo, return mock data
        orders_data = self._get_mock_data(f"/orders/user/{user_id}", user_id)
        return type("MockResponse", (), {"json": lambda: orders_data})()

    @hybrid_cache(resource="products", auto_register=True)
    async def get_products(self, category: str = None):
        """Get products with automatic schema inference"""
        endpoint = f"/products/category/{category}" if category else "/products"

        # For demo, return mock data
        products_data = self._get_mock_data(endpoint)
        if category:
            products_data = [p for p in products_data if p.get("category") == category]

        return type("MockResponse", (), {"json": lambda: products_data})()

    async def get_user_info(self, user_id: str):
        """Get user information - simple caching"""
        # In real implementation:
        # response = await self.client.get(f"/users/{user_id}")
        # return response.json()

        # For demo, return mock data
        return self._get_mock_data(f"/users/{user_id}", user_id)

    async def check_inventory(self, product_id: str = None):
        """Check inventory - frequent updates needed"""
        # In real implementation:
        # endpoint = f"/inventory/{product_id}" if product_id else "/inventory"
        # response = await self.client.get(endpoint)
        # return response.json()

        # For demo, return mock data
        inventory_data = self._get_mock_data("/inventory")
        if product_id:
            inventory_data = [
                item for item in inventory_data if item.get("product_id") == product_id
            ]
            return inventory_data[0] if inventory_data else {"error": "Product not found"}

        return inventory_data
