"""
Customer Support Chatbot using LangGraph - Fixed Version
Based on: https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/
Updated for LangGraph 0.5.x and GPT-4o-mini
"""

import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain.tools import tool
import json

# Load environment variables
load_dotenv()

# Define the state schema
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    next: str

# Initialize the LLM with correct configuration
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=1000
)

# Define tools for the customer support agent
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information about products and services."""
    # Simulated knowledge base - in a real implementation, this would connect to a database
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
        "cancellation": "You can cancel your order within 1 hour of placing it. After that, contact customer service immediately.",
        "delivery": "We offer standard delivery (3-5 days), express delivery (1-2 days), and same-day delivery in select areas.",
        "international": "We ship to most countries. International shipping takes 7-14 business days and may incur additional fees.",
        "damaged": "If you receive a damaged item, please take photos and contact us within 48 hours. We'll arrange a replacement or refund.",
        "size guide": "Our size guide is available on each product page. If you're unsure about sizing, we recommend ordering multiple sizes.",
        "gift cards": "Gift cards are available in denominations from $10 to $500. They never expire and can be used for any purchase."
    }
    
    query_lower = query.lower()
    for key, value in knowledge_base.items():
        if key in query_lower:
            return value
    
    return "I couldn't find specific information about that topic. Please contact our support team for assistance."

@tool
def create_support_ticket(issue: str, customer_email: str, priority: str = "medium") -> str:
    """Create a support ticket for complex issues that require human intervention."""
    # Simulated ticket creation
    priority_levels = {
        "low": "24-48 hours",
        "medium": "12-24 hours", 
        "high": "4-8 hours",
        "urgent": "1-2 hours"
    }
    
    response_time = priority_levels.get(priority, "12-24 hours")
    ticket_id = f"TICKET-{len(issue) + len(customer_email)}"
    return f"Support ticket {ticket_id} has been created with {priority} priority. A representative will contact you at {customer_email} within {response_time}."

@tool
def check_order_status(order_number: str) -> str:
    """Check the status of an order using the order number."""
    # Simulated order status check
    if not order_number or len(order_number) < 6:
        return "Invalid order number. Please provide a valid order number (minimum 6 characters)."
    
    # Simulate different order statuses based on order number
    statuses = {
        "processing": "Your order is being processed and will ship within 2-3 business days.",
        "shipped": "Your order has been shipped! You should receive a tracking number shortly.",
        "delivered": "Your order has been delivered. Please check your doorstep or mailbox.",
        "returned": "Your order has been returned and a refund is being processed.",
        "cancelled": "Your order has been cancelled. If you were charged, a refund will be processed within 5-7 business days."
    }
    
    # Determine status based on order number hash
    status_key = list(statuses.keys())[hash(order_number) % len(statuses)]
    return f"Order {order_number}: {statuses[status_key]}"

@tool
def get_customer_info(customer_email: str) -> str:
    """Retrieve customer information and order history."""
    # Simulated customer data
    customer_data = {
        "john@example.com": {
            "name": "John Smith",
            "orders": 5,
            "total_spent": "$450.00",
            "last_order": "2024-01-15",
            "loyalty_tier": "silver"
        },
        "jane@example.com": {
            "name": "Jane Doe", 
            "orders": 12,
            "total_spent": "$1,200.00",
            "last_order": "2024-01-20",
            "loyalty_tier": "gold"
        },
        "mike@example.com": {
            "name": "Mike Johnson",
            "orders": 2,
            "total_spent": "$150.00",
            "last_order": "2024-01-10",
            "loyalty_tier": "bronze"
        }
    }
    
    if customer_email in customer_data:
        data = customer_data[customer_email]
        return (f"Customer: {data['name']}, Orders: {data['orders']}, "
                f"Total Spent: {data['total_spent']}, Last Order: {data['last_order']}, "
                f"Loyalty Tier: {data['loyalty_tier']}")
    else:
        return f"No customer record found for {customer_email}. Please verify the email address."

# Create list of tools
tools = [search_knowledge_base, create_support_ticket, check_order_status, get_customer_info]

# Define the agent node
def call_model(state: AgentState) -> AgentState:
    """Call the LLM to generate a response."""
    messages = state["messages"]
    
    # Check if user wants to exit
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        if any(phrase in content for phrase in ["goodbye", "bye", "end", "stop", "thank you", "thanks", "quit", "exit"]):
            return {"messages": messages}
    
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
        - Respond in the same language as the user's message
        
        Available tools:
        - search_knowledge_base: For policy and general information
        - check_order_status: To check order status with order number
        - create_support_ticket: For complex issues requiring human help
        - get_customer_info: To retrieve customer data with email
        
        Use tools when appropriate to provide accurate information."""),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent with tools
    agent = prompt | llm.bind_tools(tools)
    
    # Get response
    response = agent.invoke({
        "messages": messages,
        "agent_scratchpad": []
    })
    
    # Add response to messages
    new_messages = list(messages) + [response]
    
    # If there are tool calls, execute them
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute the tool
            tool_func = None
            for tool in tools:
                if tool.name == tool_name:
                    tool_func = tool
                    break
            
            if tool_func:
                try:
                    result = tool_func.invoke(tool_args)
                    # Add tool result to messages
                    new_messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))
                except Exception as e:
                    new_messages.append(ToolMessage(
                        content=f"Error executing {tool_name}: {str(e)}",
                        tool_call_id=tool_call["id"]
                    ))
            else:
                new_messages.append(ToolMessage(
                    content=f"Tool {tool_name} not found",
                    tool_call_id=tool_call["id"]
                ))
    
    return {"messages": new_messages}

# Create workflow
workflow = StateGraph(AgentState)

# Add node
workflow.add_node("agent", call_model)

# Set entry point
workflow.set_entry_point("agent")

# Add edge to end
workflow.add_edge("agent", END)

# Compile graph
app = workflow.compile()

# Function to run the chatbot
def run_chatbot():
    """Run the customer support chatbot."""
    print("🤖 Customer Support Chatbot (Fixed - LangGraph 0.5.x)")
    print("Type 'quit' to exit")
    print("=" * 60)
    print("I can help you with:")
    print("• Order status and tracking")
    print("• Return and refund policies") 
    print("• Shipping information")
    print("• Payment and account questions")
    print("• Creating support tickets")
    print("• Customer information")
    print("=" * 60)
    
    # Initialize state
    state = {
        "messages": [],
        "next": ""
    }
    
    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
            print("🤖 Thank you for using our customer support! Goodbye!")
            break
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            # Execute workflow
            result = app.invoke(state)
            
            # Get last AI message
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
    # Check configuration
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        run_chatbot() 