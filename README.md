# ✈️ Flight Search AI Chat

An intelligent conversational API that uses Claude AI with tool use to search and recommend flights in natural language.

## 🚀 Demo

```bash
POST http://localhost:8000/chat

{
  "message": "Find flights from GRU to JFK on May 1st, 2026",
  "session_id": "test-01"
}
```

```json
{
  "reply": "I found 5 flight options from GRU to JFK on May 1st...",
  "session_id": "test-01",
  "tools_used": ["search_flights"]
}
```

## 🧠 How It Works

This project uses **Claude's native tool use** to bridge natural language and flight search:

```
User message
     ↓
Claude analyzes intent
     ↓
Decides to call search_flights tool
     ↓
Tool executes flight search
     ↓
Result returned to Claude
     ↓
Claude formats natural language response
```

## 🛠️ Tech Stack

- **Python** — core language
- **FastAPI** — REST API framework
- **Anthropic Claude API** — LLM orchestration with tool use
- **Tool Use** — `search_flights` tool with JSON schema

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/flight-search-ai-chat
cd flight-search-ai-chat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_api_key_here
```

## ▶️ Running

```bash
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`

## 📡 API Reference

### POST `/chat`

Send a message to the flight search assistant.

**Request:**
```json
{
  "message": "string",
  "session_id": "string"
}
```

**Response:**
```json
{
  "reply": "string",
  "session_id": "string",
  "tools_used": ["string"]
}
```

**Example queries:**
```
"Find the cheapest flight from São Paulo to New York next Friday"
"Compare flights from GRU to LHR in June"
"What are my options to fly to Berlin in May with one stop?"
```

## 🔧 Tool Schema

The `search_flights` tool follows JSON Schema specification:

```json
{
  "name": "search_flights",
  "description": "Search for available flights between two airports",
  "input_schema": {
    "type": "object",
    "properties": {
      "origin": { "type": "string", "description": "IATA airport code (e.g. GRU)" },
      "destination": { "type": "string", "description": "IATA airport code (e.g. JFK)" },
      "date": { "type": "string", "description": "Departure date in YYYY-MM-DD format" },
      "passengers": { "type": "integer", "description": "Number of passengers", "default": 1 }
    },
    "required": ["origin", "destination", "date"]
  }
}
```

## 📁 Project Structure

```
flight-search-ai-chat/
├── main.py              # FastAPI app and routes
├── orchestrator.py      # Claude tool use orchestration
├── tools/
│   └── search_flights.py  # Flight search tool implementation
├── schemas.py           # Tool JSON schemas
├── requirements.txt
└── README.md
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | ✅ |

## 📋 Requirements

```
fastapi
uvicorn
anthropic
python-dotenv
```

## 📄 License

MIT
