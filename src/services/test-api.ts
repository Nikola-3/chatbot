import axios from 'axios';

const API_URL = 'http://localhost:3001';

export const fetchChatbotResponse = async (userInput: string) => {
    try {
        const response = await axios.post(`${API_URL}/chat`, { input: userInput });
        console.log(response.data);
        return response.data;
    } catch (error) {
        console.error('Error fetching chatbot response:', error);
        throw error;
    }
};