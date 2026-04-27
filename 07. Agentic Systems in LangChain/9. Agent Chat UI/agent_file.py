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