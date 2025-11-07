# AI Customer Support Agent Example

This example demonstrates building an intelligent customer support agent using PydanticAI that can access company APIs to answer questions about users, orders, and inventory with real-time data through cachedx caching.

## Features Demonstrated

- **Intelligent Responses**: Agent has access to real-time company data
- **Fast Agent Responses**: Cached data enables sub-second responses
- **Safe Operations**: Agent can query but never modify data
- **Rich Context**: Agent sees user history, inventory, orders in real-time
- **Always Current**: Critical data like inventory refreshes every 30 seconds
- **Scalable**: Handles thousands of concurrent users with cached data
- **Actionable**: Agent can suggest specific next steps based on data

## Project Structure

```
support-agent/
├── backend/
│   ├── agents/
│   │   ├── data_service.py    # cachedx API service
│   │   └── support_agent.py   # PydanticAI agent
│   ├── main.py               # FastAPI server
│   └── pyproject.toml        # Python dependencies (uv)
├── frontend/
│   ├── src/
│   │   └── components/
│   │       └── SupportChat.js # Chat interface
│   ├── package.json          # Node dependencies
│   └── public/
└── README.md                # This file
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
uv sync
export OPENAI_API_KEY="your-openai-api-key"
uv run python main.py
```

The backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`

### 3. Usage

1. Open `http://localhost:3000` in your browser
2. Start chatting with the AI agent
3. Ask questions like:
   - "What's the status of my recent orders?"
   - "Is the iPhone 15 Pro in stock?"
   - "Show me my account information"
   - "What products do you have in the electronics category?"

## Configuration

The backend uses different caching strategies for different data types:

- **User data**: 15 minutes (moderate changes)
- **Orders**: 2 minutes (frequent updates)
- **Inventory**: 30 seconds (critical accuracy)
- **Product catalog**: 2 hours (rarely changes)

## API Endpoints

- `POST /support/chat` - Chat with the AI agent
- `GET /support/data-stats` - Get cache and data statistics
- `GET /support/schema` - Get database schema information
- `POST /support/direct-query` - Execute direct SQL queries (admin)

## Environment Variables

Create a `.env` file in the backend directory:

```
OPENAI_API_KEY=your-openai-api-key-here
COMPANY_API_BASE_URL=https://api.yourcompany.com
COMPANY_API_TOKEN=your-api-token-here
```

## Benefits

- Agent responses in ~500ms instead of 3-5 seconds
- Works with live data from multiple API endpoints
- Automatic safety: agent cannot modify any data
- Rich context from user history, inventory, and orders
- Critical data stays current (inventory updates every 30s)
- Scales to thousands of concurrent users
- Provides actionable suggestions based on real data

## Example Conversations

**User:** "What's the status of my recent orders?"

**Agent:** "I found 3 recent orders for you:

- Order #12345: Delivered yesterday (Wireless Headphones - $89.99)
- Order #12346: In transit, expected tomorrow (Laptop Stand - $45.00)
- Order #12347: Processing (USB Cable - $12.99)

Would you like me to check the tracking details for any of these orders?"

**User:** "Is the iPhone 15 Pro in stock?"

**Agent:** "Let me check current inventory... The iPhone 15 Pro (256GB, Natural Titanium) shows 12 units in stock at our main warehouse. However, stock is running low - we typically restock when we reach 5 units.

I'd recommend placing your order soon if you're interested. Would you like me to help you get started with an order?"
