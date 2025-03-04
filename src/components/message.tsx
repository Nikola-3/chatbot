import React from 'react';

export interface MessageProps {
    sender: 'user-message' | 'bot-message';
    content: string;
}

const Message: React.FC<MessageProps> = ({ sender, content }) => {
const messageClass = sender === 'user-message' ? 'user-message' : 'bot-message';
    return (
        <div className={`message ${messageClass}`}>
            <span className="sender"></span>
            <span className="content">{content}</span>
        </div>
    );
};

export default Message;