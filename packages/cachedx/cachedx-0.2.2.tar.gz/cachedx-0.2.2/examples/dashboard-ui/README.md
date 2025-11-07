# Data Dashboard UI App Example

This example demonstrates building a React dashboard that displays user analytics from a REST API with intelligent caching using cachedx.

## Features Demonstrated

- **Fast Loading**: 50x faster dashboard loading with intelligent caching
- **Offline Capability**: Works even when API is down (serves cached data)
- **Custom Analytics**: Users can write SQL queries without touching the backend
- **Safety**: SQL injection protection, query limits, SELECT-only enforcement
- **Real-time Updates**: Live metrics with query caching benefits

## Project Structure

```
dashboard-ui/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── cache_service.py  # cachedx configuration
│   └── pyproject.toml    # Python dependencies (uv)
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── dashboardAPI.js  # API client
│   │   ├── components/
│   │   │   ├── Dashboard.js     # Main dashboard
│   │   │   └── QueryBuilder.js  # SQL query interface
│   │   └── App.js        # React app
│   ├── package.json      # Node dependencies
│   └── public/
└── README.md            # This file
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
uv sync
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
2. The dashboard will automatically load cached data
3. Try the custom query builder to run SQL queries
4. Monitor cache performance in the console

## Configuration

The backend uses different caching strategies:

- **User data**: 30 minutes (changes infrequently)
- **Analytics**: 10 minutes (moderate updates)
- **Live metrics**: Realtime (always fetch, but queryable)
- **Configuration**: Static (cache forever)

## API Endpoints

- `GET /dashboard/users` - Get user data with caching
- `GET /dashboard/analytics` - Get analytics with SQL capabilities
- `GET /dashboard/custom-query?sql=...` - Run custom SQL queries
- `GET /dashboard/schema` - Get database schema for query builder

## Benefits

- Dashboard loads in ~100ms instead of 5+ seconds
- Works offline with cached data
- Custom SQL queries without backend changes
- Automatic query safety and limits
- Real-time data with caching benefits
