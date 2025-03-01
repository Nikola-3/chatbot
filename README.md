# Simple Chatbot Application

This is a React application that implements a Retrieval-Augmented Generation (RAG) chatbot. The chatbot is designed to provide enhanced responses by retrieving relevant information from a backend service.

## Project Structure

```
chatbot
├── backend
│   └── server.js           # Backend server file
├── public
│   ├── index.html          # Main HTML file for the React application
│   ├── manifest.json       # Metadata for Progressive Web App features
│   ├── icon-192x192.png    # Placeholder icon file (192x192)
│   └── icon-512x512.png    # Placeholder icon file (512x512)
├── src
│   ├── components          # Contains React components
│   │   ├── chatbot.tsx     # Main chatbot interface component
│   │   └── message.tsx     # Component for individual chat messages
│   ├── services            # Contains API service functions
│   │   └── api.ts          # Functions for making API calls
│   ├── app.tsx             # Main application component
│   ├── index.tsx           # Entry point for the React application
│   └── styles              # Contains CSS styles
│       └── app.css         # Styles for the application
├── package.json            # npm configuration file
├── tsconfig.json           # TypeScript configuration file
└── README.md               # Project documentation
```

## Setup Instructions

### Frontend

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd chatbot
   ```

2. **Install dependencies:**
   ```
   yarn install
   ```

3. **Run the frontend:**
   ```
   yarn parcel serve index.html --port 3000 --host localhost
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000` to view the application.

### Backend

1. Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY=your-actual-api-key
```

2. Copy the environment template:
```bash
cd backend
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key:
```properties
OPENAI_API_KEY=your-actual-api-key
```

4. Configure other environment variables as needed

5. **Run the backend:**
   ```
    uvicorn main:app --port --loop asyncio 3001
   ```

6. **Run the backend for dev:**
   ```
    uvicorn main:app --reload --loop asyncio --port 3001
   ```

7. **Run a fake backend for testing frontend
   ```
    node --loader ts-node/esm ./backend/test-server.ts
   ```

8. **IMPORTANT NOTE**
uvicorn's default async loop uvloop doesn't seem to work correctly with asyncpg, so 
the database can't be set up properly with it, using --loop asyncio seems to be
necessary.

## Database Setup

### PostgreSQL
This project requires PostgreSQL as its main database. Here's how to set it up:

1. Install PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Start PostgreSQL service:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Optional: start on boot
```

3. Create database and user:
```bash
# Switch to postgres user
sudo -i -u postgres

# Create database
createdb chatbot

# Create user and set permissions (in psql)
psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE chatbot TO postgres;"
```

4. Verify connection:
```bash
psql -h localhost -U postgres -d chatbot
# Enter password when prompted: postgres
```

5. Configure environment variables in `.env`:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=chatbot
```

## Data Storage

The application uses the following directory structure for data:

```
backend/data/
├── documents/     # Stored uploaded files
└── vector_store/ # ChromaDB vector embeddings
```

These directories are automatically created when needed. You can configure their locations in the `.env` file.

## Usage Guidelines

- Interact with the chatbot by typing your queries in the input field.
- The chatbot will respond with generated answers based on the retrieved information from the backend service.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the GNU General Public License.