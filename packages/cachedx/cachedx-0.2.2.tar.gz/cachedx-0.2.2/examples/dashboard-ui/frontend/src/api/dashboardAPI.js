/**
 * Dashboard API client for communicating with cachedx FastAPI backend
 */
class DashboardAPI {
    constructor() {
        this.baseURL = process.env.NODE_ENV === 'production'
            ? 'https://your-api.com'  // Update for production
            : 'http://localhost:8000';
    }

    async getUsers() {
        const response = await fetch(`${this.baseURL}/dashboard/users`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async getAnalytics() {
        const response = await fetch(`${this.baseURL}/dashboard/analytics`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async runCustomQuery(sql) {
        const params = new URLSearchParams({ sql });
        const response = await fetch(`${this.baseURL}/dashboard/custom-query?${params}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async getSchema() {
        const response = await fetch(`${this.baseURL}/dashboard/schema`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async getStats() {
        const response = await fetch(`${this.baseURL}/dashboard/stats`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async getSampleQueries() {
        const response = await fetch(`${this.baseURL}/dashboard/sample-queries`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }
}

const dashboardAPIInstance = new DashboardAPI();
export default dashboardAPIInstance;
