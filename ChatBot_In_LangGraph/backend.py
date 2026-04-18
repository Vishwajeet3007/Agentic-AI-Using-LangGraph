from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# --- Load .env file ---
load_dotenv()

# --- Configure Google Generative AI ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Initialize the LLM ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# --- Define the chat state ---
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# --- Node function ---
def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# --- Configure checkpoint memory ---
checkpointer = InMemorySaver()

# --- Build the graph ---
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# --- Compile chatbot with checkpoint ---
chatbot = graph.compile(checkpointer=checkpointer)

# --- Interactive loop ---
print("✅ Chatbot ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    # Create state with user message
    state = {"messages": [HumanMessage(content=user_input)]}

    # Required checkpoint config
    config = {
        "thread_id": "chat_1",          # unique ID per chat session
        "checkpoint_ns": "chatbot_demo", 
        "checkpoint_id": "latest"
    }

    # Invoke chatbot
    output = chatbot.invoke(state, config=config)

    # Print bot response
    bot_message = output["messages"][-1].content
    print(f"Bot: {bot_message}\n")
