"""
Customer Support Chatbot using LangGraph
Based on: https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/
"""

import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain.tools import tool
from langchain_core.tools import BaseTool
import json

# Load environment variables
load_dotenv()

# Define the state schema
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    next: str

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Define tools for the customer support agent
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information about products and services."""
    # Simulated knowledge base - in a real implementation, this would connect to a database
    knowledge_base = {
        "return policy": "Our return policy allows returns within 30 days of purchase with original receipt.",
        "shipping": "Standard shipping takes 3-5 business days. Express shipping is available for an additional fee.",
        "warranty": "All products come with a 1-year manufacturer warranty.",
        "payment": "We accept all major credit cards, PayPal, and Apple Pay.",
        "account": "You can create an account on our website to track orders and save payment information.",
        "refund": "Refunds are processed within 5-7 business days after we receive your return.",
        "tracking": "You can track your order using the tracking number provided in your confirmation email.",
        "contact": "You can reach our customer service team at support@company.com or call 1-800-123-4567."
    }
    
    query_lower = query.lower()
    for key, value in knowledge_base.items():
        if key in query_lower:
            return value
    
    return "I couldn't find specific information about that. Please contact our support team for assistance."

@tool
def create_support_ticket(issue: str, customer_email: str) -> str:
    """Create a support ticket for complex issues that require human intervention."""
    # Simulated ticket creation
    ticket_id = f"TICKET-{len(issue) + len(customer_email)}"
    return f"Support ticket {ticket_id} has been created for your issue: '{issue}'. A representative will contact you at {customer_email} within 24 hours."

@tool
def check_order_status(order_number: str) -> str:
    """Check the status of an order using the order number."""
    # Simulated order status check
    if order_number and len(order_number) > 5:
        return f"Order {order_number} is currently being processed and will ship within 2-3 business days."
    else:
        return "Invalid order number. Please provide a valid order number to check status."

# Create tool executor
tools = [search_knowledge_base, create_support_ticket, check_order_status]
tool_executor = ToolExecutor(tools)

# Define the agent nodes
def should_continue(state: AgentState) -> str:
    """Determine if the conversation should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if the user wants to end the conversation
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        if any(phrase in content for phrase in ["goodbye", "bye", "end", "stop", "thank you", "thanks"]):
            return "end"
    
    return "continue"

def call_model(state: AgentState) -> AgentState:
    """Call the LLM to generate a response."""
    messages = state["messages"]
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful customer support agent for an e-commerce company. 
        You can help with order status, returns, shipping, warranties, and general inquiries.
        Always be polite and professional. If you need to use tools to help the customer, do so.
        If the issue is too complex, create a support ticket."""),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = prompt | llm.bind_tools(tools)
    
    # Get the response
    response = agent.invoke({
        "messages": messages,
        "agent_scratchpad": []
    })
    
    # Add the response to the messages
    new_messages = list(messages) + [response]
    
    return {"messages": new_messages}

def call_tool(state: AgentState) -> AgentState:
    """Call a tool and add the result to the messages."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Extract tool calls from the last message
    tool_calls = last_message.tool_calls
    
    # Execute each tool call
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Execute the tool
        result = tool_executor.invoke({
            "name": tool_name,
            "arguments": tool_args
        })
        
        # Add the tool result to messages
        messages.append(AIMessage(
            content=f"Tool {tool_name} returned: {result}",
            tool_calls=[tool_call]
        ))
    
    return {"messages": messages}

# Create the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tool)

# Add edges
workflow.add_edge("agent", should_continue)
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()

# Function to run the chatbot
def run_chatbot():
    """Run the customer support chatbot."""
    print("🤖 Customer Support Chatbot")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    # Initialize the state
    state = {"messages": []}
    
    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("🤖 Thank you for using our customer support! Goodbye!")
            break
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))
        
        # Run the workflow
        result = app.invoke(state)
        
        # Get the last AI message
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        if ai_messages:
            last_ai_message = ai_messages[-1]
            print(f"🤖 Assistant: {last_ai_message.content}")
        
        # Update state for next iteration
        state = result

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        run_chatbot() 