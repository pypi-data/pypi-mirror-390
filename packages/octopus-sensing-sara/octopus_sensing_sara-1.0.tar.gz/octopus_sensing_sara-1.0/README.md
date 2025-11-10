# Octopus Sensing SARA

An empathetic conversational AI companion with persistent memory, user profiling, and multi-LLM support. Part of the [Octopus Sensing](https://github.com/octopus-sensing) project ecosystem.

Built with FastAPI, LangChain, and React.

---

## Features

- 🧠 **Empathetic AI** - Emotionally intelligent responses with advanced prompt engineering
- 💾 **Persistent Memory** - SQLite storage for conversations and user profiles
- 👤 **User Profiling** - Automatic extraction of preferences and personal information
- 🔌 **Multi-LLM Support** - OpenAI, Anthropic (Claude), Google Gemini, and Ollama
- 📝 **Auto-Summarization** - Long-term conversation summaries for context retention
- 🚀 **Production-Ready** - Docker deployment, type safety, async API
- 🎨 **Modern UI** - React frontend with shadcn/ui components

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API key for your LLM provider (OpenAI, Anthropic, or Google)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/octopus-sensing/octopus-sensing-sara.git
   cd octopus-sensing-sara
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   ```

3. **Add your API key to `.env`**

   ```bash
   # Choose your provider
   LLM_PROVIDER=gemini
   LLM_MODEL=models/gemini-2.5-flash
   GOOGLE_API_KEY=your-api-key-here
   ```

4. **Start the application**

   ```bash
   docker compose up --build
   ```

5. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Configuration

Configure SARA by editing the `.env` file:

| Variable                             | Description                   | Example                                             |
| ------------------------------------ | ----------------------------- | --------------------------------------------------- |
| `LLM_PROVIDER`                       | AI provider                   | `openai`, `anthropic`, `gemini`, `ollama`           |
| `LLM_MODEL`                          | Model name                    | `models/gemini-2.5-flash`, `gpt-4`, `claude-3-opus` |
| `LLM_TEMPERATURE`                    | Response creativity (0-2)     | `0.7`                                               |
| `LLM_MAX_TOKENS`                     | Max response length           | `2000`                                              |
| `SHORT_TERM_MEMORY_WINDOW`           | Recent messages to remember   | `10`                                                |
| `LONG_TERM_MEMORY_SUMMARY_THRESHOLD` | Messages before summarization | `50`                                                |

### LLM Provider Setup

**Google Gemini (Free Tier)**

```bash
LLM_PROVIDER=gemini
LLM_MODEL=models/gemini-2.5-flash
GOOGLE_API_KEY=your-google-api-key
```

**OpenAI**

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=sk-your-openai-key
```

**Anthropic Claude**

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

---

## API Reference

### Send Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, I need help with something."
  }'
```

### Get User Profile

```bash
curl http://localhost:8000/user/user123/profile
```

### Get Conversation History

```bash
curl http://localhost:8000/conversation/{session_id}
```

**Full API documentation**: http://localhost:8000/docs

---

## Architecture

```
┌─────────────────┐
│  React Frontend │
└────────┬────────┘
         │
┌────────▼────────┐
│   FastAPI REST  │
└────────┬────────┘
         │
┌────────▼──────────────────────────┐
│   Conversation Service             │
│   • Process messages               │
│   • Extract user info              │
│   • Manage memory & summarization  │
└────────┬──────────────────────────┘
         │
┌────────▼────────┬──────────┬──────────┐
│ Memory Service  │  User    │   LLM    │
│                 │ Service  │ Factory  │
└────────┬────────┴────┬─────┴────┬─────┘
         │             │          │
┌────────▼─────────────▼──────────▼─────┐
│     SQLite Database (Persistent)       │
│  • Conversations  • Users  • Messages  │
└────────────────────────────────────────┘
```

---

## Project Structure

```
octopus-sensing-sara/
├── server/
│   ├── octopus_sensing_sara/
│   │   ├── api/              # REST endpoints
│   │   ├── core/             # Config, LLM factory
│   │   ├── prompts/          # Modular prompt system
│   │   │   ├── system_prompt/
│   │   │   ├── summarization_prompt/
│   │   │   └── extraction_prompt/
│   │   ├── models/           # Database & schemas
│   │   ├── services/         # Business logic
│   │   ├── storage/          # Database layer
│   │   ├── main.py           # FastAPI app
│   │   └── run.py            # Entry point
│   ├── tests/
│   └── Dockerfile
│
├── octopus_sensing_sara_ui/
│   ├── src/
│   │   ├── components/       # UI components
│   │   └── pages/            # Page components
│   └── Dockerfile
│
├── docker-compose.yml
├── pyproject.toml              # Poetry configuration & dependencies
└── poetry.lock
```

---

## How It Works

### 1. **Empathetic Conversations**

SARA uses advanced prompt engineering to:

- Recognize emotional states from user messages
- Validate feelings before offering solutions
- Adapt tone based on user's emotional context
- Maintain warm, supportive communication

### 2. **Memory System**

**Short-Term Memory**

- Last 10 messages kept in memory
- Provides immediate conversation context
- Cached per session

**Long-Term Memory**

- All conversations stored in SQLite
- User profiles with extracted facts
- Automatic summarization after 50 messages

### 3. **User Profiling**

SARA automatically extracts and remembers:

- Name and personal details
- Preferences and interests
- Conversation history
- Emotional patterns

This data personalizes future interactions.

### 4. **Modular Prompts**

Prompts are organized by function:

- `system_prompt/` - SARA's core personality
- `summarization_prompt/` - Conversation summaries
- `extraction_prompt/` - User information extraction

Each uses LangChain templates for consistency.

---

## Docker Commands

**Start application**

```bash
docker compose up -d
```

**View logs**

```bash
docker compose logs -f backend
```

**Restart after changes**

```bash
docker compose restart backend
```

**Stop application**

```bash
docker compose down
```

**Clean database (fresh start)**

```bash
./clean.sh
```

---

## Development

### Local Setup (without Docker)

**Backend**

```bash
# Using Poetry (recommended)
poetry install
poetry run python -m octopus_sensing_sara.run

# OR using venv + pip
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ..  # Install from pyproject.toml
python -m octopus_sensing_sara.run
```

**Frontend**

```bash
cd octopus_sensing_sara_ui
npm install
npm run dev
```

### Adding a New LLM Provider

1. Add API key field to `server/octopus_sensing_sara/core/config.py`
2. Add provider logic to `server/octopus_sensing_sara/core/llm_factory.py`
3. Update `docker-compose.yml` environment variables
4. Add to `.env` file

---

## Tech Stack

FastAPI • LangChain • React • SQLite • Docker • Poetry
