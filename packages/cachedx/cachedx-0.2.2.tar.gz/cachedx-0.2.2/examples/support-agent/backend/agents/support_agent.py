"""
PydanticAI support agent with cachedx data access
"""

import json
import os

from cachedx import safe_llm_query
from cachedx.mirror import mirror_json
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from .data_service import CompanyDataService


class SupportQuery(BaseModel):
    user_id: str
    question: str
    context: str = ""


class SupportResponse(BaseModel):
    answer: str
    confidence: float
    data_sources: list[str]
    suggested_actions: list[str] = []


# Create the PydanticAI agent
support_agent = Agent[None, SupportResponse](
    "openai:gpt-4o-mini",  # Use mini for cost efficiency in demo
    system_prompt="""
    You are an intelligent customer support agent for a company.

    You have access to a SQL database with real-time company data including:
    - User information and profiles
    - Order history and status
    - Product catalog and details
    - Inventory levels

    When answering questions:
    1. Use the query_company_data tool to get accurate, up-to-date information
    2. Provide specific details from the data
    3. Suggest actionable next steps when appropriate
    4. Be helpful, accurate, and professional
    5. If you can't find information, say so clearly
    6. Always include confidence level (0.0-1.0) based on data availability
    7. List data sources you used (tables/endpoints)

    IMPORTANT: You can only read data, never modify it. Only SELECT queries work.

    Example response format:
    - Answer: Clear, helpful response with specific data
    - Confidence: 0.9 (high confidence when you have good data)
    - Data sources: ["users", "orders", "inventory"]
    - Suggested actions: ["Check tracking", "Contact shipping"]
    """,
)


@support_agent.tool
async def query_company_data(ctx: RunContext[None], question: str, user_id: str = None) -> str:
    """
    Query company database for information to answer customer questions.
    Use this tool to get real-time data about users, orders, products, and inventory.

    Args:
        question: The customer's question
        user_id: Optional user ID for personalized queries
    """

    try:
        # Pre-populate cache with relevant user data
        async with CompanyDataService() as data_service:
            if user_id:
                # Load user-specific data into cache
                user_info = await data_service.get_user_info(user_id)
                user_orders = await data_service.get_user_orders(user_id)

                # Mirror data to database for querying
                if user_info and not isinstance(user_info, dict) or user_info.get("error"):
                    pass  # Skip invalid data
                else:
                    mirror_json(
                        [user_info] if isinstance(user_info, dict) else user_info,
                        "users",
                        auto_register=True,
                    )

                if hasattr(user_orders, "json"):
                    orders_data = user_orders.json()
                    if orders_data:
                        mirror_json(orders_data, "orders", auto_register=True)

            # Load general data
            products = await data_service.get_products()
            inventory = await data_service.check_inventory()

            # Mirror general data
            if hasattr(products, "json"):
                products_data = products.json()
                if products_data:
                    mirror_json(products_data, "products", auto_register=True)

            if inventory and isinstance(inventory, list):
                mirror_json(inventory, "inventory", auto_register=True)

        # Get schema context for query generation
        # context = build_llm_context(include_schemas=True, include_samples=True, sample_limit=2)

        # Generate appropriate SQL based on question type
        sql_queries = []

        question_lower = question.lower()

        if "order" in question_lower and user_id:
            sql_queries.append(
                f"SELECT * FROM orders WHERE user_id = '{user_id}' ORDER BY created_at DESC LIMIT 5"  # nosec B608
            )

        if "user" in question_lower or "account" in question_lower and user_id:
            sql_queries.append(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")  # nosec B608

        if "inventory" in question_lower or "stock" in question_lower:
            if "iphone" in question_lower or "phone" in question_lower:
                sql_queries.append("SELECT * FROM inventory WHERE product_name LIKE '%iPhone%'")
            else:
                sql_queries.append(
                    "SELECT * FROM inventory WHERE quantity < 20 ORDER BY quantity ASC"
                )

        if "product" in question_lower:
            if "electronics" in question_lower:
                sql_queries.append("SELECT * FROM products WHERE category = 'electronics'")
            else:
                sql_queries.append("SELECT * FROM products LIMIT 10")

        # If no specific queries, do general exploration
        if not sql_queries:
            sql_queries = [
                "SELECT COUNT(*) as count FROM users",
                "SELECT COUNT(*) as count FROM orders",
                "SELECT COUNT(*) as count FROM products",
                "SELECT COUNT(*) as count FROM inventory",
            ]

        # Execute queries and collect results
        results = []
        for sql in sql_queries:
            try:
                result = safe_llm_query(sql)
                if result["success"] and result["data"]:
                    results.append(
                        {
                            "query": sql,
                            "data": result["data"][:3],  # Limit for performance
                            "row_count": result["row_count"],
                        }
                    )
                else:
                    # Log the unsuccessful query for debugging
                    error_msg = result.get("error", "No data returned")
                    results.append({"query": sql, "error": error_msg, "success": False})
            except Exception as e:
                results.append({"query": sql, "error": str(e), "success": False})

        return f"Database query results for: {question}\n\n" + json.dumps(
            results, indent=2, default=str
        )

    except Exception as e:
        return f"Error querying company data: {str(e)}"


async def handle_support_query(query: SupportQuery) -> SupportResponse:
    """Main function to handle support queries"""

    try:
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            return SupportResponse(
                answer="I'm sorry, but the AI agent is not properly configured. Please set the OPENAI_API_KEY environment variable.",
                confidence=0.0,
                data_sources=["system"],
                suggested_actions=[
                    "Contact system administrator",
                    "Check environment configuration",
                ],
            )

        # Run the agent with user context
        result = await support_agent.run(
            f"User {query.user_id} asks: {query.question}",
            message_history=[],  # Could maintain conversation history
        )

        # Extract the structured response from the result
        if hasattr(result, "data") and isinstance(result.data, SupportResponse):
            return result.data
        elif hasattr(result, "output"):
            # Parse the text output into a structured response
            output_text = result.output
            return SupportResponse(
                answer=output_text,
                confidence=0.7,  # Default confidence
                data_sources=["agent_output"],
                suggested_actions=["Contact support if needed"],
            )
        else:
            # Fallback for unexpected result format
            return SupportResponse(
                answer=str(result),
                confidence=0.5,
                data_sources=["agent_fallback"],
                suggested_actions=["Try rephrasing your question"],
            )

    except Exception as e:
        # Fallback response when AI agent fails
        return SupportResponse(
            answer=f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or contact human support.",
            confidence=0.0,
            data_sources=["error_handler"],
            suggested_actions=[
                "Try rephrasing your question",
                "Contact human support",
                "Check system status",
            ],
        )
