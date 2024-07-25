import streamlit as st
from openai import OpenAI

# Read the API Key and Setup an OpenAI Client
f = open("keys/.openai_api_key.txt")
key = f.read()
model = OpenAI(api_key=key)

st.title("💬AI Chatbot")

# Synatx: st.chat_message("ROLE").write("MESSAGE")
st.chat_message("assistant").write("Hi, How may I help you?")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# For taking user inputs
user_input = st.chat_input()

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    #### What Next? ####
    response = model.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": """ You are a helpful AI Assistant who answers all the user queries politely. If someone asks your name, tell them that your name is "Chiti The Robot". """}
            ] + st.session_state["messages"] + [
            {"role": "user", "content": user_input}
        ]
    )
    
    st.session_state["memory"].append({"role": "assistant", "content": response.choices[0].message.content})

    st.chat_message("ai").write(response.choices[0].message.content)




