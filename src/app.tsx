import React from 'react';
import Chatbot from './components/chatbot';
import './styles/app.css';

const App: React.FC = () => {
    return (
        <div className="App">
            <h1>RAG Chatbot</h1>
            <Chatbot />
        </div>
    );
};

export default App;