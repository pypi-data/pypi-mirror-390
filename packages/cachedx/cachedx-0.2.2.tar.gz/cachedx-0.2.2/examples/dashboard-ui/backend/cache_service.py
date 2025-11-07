"""
cachedx configuration for dashboard analytics API
"""

from datetime import timedelta

from cachedx.httpcache import CacheConfig, CachedClient, CacheStrategy, EndpointConfig


class APIService:
    """Service for managing cached API access to company data"""

    def __init__(self):
        # Configure different caching strategies for different endpoints
        self.cache_config = CacheConfig(
            default_ttl=timedelta(minutes=5),
            enable_logging=True,
            endpoints={
                # User data changes infrequently - cache for 30 minutes
                "/api/users": EndpointConfig(
                    strategy=CacheStrategy.CACHED, ttl=timedelta(minutes=30), table_name="users"
                ),
                # Analytics data - cache for 10 minutes
                "/api/analytics/*": EndpointConfig(
                    strategy=CacheStrategy.CACHED, ttl=timedelta(minutes=10)
                ),
                # Live metrics - always fetch but store for querying
                "/api/metrics/realtime": EndpointConfig(strategy=CacheStrategy.REALTIME),
                # Configuration rarely changes - cache forever
                "/api/config": EndpointConfig(strategy=CacheStrategy.STATIC),
            },
        )

        self.client = None

    async def __aenter__(self):
        self.client = CachedClient(
            base_url="https://api.yourcompany.com",
            cache_config=self.cache_config,
            headers={"Authorization": "Bearer YOUR_API_TOKEN"},
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    async def get_mock_data(self, endpoint: str):
        """Get mock data for demo purposes"""
        import json

        # Mock data for different endpoints
        mock_responses = {
            "/api/users": [
                {
                    "id": 1,
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "active": True,
                    "created_at": "2023-01-15T10:30:00Z",
                },
                {
                    "id": 2,
                    "name": "Bob Smith",
                    "email": "bob@example.com",
                    "active": True,
                    "created_at": "2023-02-20T14:22:00Z",
                },
                {
                    "id": 3,
                    "name": "Carol Davis",
                    "email": "carol@example.com",
                    "active": False,
                    "created_at": "2023-03-10T09:15:00Z",
                },
            ],
            "/api/analytics/daily": [
                {"date": "2024-01-01", "active_users": 1250, "revenue": 5420.50, "conversions": 45},
                {"date": "2024-01-02", "active_users": 1180, "revenue": 4890.25, "conversions": 38},
                {"date": "2024-01-03", "active_users": 1340, "revenue": 6125.75, "conversions": 52},
            ],
            "/api/analytics/monthly": [
                {
                    "date": "2024-01-01",
                    "active_users": 35000,
                    "revenue": 125000.00,
                    "conversions": 1250,
                },
                {
                    "date": "2023-12-01",
                    "active_users": 32000,
                    "revenue": 115000.00,
                    "conversions": 1100,
                },
                {
                    "date": "2023-11-01",
                    "active_users": 30000,
                    "revenue": 108000.00,
                    "conversions": 980,
                },
            ],
        }

        # Return mock data as JSON string (simulating API response)
        if endpoint in mock_responses:
            return json.dumps(mock_responses[endpoint])
        else:
            return json.dumps({"error": "Endpoint not found"})
