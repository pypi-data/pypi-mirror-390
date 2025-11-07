/**
 * AI Support Chat component using PydanticAI agent with cachedx data
 */
import React, { useState, useEffect, useRef } from 'react';

function SupportChat({ userId = "user123" }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [systemStatus, setSystemStatus] = useState(null);
    const [sampleQuestions, setSampleQuestions] = useState([]);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        checkSystemStatus();
        loadSampleQuestions();
        // Add welcome message
        setMessages([{
            type: 'agent',
            content: `Hello! I'm your AI support agent. I have access to real-time data about your orders, account, and our inventory. How can I help you today?`,
            confidence: 1.0,
            data_sources: ['system'],
            suggested_actions: ['Ask about your orders', 'Check product availability', 'View account information']
        }]);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const checkSystemStatus = async () => {
        try {
            const response = await fetch('/support/data-stats');
            const data = await response.json();
            setSystemStatus(data);
        } catch (error) {
            console.error('Failed to check system status:', error);
        }
    };

    const loadSampleQuestions = async () => {
        try {
            const response = await fetch('/support/sample-queries');
            const data = await response.json();
            setSampleQuestions(data.sample_questions || []);
        } catch (error) {
            console.error('Failed to load sample questions:', error);
        }
    };

    const sendMessage = async (messageText = null) => {
        const messageToSend = messageText || input;
        if (!messageToSend.trim()) return;

        const userMessage = { type: 'user', content: messageToSend };
        setMessages(prev => [...prev, userMessage]);

        setLoading(true);
        setInput('');

        try {
            const response = await fetch('/support/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    question: messageToSend,
                    context: ""
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            const agentMessage = {
                type: 'agent',
                content: result.answer,
                confidence: result.confidence,
                data_sources: result.data_sources || [],
                suggested_actions: result.suggested_actions || []
            };

            setMessages(prev => [...prev, agentMessage]);

        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = {
                type: 'error',
                content: `Sorry, I encountered an error: ${error.message}. Please try again or contact human support.`
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const askSampleQuestion = (question) => {
        sendMessage(question);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const formatConfidence = (confidence) => {
        const percentage = Math.round(confidence * 100);
        let color = '#28a745'; // green
        if (percentage < 70) color = '#ffc107'; // yellow
        if (percentage < 50) color = '#dc3545'; // red
        return { percentage, color };
    };

    return (
        <div style={{
            maxWidth: '800px',
            margin: '0 auto',
            padding: '20px',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {/* Header */}
            <div style={{
                marginBottom: '20px',
                padding: '15px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <h1 style={{ margin: '0 0 10px 0' }}>🤖 AI Customer Support</h1>
                <p style={{ margin: '0', color: '#6c757d' }}>
                    Powered by <strong>PydanticAI</strong> + <strong>cachedx</strong> - Real-time data access
                </p>

                {/* System Status */}
                {systemStatus && (
                    <div style={{
                        marginTop: '10px',
                        padding: '8px 12px',
                        backgroundColor: systemStatus.openai_configured ? '#d4edda' : '#f8d7da',
                        borderRadius: '4px',
                        fontSize: '14px'
                    }}>
                        <strong>Status:</strong> {systemStatus.system_status} |
                        <strong> AI:</strong> {systemStatus.openai_configured ? '✅ Ready' : '❌ Not configured'} |
                        <strong> Data tables:</strong> {Object.keys(systemStatus.table_stats || {}).length}
                    </div>
                )}
            </div>

            {/* Sample Questions */}
            {sampleQuestions.length > 0 && messages.length <= 1 && (
                <div style={{
                    marginBottom: '20px',
                    padding: '15px',
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                    <h3 style={{ margin: '0 0 15px 0' }}>💡 Try asking me:</h3>
                    {sampleQuestions.map((category, categoryIndex) => (
                        <div key={categoryIndex} style={{ marginBottom: '15px' }}>
                            <h4 style={{ margin: '0 0 8px 0', color: '#007bff' }}>{category.category}</h4>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                {category.questions.map((question, questionIndex) => (
                                    <button
                                        key={questionIndex}
                                        onClick={() => askSampleQuestion(question)}
                                        style={{
                                            padding: '6px 12px',
                                            backgroundColor: '#f8f9fa',
                                            border: '1px solid #dee2e6',
                                            borderRadius: '20px',
                                            cursor: 'pointer',
                                            fontSize: '14px',
                                            transition: 'background-color 0.2s'
                                        }}
                                        onMouseOver={(e) => e.target.style.backgroundColor = '#e9ecef'}
                                        onMouseOut={(e) => e.target.style.backgroundColor = '#f8f9fa'}
                                    >
                                        {question}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Messages */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                marginBottom: '20px'
            }}>
                {messages.map((msg, index) => (
                    <div key={index} style={{
                        marginBottom: '15px',
                        display: 'flex',
                        justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start'
                    }}>
                        <div style={{
                            maxWidth: '70%',
                            padding: '12px 16px',
                            borderRadius: '18px',
                            backgroundColor: msg.type === 'user' ? '#007bff' :
                                           msg.type === 'error' ? '#dc3545' : 'white',
                            color: msg.type === 'user' ? 'white' :
                                   msg.type === 'error' ? 'white' : 'black',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}>
                            <div style={{ whiteSpace: 'pre-wrap' }}>
                                {msg.content}
                            </div>

                            {/* Agent metadata */}
                            {msg.type === 'agent' && msg.confidence !== undefined && (
                                <div style={{
                                    marginTop: '8px',
                                    padding: '8px',
                                    backgroundColor: '#f8f9fa',
                                    borderRadius: '8px',
                                    fontSize: '12px'
                                }}>
                                    <div style={{ marginBottom: '4px' }}>
                                        <strong>Confidence:</strong>
                                        <span style={{
                                            color: formatConfidence(msg.confidence).color,
                                            marginLeft: '4px'
                                        }}>
                                            {formatConfidence(msg.confidence).percentage}%
                                        </span>
                                    </div>

                                    {msg.data_sources && msg.data_sources.length > 0 && (
                                        <div style={{ marginBottom: '4px' }}>
                                            <strong>Data sources:</strong> {msg.data_sources.join(', ')}
                                        </div>
                                    )}

                                    {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                                        <div>
                                            <strong>Suggested actions:</strong>
                                            <ul style={{ margin: '4px 0 0 0', paddingLeft: '16px' }}>
                                                {msg.suggested_actions.map((action, i) => (
                                                    <li key={i}>{action}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div style={{
                        display: 'flex',
                        justifyContent: 'flex-start',
                        marginBottom: '15px'
                    }}>
                        <div style={{
                            padding: '12px 16px',
                            backgroundColor: 'white',
                            borderRadius: '18px',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                            color: '#6c757d'
                        }}>
                            🤖 Thinking... (accessing real-time data)
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div style={{
                display: 'flex',
                gap: '10px',
                padding: '15px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Ask me anything about your account, orders, or products... (Enter to send, Shift+Enter for new line)"
                    disabled={loading}
                    style={{
                        flex: 1,
                        padding: '10px',
                        border: '1px solid #ced4da',
                        borderRadius: '20px',
                        resize: 'none',
                        minHeight: '40px',
                        maxHeight: '100px',
                        fontFamily: 'inherit'
                    }}
                    rows={1}
                />
                <button
                    onClick={() => sendMessage()}
                    disabled={loading || !input.trim()}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: loading || !input.trim() ? '#6c757d' : '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '20px',
                        cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold'
                    }}
                >
                    {loading ? '⏳' : '📤'}
                </button>
            </div>

            {/* Footer */}
            <div style={{
                marginTop: '10px',
                textAlign: 'center',
                fontSize: '12px',
                color: '#6c757d'
            }}>
                User ID: {userId} | Powered by cachedx + PydanticAI
            </div>
        </div>
    );
}

export default SupportChat;
