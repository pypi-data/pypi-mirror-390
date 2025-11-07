/**
 * SQL Query Builder component for running custom queries against cached data
 */
import React, { useState, useEffect } from 'react';
import dashboardAPI from '../api/dashboardAPI';

function QueryBuilder() {
    const [sql, setSql] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [sampleQueries, setSampleQueries] = useState([]);
    const [showSchema, setShowSchema] = useState(false);
    const [schema, setSchema] = useState('');

    useEffect(() => {
        loadSampleQueries();
    }, []);

    const loadSampleQueries = async () => {
        try {
            const data = await dashboardAPI.getSampleQueries();
            setSampleQueries(data.queries || []);
        } catch (err) {
            console.error('Failed to load sample queries:', err);
        }
    };

    const loadSchema = async () => {
        try {
            const data = await dashboardAPI.getSchema();
            setSchema(data.schema_context || 'No schema available');
            setShowSchema(true);
        } catch (err) {
            console.error('Failed to load schema:', err);
            setError('Failed to load schema information');
        }
    };

    const executeQuery = async () => {
        if (!sql.trim()) {
            setError('Please enter a SQL query');
            return;
        }

        try {
            setLoading(true);
            setError(null);

            const result = await dashboardAPI.runCustomQuery(sql);
            setResults(result);

        } catch (err) {
            console.error('Query execution failed:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const applySampleQuery = (query) => {
        setSql(query.sql);
        setResults(null);
        setError(null);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            executeQuery();
        }
    };

    return (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2>🔍 SQL Query Builder</h2>
            <p>Run custom SQL queries against your cached data. Only SELECT queries are allowed for security.</p>

            {/* Controls */}
            <div style={{ marginBottom: '15px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                <button
                    onClick={loadSchema}
                    style={{
                        padding: '8px 12px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Show Schema
                </button>
            </div>

            {/* Sample Queries */}
            {sampleQueries.length > 0 && (
                <div style={{ marginBottom: '20px' }}>
                    <h3>📋 Sample Queries</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '10px' }}>
                        {sampleQueries.map((query, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '10px',
                                    backgroundColor: '#f8f9fa',
                                    border: '1px solid #dee2e6',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    transition: 'background-color 0.2s'
                                }}
                                onClick={() => applySampleQuery(query)}
                                onMouseOver={(e) => e.target.style.backgroundColor = '#e9ecef'}
                                onMouseOut={(e) => e.target.style.backgroundColor = '#f8f9fa'}
                            >
                                <strong>{query.name}</strong>
                                <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#6c757d' }}>
                                    {query.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Schema Display */}
            {showSchema && (
                <div style={{ marginBottom: '20px' }}>
                    <h3>📊 Database Schema</h3>
                    <div style={{
                        backgroundColor: '#f8f9fa',
                        border: '1px solid #dee2e6',
                        borderRadius: '4px',
                        padding: '15px',
                        maxHeight: '300px',
                        overflowY: 'auto'
                    }}>
                        <pre style={{ margin: 0, fontSize: '12px', whiteSpace: 'pre-wrap' }}>
                            {schema}
                        </pre>
                    </div>
                    <button
                        onClick={() => setShowSchema(false)}
                        style={{
                            marginTop: '10px',
                            padding: '4px 8px',
                            backgroundColor: '#6c757d',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                        }}
                    >
                        Hide Schema
                    </button>
                </div>
            )}

            {/* SQL Input */}
            <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    SQL Query (Ctrl/Cmd + Enter to execute):
                </label>
                <textarea
                    value={sql}
                    onChange={(e) => setSql(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="SELECT * FROM users LIMIT 10;"
                    style={{
                        width: '100%',
                        height: '100px',
                        padding: '10px',
                        border: '1px solid #ced4da',
                        borderRadius: '4px',
                        fontFamily: 'monospace',
                        fontSize: '14px',
                        resize: 'vertical'
                    }}
                />
            </div>

            {/* Execute Button */}
            <button
                onClick={executeQuery}
                disabled={loading || !sql.trim()}
                style={{
                    padding: '10px 20px',
                    backgroundColor: loading ? '#6c757d' : '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    marginBottom: '20px'
                }}
            >
                {loading ? 'Executing...' : 'Execute Query'}
            </button>

            {/* Error Display */}
            {error && (
                <div style={{
                    padding: '10px',
                    backgroundColor: '#f8d7da',
                    border: '1px solid #f5c6cb',
                    borderRadius: '4px',
                    color: '#721c24',
                    marginBottom: '20px'
                }}>
                    <strong>Error:</strong> {error}
                </div>
            )}

            {/* Results Display */}
            {results && (
                <div>
                    <h3>📊 Query Results</h3>

                    {/* Result Metadata */}
                    <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#d4edda', borderRadius: '4px' }}>
                        <strong>Success:</strong> {results.success ? '✅' : '❌'} |
                        <strong> Rows:</strong> {results.row_count || 0} |
                        <strong> Execution Time:</strong> {results.execution_time_ms || 0}ms

                        {results.warnings && results.warnings.length > 0 && (
                            <div style={{ marginTop: '5px' }}>
                                <strong>Warnings:</strong>
                                <ul style={{ margin: '5px 0 0 20px' }}>
                                    {results.warnings.map((warning, index) => (
                                        <li key={index}>{warning}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Results Table */}
                    {results.success && results.data && results.data.length > 0 ? (
                        <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                            <table style={{
                                width: '100%',
                                borderCollapse: 'collapse',
                                backgroundColor: 'white',
                                border: '1px solid #dee2e6'
                            }}>
                                <thead style={{ backgroundColor: '#e9ecef', position: 'sticky', top: 0 }}>
                                    <tr>
                                        {Object.keys(results.data[0]).map((column) => (
                                            <th key={column} style={{
                                                padding: '8px',
                                                textAlign: 'left',
                                                borderBottom: '2px solid #dee2e6',
                                                fontSize: '14px',
                                                fontWeight: 'bold'
                                            }}>
                                                {column}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.data.map((row, rowIndex) => (
                                        <tr key={rowIndex} style={{
                                            borderBottom: '1px solid #dee2e6',
                                            backgroundColor: rowIndex % 2 === 0 ? '#f8f9fa' : 'white'
                                        }}>
                                            {Object.values(row).map((value, cellIndex) => (
                                                <td key={cellIndex} style={{
                                                    padding: '8px',
                                                    fontSize: '13px',
                                                    maxWidth: '200px',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    whiteSpace: 'nowrap'
                                                }}>
                                                    {value === null ? (
                                                        <span style={{ color: '#6c757d', fontStyle: 'italic' }}>NULL</span>
                                                    ) : (
                                                        String(value)
                                                    )}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : results.success ? (
                        <p style={{ fontStyle: 'italic', color: '#6c757d' }}>Query executed successfully but returned no data.</p>
                    ) : null}
                </div>
            )}
        </div>
    );
}

export default QueryBuilder;
