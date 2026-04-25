## **Running and Inspecting a FastMCP Server**

FastMCP provides built-in utilities to **validate and inspect your MCP server locally** before integrating it with any client or LLM.

---

### **Step 1: Install FastMCP**

```bash
pip install fastmcp
```

---

### **Step 2: Implement a FastMCP Server**

Create your MCP server (e.g., `mcp-server.py`) with tool definitions using `FastMCP`.

---

### **Step 3: Inspect the Server (Static Validation)**

```bash
fastmcp inspect mcp-server.py
```

This step performs a **static inspection** of your server:
* Verifies that the server loads correctly
* Lists all registered tools
* Validates tool schemas (arguments, types, descriptions)

👉 This helps catch:
* registration issues
* schema mismatches
* missing type hints

---

### **Step 4: Launch the Inspector UI**

```bash
fastmcp dev inspector mcp-server.py
```

This starts an **interactive inspector interface** where you can:
* View available tools
* Manually invoke tools
* Test different inputs
* Inspect outputs and behavior in real time

---

### **Step 5: Build an LLM Application Using LangChain MCP Client**

Once the MCP server is validated using the inspector, the next step is to **integrate it into an LLM-powered application** using LangChain as the MCP host.

---

#### **Create an MCP Client in LangChain**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "local-mcp": {
        "transport": "stdio",
        "command": "/path/to/python",          # Python executable
        "args": ["/path/to/mcp-server.py"],    # MCP server file
    }
})
```

---

#### **Load Tools from MCP Server**

```python
tools = await client.get_tools()
```

This step:

* Connects to the MCP server
* Discovers all registered tools
* Converts them into LangChain-compatible tools

---

#### **Create the Agent**

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=tools,
)
```

---

#### **Invoke the Application**

```python
response = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": "What is 5 multiplied by 6?"}
    ]
})
```