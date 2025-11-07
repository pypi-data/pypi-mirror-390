/**
 * Main Dashboard component showing analytics data with cachedx
 */
import React, { useState, useEffect } from 'react';
import dashboardAPI from '../api/dashboardAPI';
import QueryBuilder from './QueryBuilder';

function Dashboard() {
    const [users, setUsers] = useState([]);
    const [analytics, setAnalytics] = useState({ daily_stats: [], monthly_trends: [] });
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Load all data in parallel - cachedx will handle caching
            const [usersData, analyticsData, statsData] = await Promise.all([
                dashboardAPI.getUsers(),
                dashboardAPI.getAnalytics(),
                dashboardAPI.getStats()
            ]);

            setUsers(usersData.users || []);
            setAnalytics(analyticsData);
            setStats(statsData);

        } catch (err) {
            console.error('Failed to load dashboard data:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const formatNumber = (num) => {
        return new Intl.NumberFormat('en-US').format(num);
    };

    if (loading) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <h2>Loading Dashboard...</h2>
                <p>cachedx is fetching and caching your data</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '20px', color: 'red' }}>
                <h2>Error Loading Dashboard</h2>
                <p>{error}</p>
                <button onClick={loadDashboardData}>Retry</button>
            </div>
        );
    }

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
            <header style={{ marginBottom: '30px' }}>
                <h1>📊 Analytics Dashboard</h1>
                <p>Powered by <strong>cachedx</strong> - Fast, cached, queryable data</p>
                <button
                    onClick={loadDashboardData}
                    style={{
                        padding: '8px 16px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Refresh Data
                </button>
            </header>

            {/* Stats Overview */}
            <section style={{ marginBottom: '30px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #dee2e6' }}>
                    <h3>👥 Total Users</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0' }}>
                        {formatNumber(stats.table_stats?.users || 0)}
                    </p>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #dee2e6' }}>
                    <h3>📈 Daily Records</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0' }}>
                        {formatNumber(stats.table_stats?.analytics_daily || 0)}
                    </p>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #dee2e6' }}>
                    <h3>📅 Monthly Records</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0' }}>
                        {formatNumber(stats.table_stats?.analytics_monthly || 0)}
                    </p>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#e8f5e8', borderRadius: '8px', border: '1px solid #c3e6c3' }}>
                    <h3>⚡ Cache Status</h3>
                    <p style={{ fontSize: '18px', fontWeight: 'bold', margin: '0', color: '#28a745' }}>
                        {stats.status || 'Active'}
                    </p>
                </div>
            </section>

            {/* Users Table */}
            <section style={{ marginBottom: '30px' }}>
                <h2>👥 Users</h2>
                {users.length > 0 ? (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                            <thead style={{ backgroundColor: '#007bff', color: 'white' }}>
                                <tr>
                                    <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
                                    <th style={{ padding: '12px', textAlign: 'left' }}>Email</th>
                                    <th style={{ padding: '12px', textAlign: 'center' }}>Status</th>
                                    <th style={{ padding: '12px', textAlign: 'left' }}>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((user, index) => (
                                    <tr key={user.id} style={{ borderBottom: '1px solid #dee2e6', backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white' }}>
                                        <td style={{ padding: '12px' }}>{user.name}</td>
                                        <td style={{ padding: '12px' }}>{user.email}</td>
                                        <td style={{ padding: '12px', textAlign: 'center' }}>
                                            <span style={{
                                                padding: '4px 8px',
                                                borderRadius: '4px',
                                                fontSize: '12px',
                                                fontWeight: 'bold',
                                                backgroundColor: user.active ? '#d4edda' : '#f8d7da',
                                                color: user.active ? '#155724' : '#721c24'
                                            }}>
                                                {user.active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td style={{ padding: '12px' }}>
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p>No users found</p>
                )}
            </section>

            {/* Analytics Tables */}
            <section style={{ marginBottom: '30px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                {/* Daily Stats */}
                <div>
                    <h2>📈 Daily Analytics</h2>
                    {analytics.daily_stats && analytics.daily_stats.length > 0 ? (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                                <thead style={{ backgroundColor: '#28a745', color: 'white' }}>
                                    <tr>
                                        <th style={{ padding: '10px', textAlign: 'left' }}>Date</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Users</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {analytics.daily_stats.slice(0, 5).map((stat, index) => (
                                        <tr key={stat.date} style={{ borderBottom: '1px solid #dee2e6', backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white' }}>
                                            <td style={{ padding: '10px' }}>{stat.date}</td>
                                            <td style={{ padding: '10px', textAlign: 'right' }}>{formatNumber(stat.active_users)}</td>
                                            <td style={{ padding: '10px', textAlign: 'right' }}>{formatCurrency(stat.revenue)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p>No daily analytics data</p>
                    )}
                </div>

                {/* Monthly Trends */}
                <div>
                    <h2>📅 Monthly Trends</h2>
                    {analytics.monthly_trends && analytics.monthly_trends.length > 0 ? (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                                <thead style={{ backgroundColor: '#6f42c1', color: 'white' }}>
                                    <tr>
                                        <th style={{ padding: '10px', textAlign: 'left' }}>Date</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Revenue</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Conversions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {analytics.monthly_trends.slice(0, 5).map((trend, index) => (
                                        <tr key={trend.date} style={{ borderBottom: '1px solid #dee2e6', backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white' }}>
                                            <td style={{ padding: '10px' }}>{trend.date}</td>
                                            <td style={{ padding: '10px', textAlign: 'right' }}>{formatCurrency(trend.revenue)}</td>
                                            <td style={{ padding: '10px', textAlign: 'right' }}>{formatNumber(trend.conversions)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p>No monthly trends data</p>
                    )}
                </div>
            </section>

            {/* Query Builder */}
            <section>
                <QueryBuilder />
            </section>
        </div>
    );
}

export default Dashboard;
