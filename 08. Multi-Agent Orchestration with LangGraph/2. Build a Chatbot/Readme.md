# **Memory**
https://docs.langchain.com/oss/python/concepts/memory

Memory is a system that remembers information about previous interactions. For AI agents, memory is crucial because it lets them remember previous interactions, learn from feedback, and adapt to user preferences.

Types of Memory:
1. Short Term
2. Long Term

Short-term memory tracks conversation history within a single thread/session, while long-term memory persists key facts across multiple conversations/sessions.

Short-term memory uses a **checkpointer** to store the full message history for one conversation thread. Each **thread_id** gets its own isolated history that persists across invocations within that thread.

Long-term memory uses a **store** for semantic search across all user data/sessions. It extracts and saves important facts (preferences, facts learned) that get retrieved by similarity search when relevant.

## **Short Term Memory (Thread Level Persistence)**

Ref: https://docs.langchain.com/oss/python/langchain/short-term-memory  

Short term memory lets your application remember previous interactions within a single thread or conversation.
> A thread organizes multiple interactions in a session, similar to the way email groups messages in a single conversation.

Conversation history is the most common form of short-term memory. Long conversations pose a challenge to today’s LLMs; a full history may not fit inside an LLM’s context window, resulting in an context loss or errors.

To add short-term memory (thread-level persistence) to an agent, you need to specify a **checkpointer** when creating an agent.

### **Installation**
```
pip install langgraph-checkpoint-postgres
```

### **Usage**
```python
from langchain.agents import create_agent

from langgraph.checkpoint.postgres import PostgresSaver  

DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup() # auto create tables in PostgresSql
    agent = create_agent(
        "gpt-5",
        tools=[get_user_info],
        checkpointer=checkpointer,  
    )
```

### **Customizing agent memory**
By default, agents use **AgentState** to manage short term memory, specifically the conversation history via a **messages** key.

You can extend **AgentState** to add additional fields. Custom state schemas are passed to **create_agent** using the **state_schema** parameter.

```python
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver


class CustomAgentState(AgentState):  
    user_id: str
    preferences: dict

agent = create_agent(
    "gpt-5",
    tools=[get_user_info],
    state_schema=CustomAgentState,  
    checkpointer=InMemorySaver(),
)

# Custom state can be passed in invoke
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "Hello"}],
        "user_id": "user_123",  
        "preferences": {"theme": "dark"}  
    },
    {"configurable": {"thread_id": "1"}})
```

### **Common patterns**
With short-term memory enabled, long conversations can exceed the LLM’s context window. Common solutions are:
1. Trim Messages
2. Delete Messages
3. Summarize Messages
4. Custom Strategies


















