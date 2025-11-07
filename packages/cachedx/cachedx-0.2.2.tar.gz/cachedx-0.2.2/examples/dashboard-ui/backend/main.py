"""
FastAPI backend for dashboard UI example using cachedx
"""

import json

from cache_service import APIService
from cachedx import build_llm_context, safe_llm_query
from cachedx.mirror import mirror_json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analytics Dashboard API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Dashboard API is running", "status": "healthy"}


@app.get("/dashboard/users")
async def get_users():
    """Get user data with automatic caching"""
    async with APIService() as api:
        # Simulate API call with mock data
        response_data = await api.get_mock_data("/api/users")
        data = json.loads(response_data)

        # Mirror to database for querying
        mirror_json(data, "users", auto_register=True)

        return {"users": data, "cached": True}


@app.get("/dashboard/analytics")
async def get_analytics():
    """Get analytics with SQL querying capability"""
    async with APIService() as api:
        # Fetch and cache analytics data
        daily_data = json.loads(await api.get_mock_data("/api/analytics/daily"))
        monthly_data = json.loads(await api.get_mock_data("/api/analytics/monthly"))

        # Mirror to database
        mirror_json(daily_data, "analytics_daily", auto_register=True)
        mirror_json(monthly_data, "analytics_monthly", auto_register=True)

        # Now query the cached data with custom SQL
        daily_stats = safe_llm_query("""
            SELECT date, active_users, revenue
            FROM analytics_daily
            ORDER BY date DESC
        """)

        monthly_trends = safe_llm_query("""
            SELECT
                date,
                active_users,
                revenue,
                conversions
            FROM analytics_monthly
            ORDER BY date DESC
        """)

        return {
            "daily_stats": daily_stats["data"] if daily_stats["success"] else [],
            "monthly_trends": monthly_trends["data"] if monthly_trends["success"] else [],
            "cached": True,
        }


@app.get("/dashboard/custom-query")
async def custom_query(sql: str = Query(..., description="SQL query to execute")):
    """Allow dashboard to run custom SQL queries safely"""
    try:
        result = safe_llm_query(sql, limit=1000)  # Limit for safety

        return {
            "success": result["success"],
            "data": result.get("data", []),
            "row_count": result.get("row_count", 0),
            "warnings": result.get("warnings", []),
            "error": result.get("error"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/dashboard/schema")
async def get_schema():
    """Get schema information for the dashboard query builder"""
    context = build_llm_context(include_samples=True, sample_limit=3)
    return {"schema_context": context}


@app.get("/dashboard/stats")
async def get_stats():
    """Get cache and database statistics"""
    try:
        # Get table statistics
        table_stats = {}
        tables = ["users", "analytics_daily", "analytics_monthly"]

        for table in tables:
            try:
                result = safe_llm_query(f"SELECT COUNT(*) as count FROM {table}")  # nosec B608
                if result["success"] and result["data"]:
                    table_stats[table] = result["data"][0]["count"]
            except Exception:
                table_stats[table] = 0

        return {"table_stats": table_stats, "status": "operational"}
    except Exception as e:
        return {"error": str(e), "status": "error"}


@app.get("/dashboard/sample-queries")
async def get_sample_queries():
    """Get sample queries users can try"""
    return {
        "queries": [
            {
                "name": "All Users",
                "description": "Get all users with their status",
                "sql": "SELECT name, email, active FROM users ORDER BY name",
            },
            {
                "name": "Active Users Only",
                "description": "Get only active users",
                "sql": "SELECT name, email FROM users WHERE active = true",
            },
            {
                "name": "Daily Analytics Summary",
                "description": "Recent daily analytics data",
                "sql": "SELECT date, active_users, revenue FROM analytics_daily ORDER BY date DESC LIMIT 7",
            },
            {
                "name": "Revenue Trends",
                "description": "Monthly revenue comparison",
                "sql": "SELECT date, revenue, conversions FROM analytics_monthly ORDER BY revenue DESC",
            },
            {
                "name": "User Activity Stats",
                "description": "Count of active vs inactive users",
                "sql": "SELECT active, COUNT(*) as count FROM users GROUP BY active",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting Dashboard API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
