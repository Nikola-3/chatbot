# Chatbot Architecture Overview

## Workflow
I adopted a simple workflow:

1. User sends a message to chatbot via frontend
2. The message is sent to backend via an http request
3. The message is stored, embdedded with ada-002 and processed against history for relevant context
4. It is then sent along with relevant context to gpt-3.5-turbo for a response
5. response is forwarded to user

The user may upload documents, currently held on the file system, which are stored and their contents vectorised and tokenised for ease of relevance querying of context in any future query.

## Overall Design

The application has four layers:

1. **Storage**
2. **Processing**
3. **FastAPI**
4. **Frontend UI**

1., 2. and 3. are in Python because it has by far the most comprehensive libraries supporting AI/LLM/NLP functionality.

4. is a simple React app

## Implementation Details

### 1. Storage Layer
The storage layer separates the data by category: File / Content and File Metadata / Content and unifies them with a simple manager class. Currently, it's messy in the sense that the behaviour is not isolated top down. The storage manager is intended to provide an abstraction layer, so that different storage strategies may be used in the future. This is somewhat achieved with the combination with the interface, however the choice of sqlalchemy made the interface's abstraction usefulness limited.

### 2. Processing Layer
The processing layer ended up being convoluted despite the simplicity. I did not use the ProcessingProgress class in the end. The layer is meant to streamline file processing. This is achieved, asynchronously, with a lot of pain. Testing is difficult, some tests do not work because of the choice to make the file system asynchronous, there is a fix but it would take time. It uses a manager to build a prompt, given a query. It also uses a manager for the conversation history, to increase relevance of queries relative to the most recently had conversation. 

The processing itself is simple:
- receive message or document → process the relevant item
- If message → make a query → embed it → remember it → fetch relevant context → complete the query with open ai
- If document → save it → extract text → vectorise → save embedding for relevance querying
- In both cases → respond to user

### 3. FastAPI Layer
The fastapi app is a simple implementation of 3 endpoints, two of which are in use. `/chat` for message post requests and `/document/upload` for uploading files. They rely on the manager's in the processing layer to interact with the backend and are straighforward.

### 4. Frontend UI Layer
Very simple react app with a couple of components. It intends to mimic the chatgpt look, but not. I chose to block new input, though it could have been displayed more gracefully, while waiting for a response from the backend. This was inspired by chatgpt as well, since it is easier to block new requests than maintaining a queue of unfulfilled requests.

## TODO

### Security
1. Authentication
2. File validation and verification, virus scanning...
3. Cloudflare layer for user access
4. User access control and management
5. Storage safety, currently I just store the files and data directly
6. API upload safety, currently anyone can just send any request to the endpoints 
7. Cleaning up stale data, the functionality is mostly implemented, but it needs to be used periodically, or when a file size limit is reached
8. BYOK - allow user's organisation to provide API keys and models for the bot to use, ideally the bot is just highly customised middleware between llm's and companies as consumers

### Architecture
1. Use abstraction layer to isolate app from openai's API, e.g. with langchain
2. Redesign storage to use more transactional style writes to guarantee their atomicity
3. Allow for concurrency of requests from different users with a publisher/subscriber pattern
4. Per user rate limiting, by designing a user tracking system
5. Containerisation to make the app more platform agnostic, e.g. with docker
6. Make the layers communicate strictly through interface level functionality
7. Allow for larger files by streaming them
8. Consider continuous conversation and response token streaming via websockets, this would allow making requests that exceed single response token threshold
9. Logging - the app needs more logs, the logging module seems useful, I just didn't have the time to make it available. It would probably have been easy if I had done it from the start...
10. Observability - I really like sentry for error tracking and integrating the bot with something like splunk would allow more observability of how others use it
11. Consider supporting queued requests

### Optimisations
1. Currently I use ada-002 to embed the queries and then chromadb's query does a knn walk through the relevant data. However, there are a variety of query optimisation strategies that can be performed, for example query expansion (synonym, semantic, llm's can do it too), building and searching knowledge graphs with the uploaded documents and the query...
2. Query caching could help with repeated request response time and reduce load on the llm
3. Query complexity analysis - if the query is simple enough and doesn't require context, I could save time by directly forwarding to the llm
4. Database cache - within a short period of time, I would expect the same context to be brought up, so caching contextual data fetches might be useful, less relevant context, much faster response
5. Request compression and decompression, compressing sending a compressed file and decompressing may be faster than sending a large http request
6. Consider shipping the backend as a compiled python app instead
7. Use Http/2 (or maybe even Http/3) for faster client<->server communication

### Frontend
1. Currently the entire conversation is blocked while waiting on a response, instead it should just be the input container

### Quality of Life
1. There are commands I run that could be made into `package.json` scripts or put togething into bash scripts
2. pylint didn't work properly in my vscode
3. I could probably refactor some of the .py files in the backend into a single dataclass file
4. I could make the devloop faster in case of system testing by setting up a job that executes a task whenever I tell it to and run it through the terminal rather than using the UI to do the testing
5. More tests would make the devloop faster in some cases

### Testing
1. Using asyncio and file system inputs makes testing hard because not everything is easy to mock
2. There are some unit tests, but they are not exhaustive of the possible cases
3. Missing integration tests
4. Missing end to end tests
5. Missing frontend component tests with playwright/selenium