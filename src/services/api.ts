import axios from 'axios';

const API_URL = 'http://localhost:3001';

export interface ChatMessage {
    content: string;
}

export interface ChatResponse {
    response: string;
    sources: string[];
}

export async function fetchChatbotResponse(userInput: string): Promise<ChatResponse> {
    try {
        const response = await axios.post(`${API_URL}/chat`, { content: userInput });
        return response.data;
    } catch (error) {
        console.error('Error fetching chatbot response:', error);
        throw error;
    }
}

export async function uploadDocument(file: File): Promise<{ status: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await axios.post(`${API_URL}/documents/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading document:', error);
        throw error;
    }
}