"""
FastAPI server for AI support agent using cachedx + PydanticAI
"""

import os

from agents.data_service import CompanyDataService
from agents.support_agent import SupportQuery, SupportResponse, handle_support_query
from cachedx import build_llm_context, safe_llm_query
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Customer Support API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Support Agent API is running",
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/support/chat", response_model=SupportResponse)
async def chat_with_agent(query: SupportQuery):
    """Chat with the AI support agent"""
    try:
        response = await handle_support_query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/support/data-stats")
async def get_data_stats():
    """Get statistics about cached data and system status"""
    try:
        async with CompanyDataService():
            # Get basic service info
            stats = {"service": "operational"}

            # Get row counts from different tables
            table_stats = {}
            try:
                tables = ["orders", "products", "users", "inventory"]
                for table in tables:
                    try:
                        result = safe_llm_query(f"SELECT COUNT(*) as count FROM {table}")  # nosec B608
                        if result["success"] and result["data"]:
                            table_stats[table] = result["data"][0]["count"]
                    except Exception:
                        table_stats[table] = 0
            except Exception as e:
                table_stats["error"] = str(e)

            return {
                "cache_stats": stats,
                "table_stats": table_stats,
                "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                "system_status": "operational",
            }
    except Exception as e:
        return {"error": str(e), "system_status": "error"}


@app.get("/support/schema")
async def get_database_schema():
    """Get database schema for debugging/admin purposes"""
    try:
        context = build_llm_context(include_samples=True, sample_limit=2)
        return {"schema": context}
    except Exception as e:
        return {"error": str(e), "schema": "Unable to generate schema context"}


@app.post("/support/direct-query")
async def direct_query(request: dict):
    """Execute direct SQL query (for admin/debugging)"""
    try:
        sql = request.get("sql", "")
        if not sql:
            raise HTTPException(status_code=400, detail="SQL query is required")

        result = safe_llm_query(sql, limit=100)  # Limit for safety
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/support/demo-data")
async def load_demo_data():
    """Load demo data for testing (useful for first-time setup)"""
    try:
        async with CompanyDataService() as service:
            # Load demo data
            user_info = await service.get_user_info("user123")
            orders = await service.get_user_orders("user123")
            products = await service.get_products()
            inventory = await service.check_inventory()

            return {
                "message": "Demo data loaded successfully",
                "user_info": user_info,
                "orders_loaded": hasattr(orders, "json"),
                "products_loaded": hasattr(products, "json"),
                "inventory_loaded": bool(inventory),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load demo data: {e}") from e


@app.get("/support/sample-queries")
async def get_sample_queries():
    """Get sample questions users can ask the agent"""
    return {
        "sample_questions": [
            {
                "category": "Orders",
                "questions": [
                    "What's the status of my recent orders?",
                    "Do I have any orders being shipped?",
                    "Show me my order history",
                    "When will my last order arrive?",
                ],
            },
            {
                "category": "Inventory",
                "questions": [
                    "Is the iPhone 15 Pro in stock?",
                    "What electronics do you have available?",
                    "Which products are running low on inventory?",
                    "Do you have wireless headphones in stock?",
                ],
            },
            {
                "category": "Account",
                "questions": [
                    "Show me my account information",
                    "What's my email address on file?",
                    "When did I create my account?",
                    "Is my account active?",
                ],
            },
            {
                "category": "Products",
                "questions": [
                    "What products do you sell?",
                    "Show me products in the electronics category",
                    "What's the price of the laptop stand?",
                    "Tell me about your product catalog",
                ],
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting AI Support Agent server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print(f"OpenAI API configured: {bool(os.getenv('OPENAI_API_KEY'))}")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Agent responses will show configuration error.")
        print("   Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
