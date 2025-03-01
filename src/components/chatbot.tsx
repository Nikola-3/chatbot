import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaperclip } from '@fortawesome/free-solid-svg-icons';
import Message, { MessageProps } from './message';
import { fetchChatbotResponse, uploadDocument } from '../services/api';
import LoadingOverlay from './loading-overlay';

const Chatbot: React.FC = () => {
    const [messages, setMessages] = useState<MessageProps[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSendMessage = async () => {
        if (input.trim()) {
            const newMessage: MessageProps = { sender: 'user-message', content: input };
            setMessages([...messages, newMessage]);
            setInput('');

            try {
                setLoading(true);
                const botResponse = await fetchChatbotResponse(input);
                const botMessage: MessageProps = { sender: 'bot-message', content: botResponse.response };
                setMessages((prevMessages) => [...prevMessages, botMessage]);
            } catch (error) {
                console.error('Error fetching chatbot response:', error);
            } finally {
                setLoading(false);
            }
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            setLoading(true);
            const response = await uploadDocument(file);
            const botMessage: MessageProps = { 
                sender: 'bot-message', 
                content: `File uploaded successfully: ${response.message}` 
            };
            setMessages(prevMessages => [...prevMessages, botMessage]);
        } catch (error) {
            const errorMessage: MessageProps = { 
                sender: 'bot-message', 
                content: 'Error uploading document. Please try again.' 
            };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            {loading && <LoadingOverlay />}
            <div className="messages">
                {messages.map((msg, index) => (
                    <Message key={index} sender={msg.sender} content={msg.content} />
                ))}
            </div>
            <div className="input-container">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyUp={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message..."
                    disabled={loading}
                />
                <button onClick={handleSendMessage} disabled={loading}>Send</button>
                <label className="file-upload">
                    <input
                        type="file"
                        onChange={handleFileUpload}
                        accept=".pdf,.txt,.doc,.docx"
                    />
                    <span className="file-upload-icon">
                        <FontAwesomeIcon icon={faPaperclip} />
                    </span>
                </label>
            </div>
        </div>
    );
};

export default Chatbot;