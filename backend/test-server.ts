// TS server emulating backend for quick frontend testing
import express, { Request, Response } from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

app.post('/chat', (req: Request, res: Response) => {
    const userInput: string = req.body.input;
    // Simulate a chatbot response
    const botResponse: string = `${userInput}`;
    res.json({ response: botResponse });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
