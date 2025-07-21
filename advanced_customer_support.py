"""
Advanced Customer Support Chatbot using LangGraph
Enhanced version with better state management and routing
"""

import os
from typing import TypedDict, Annotated, Sequence, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
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
    customer_info: dict
    conversation_summary: str

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
    knowledge_base = {
        "return policy": "Our return policy allows returns within 30 days of purchase with original receipt. Items must be in original condition.",
        "shipping": "Standard shipping takes 3-5 business days. Express shipping (1-2 days) is available for $15.99. Free shipping on orders over $50.",
        "warranty": "All products come with a 1-year manufacturer warranty. Extended warranties are available for purchase.",
        "payment": "We accept all major credit cards, PayPal, Apple Pay, and Google Pay. Payment plans available for orders over $200.",
        "account": "You can create an account on our website to track orders, save payment information, and access exclusive deals.",
        "refund": "Refunds are processed within 5-7 business days after we receive your return. You'll receive an email confirmation.",
        "tracking": "You can track your order using the tracking number provided in your confirmation email or in your account dashboard.",
        "contact": "You can reach our customer service team at support@company.com or call 1-800-123-4567. Live chat available 24/7.",
        "hours": "Our customer service is available Monday-Friday 8AM-8PM EST, Saturday 9AM-6PM EST, and Sunday 10AM-6PM EST.",
        "cancellation": "You can cancel your order within 1 hour of placing it. After that, contact customer service immediately."
    }
    
    query_lower = query.lower()
    for key, value in knowledge_base.items():
        if key in query_lower:
            return value
    
    return "I couldn't find specific information about that topic. Please contact our support team for assistance."

@tool
def create_support_ticket(issue: str, customer_email: str, priority: str = "medium") -> str:
    """Create a support ticket for complex issues that require human intervention."""
    ticket_id = f"TICKET-{len(issue) + len(customer_email)}"
    priority_levels = {"low": "24-48 hours", "medium": "12-24 hours", "high": "4-8 hours", "urgent": "1-2 hours"}
    response_time = priority_levels.get(priority.lower(), "12-24 hours")
    
    return f"Support ticket {ticket_id} has been created with {priority} priority. A representative will contact you at {customer_email} within {response_time}."

@tool
def check_order_status(order_number: str) -> str:
    """Check the status of an order using the order number."""
    if not order_number or len(order_number) < 6:
        return "Invalid order number. Please provide a valid order number (minimum 6 characters)."
    
    # Simulated order statuses
    order_statuses = {
        "processing": "Your order is being processed and will ship within 2-3 business days.",
        "shipped": "Your order has been shipped! You should receive a tracking number shortly.",
        "delivered": "Your order has been delivered. Please check your doorstep or mailbox.",
        "returned": "Your order has been returned and a refund is being processed."
    }
    
    # Simple hash to determine status
    status_key = list(order_statuses.keys())[hash(order_number) % len(order_statuses)]
    return f"Order {order_number}: {order_statuses[status_key]}"

@tool
def get_customer_info(customer_email: str) -> str:
    """Retrieve customer information and order history."""
    # Simulated customer data
    customer_data = {
        "john@example.com": {
            "name": "John Smith",
            "orders": 5,
            "total_spent": "$450.00",
            "last_order": "2024-01-15"
        },
        "jane@example.com": {
            "name": "Jane Doe", 
            "orders": 12,
            "total_spent": "$1,200.00",
            "last_order": "2024-01-20"
        }
    }
    
    if customer_email in customer_data:
        data = customer_data[customer_email]
        return f"Customer: {data['name']}, Orders: {data['orders']}, Total Spent: {data['total_spent']}, Last Order: {data['last_order']}"
    else:
        return f"No customer record found for {customer_email}. Please verify the email address."

# Create tool executor
tools = [search_knowledge_base, create_support_ticket, check_order_status, get_customer_info]
tool_executor = ToolExecutor(tools)

# Define the agent nodes
def should_continue(state: AgentState) -> str:
    """Determine if the conversation should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        if any(phrase in content for phrase in ["goodbye", "bye", "end", "stop", "thank you", "thanks", "that's all"]):
            return "end"
    
    return "continue"

def call_model(state: AgentState) -> AgentState:
    """Call the LLM to generate a response."""
    messages = state["messages"]
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful and professional customer support agent for an e-commerce company. 
        
        Your capabilities:
        - Answer questions about products, services, policies, and procedures
        - Check order status and customer information
        - Create support tickets for complex issues
        - Search the knowledge base for information
        
        Guidelines:
        - Always be polite, professional, and helpful
        - Use tools when you need specific information
        - If an issue is too complex, create a support ticket
        - Ask for clarification when needed
        - Provide clear, actionable information
        
        Available tools:
        - search_knowledge_base: For policy and general information
        - check_order_status: To check order status with order number
        - create_support_ticket: For complex issues requiring human help
        - get_customer_info: To retrieve customer data with email
        
        Use tools when appropriate to provide accurate information."""),
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
        messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))
    
    return {"messages": messages}

def generate_summary(state: AgentState) -> AgentState:
    """Generate a summary of the conversation when ending."""
    messages = state["messages"]
    
    # Create a summary prompt
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this customer support conversation in 2-3 sentences, highlighting the main issue and resolution."),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    summary_chain = summary_prompt | llm
    summary = summary_chain.invoke({"messages": messages})
    
    return {"conversation_summary": summary.content}

# Create the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tool)
workflow.add_node("summary", generate_summary)

# Add edges
workflow.add_edge("agent", should_continue)
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": "summary"
    }
)
workflow.add_edge("tools", "agent")
workflow.add_edge("summary", END)

# Compile the graph
app = workflow.compile()

# Function to run the chatbot
def run_chatbot():
    """Run the advanced customer support chatbot."""
    print("🤖 Advanced Customer Support Chatbot")
    print("Type 'quit' to exit")
    print("=" * 60)
    print("I can help you with:")
    print("• Order status and tracking")
    print("• Return and refund policies") 
    print("• Shipping information")
    print("• Payment and account questions")
    print("• Creating support tickets")
    print("=" * 60)
    
    # Initialize the state
    state = {
        "messages": [],
        "customer_info": {},
        "conversation_summary": ""
    }
    
    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("🤖 Thank you for using our customer support! Goodbye!")
            break
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            # Run the workflow
            result = app.invoke(state)
            
            # Get the last AI message
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                print(f"🤖 Assistant: {last_ai_message.content}")
            
            # Update state for next iteration
            state = result
            
        except Exception as e:
            print(f"🤖 I apologize, but I encountered an error: {str(e)}")
            print("Please try rephrasing your question or contact our support team directly.")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        run_chatbot() 