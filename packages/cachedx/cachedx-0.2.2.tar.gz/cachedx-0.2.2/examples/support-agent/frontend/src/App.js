/**
 * Main React App component for AI Support Agent Example
 */
import React from 'react';
import SupportChat from './components/SupportChat';
import './App.css';

function App() {
  return (
    <div className="App">
      <SupportChat userId="user123" />
    </div>
  );
}

export default App;
