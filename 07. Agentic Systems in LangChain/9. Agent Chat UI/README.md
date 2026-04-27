# Deploying and Connecting Your LangGraph Agent

This document outlines the workflow for implementing, deploying, and connecting your LangGraph agent to the Agent Chat UI.

## Step 1: Create your agent implementation
Define your LangGraph workflow in a Python file (e.g., `graph.py`). Ensure your `StateGraph` object is compiled and exported so the CLI can access it.

```python
// agent_file.py
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

search_tool = DuckDuckGoSearchRun()

# Setup API Key
f = open('keys/.openai_api_key.txt')
OPENAI_API_KEY = f.read()

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0.0
)

agent_object = create_agent(
    model=llm,
    tools=[search_tool],
    system_prompt="You are a web search tool. Given a user query about recent events, you can refernce a websearch tool and answer the queries."
)
```

## Step 2: Create `langgraph.json`
Create a `langgraph.json` file in your project root. This configuration maps the CLI to your graph implementation and specifies dependency management.

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "agent_file:agent_object"
  }
  "env": ".env"
}
```

*   `dependencies`: Points to your local package (current directory).
*   `graphs`: Maps the name `agent` to the object `agent_object` inside `agent_file.py`.
*   `env`: Specifies the path to your environment variables file.

## Step 3: Install LangGraph CLI and LangGraph API
Install the necessary components to run the Agent Server and manage your deployments.

```bash
pip install langgraph-cli langgraph-api
```

## Step 4: Run the development server
Start the local server using the LangGraph CLI. This serves your graph via API and provides a local development UI.

```bash
langgraph dev
```

The terminal will confirm the server is running, typically at `http://localhost:2024`.

## Step 5: Connect to Agent Chat UI
Once the server is running, you can connect an external UI to your local API.

1.  Navigate to [https://agentchat.vercel.app](https://agentchat.vercel.app).
2.  In the configuration prompt, enter your local server URL: `http://localhost:2024`.
3.  Click **Continue** to establish the connection and begin interacting with your agent.