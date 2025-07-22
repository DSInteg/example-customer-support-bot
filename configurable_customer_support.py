"""
Customer Support Chatbot Configurable
Versión que utiliza configuración externalizada para mejor mantenibilidad
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
import logging

# Importar configuración
from config import (
    get_config, 
    get_environment_config,
    KNOWLEDGE_BASE,
    CUSTOMER_DATA,
    TICKET_CONFIG,
    ORDER_STATUSES,
    SYSTEM_PROMPTS,
    VALIDATION_CONFIG
)

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, get_config()["logging"]["level"]),
    format=get_config()["logging"]["format"],
    filename=get_config()["logging"]["file"]
)
logger = logging.getLogger(__name__)

# Definir el estado del agente
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    next: str
    customer_info: dict
    conversation_summary: str
    tool_usage_count: dict

# Obtener configuración
config = get_config()
env_config = get_environment_config()

# Inicializar el LLM con configuración
llm = ChatOpenAI(
    model=env_config["model"],
    temperature=env_config["temperature"],
    api_key=env_config["openai_api_key"],
    max_tokens=1000
)

# Definir herramientas usando configuración
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information about products and services."""
    query_lower = query.lower()
    
    # Buscar coincidencias exactas
    for key, value in KNOWLEDGE_BASE.items():
        if key in query_lower:
            logger.info(f"Knowledge base search: '{query}' -> found '{key}'")
            return value
    
    # Buscar coincidencias parciales
    for key, value in KNOWLEDGE_BASE.items():
        if any(word in query_lower for word in key.split()):
            logger.info(f"Knowledge base search: '{query}' -> partial match '{key}'")
            return value
    
    logger.warning(f"Knowledge base search: '{query}' -> no matches found")
    return "I couldn't find specific information about that topic. Please contact our support team for assistance."

@tool
def create_support_ticket(issue: str, customer_email: str, priority: str = None) -> str:
    """Create a support ticket for complex issues that require human intervention."""
    if not priority:
        priority = TICKET_CONFIG["default_priority"]
    
    if priority not in TICKET_CONFIG["priority_levels"]:
        priority = TICKET_CONFIG["default_priority"]
    
    response_time = TICKET_CONFIG["priority_levels"][priority]
    ticket_id = f"{TICKET_CONFIG['ticket_prefix']}-{len(issue) + len(customer_email)}"
    
    logger.info(f"Support ticket created: {ticket_id} with priority {priority}")
    
    return f"Support ticket {ticket_id} has been created with {priority} priority. A representative will contact you at {customer_email} within {response_time}."

@tool
def check_order_status(order_number: str) -> str:
    """Check the status of an order using the order number."""
    if not order_number or len(order_number) < VALIDATION_CONFIG["min_order_number_length"]:
        logger.warning(f"Invalid order number: '{order_number}'")
        return f"Invalid order number. Please provide a valid order number (minimum {VALIDATION_CONFIG['min_order_number_length']} characters)."
    
    # Determinar estado basado en el hash del número de pedido
    status_key = list(ORDER_STATUSES.keys())[hash(order_number) % len(ORDER_STATUSES)]
    status_message = ORDER_STATUSES[status_key]
    
    logger.info(f"Order status checked: {order_number} -> {status_key}")
    
    return f"Order {order_number}: {status_message}"

@tool
def get_customer_info(customer_email: str) -> str:
    """Retrieve customer information and order history."""
    if customer_email in CUSTOMER_DATA:
        data = CUSTOMER_DATA[customer_email]
        logger.info(f"Customer info retrieved: {customer_email}")
        
        return (f"Customer: {data['name']}, Orders: {data['orders']}, "
                f"Total Spent: {data['total_spent']}, Last Order: {data['last_order']}, "
                f"Loyalty Tier: {data['loyalty_tier']}")
    else:
        logger.warning(f"Customer not found: {customer_email}")
        return f"No customer record found for {customer_email}. Please verify the email address."

# Crear lista de herramientas
tools = [search_knowledge_base, create_support_ticket, check_order_status, get_customer_info]

# Definir nodos del agente
def should_continue(state: AgentState) -> str:
    """Determine if the conversation should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        exit_commands = config["ui"]["exit_commands"]
        if any(phrase in content for phrase in exit_commands):
            logger.info("Conversation ending - user requested exit")
            return "end"
    
    return "continue"

def call_model(state: AgentState) -> AgentState:
    """Call the LLM to generate a response and handle tools internally."""
    messages = state["messages"]
    
    # Crear template de prompt usando configuración
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPTS["main_agent"]),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Crear agente
    agent = prompt | llm.bind_tools(tools)
    
    # Obtener respuesta
    response = agent.invoke({
        "messages": messages,
        "agent_scratchpad": []
    })
    
    # Agregar respuesta a los mensajes
    new_messages = list(messages) + [response]
    
    # Si hay llamadas a herramientas, ejecutarlas internamente
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            
            # Encontrar y ejecutar la herramienta
            tool_func = None
            for tool in tools:
                if tool.name == tool_name:
                    tool_func = tool
                    break
            
            if tool_func:
                try:
                    result = tool_func.invoke(tool_args)
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    result = f"Error executing {tool_name}: {str(e)}"
            else:
                logger.error(f"Tool {tool_name} not found")
                result = f"Tool {tool_name} not found"
            
            # Agregar resultado de herramienta a mensajes
            new_messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            ))
            
            # Actualizar contador de uso de herramientas
            if "tool_usage_count" not in state:
                state["tool_usage_count"] = {}
            state["tool_usage_count"][tool_name] = state["tool_usage_count"].get(tool_name, 0) + 1
    
    logger.info(f"LLM response generated for message: {messages[-1].content[:50]}...")
    
    return {"messages": new_messages}

def call_tool(state: AgentState) -> AgentState:
    """Call a tool and add the result to the messages."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Extraer llamadas a herramientas del último mensaje
    tool_calls = last_message.tool_calls
    
    # Ejecutar cada llamada a herramienta
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        
        # Encontrar y ejecutar la herramienta
        tool_func = None
        for tool in tools:
            if tool.name == tool_name:
                tool_func = tool
                break
        
        if tool_func:
            try:
                result = tool_func.invoke(tool_args)
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                result = f"Error executing {tool_name}: {str(e)}"
        else:
            logger.error(f"Tool {tool_name} not found")
            result = f"Tool {tool_name} not found"
        
        # Agregar resultado de herramienta a mensajes
        messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))
        
        # Actualizar contador de uso de herramientas
        if "tool_usage_count" not in state:
            state["tool_usage_count"] = {}
        state["tool_usage_count"][tool_name] = state["tool_usage_count"].get(tool_name, 0) + 1
    
    return {"messages": messages}

def generate_summary(state: AgentState) -> AgentState:
    """Generate a summary of the conversation when ending."""
    messages = state["messages"]
    
    # Crear prompt de resumen usando configuración
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPTS["summary"]),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    summary_chain = summary_prompt | llm
    summary = summary_chain.invoke({"messages": messages})
    
    logger.info("Conversation summary generated")
    
    return {"conversation_summary": summary.content}

# Crear workflow simplificado
workflow = StateGraph(AgentState)

# Agregar solo el nodo principal
workflow.add_node("agent", call_model)

# Definir punto de entrada
workflow.set_entry_point("agent")

# Agregar edge directo al final
workflow.add_edge("agent", END)

# Compilar grafo
app = workflow.compile()

# Función para ejecutar el chatbot
def run_chatbot():
    """Ejecutar el chatbot de soporte al cliente configurable."""
    print(f"{config['ui']['welcome_message']} (Configurable - LangGraph 0.5.x)")
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
    
    # Inicializar estado
    state = {
        "messages": [],
        "customer_info": {},
        "conversation_summary": "",
        "tool_usage_count": {}
    }
    
    conversation_length = 0
    
    while True:
        # Verificar longitud máxima de conversación
        if conversation_length >= config["ui"]["max_conversation_length"]:
            print("🤖 Maximum conversation length reached. Thank you for using our support!")
            break
        
        # Obtener entrada del usuario
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in config["ui"]["exit_commands"]:
            print("🤖 Thank you for using our customer support! Goodbye!")
            break
        
        # Agregar mensaje del usuario al estado
        state["messages"].append(HumanMessage(content=user_input))
        conversation_length += 1
        
        try:
            # Ejecutar workflow
            result = app.invoke(state)
            
            # Obtener último mensaje del asistente
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                print(f"🤖 Assistant: {last_ai_message.content}")
            
            # Mostrar uso de herramientas si está habilitado
            if config["ui"]["show_tool_usage"] and result.get("tool_usage_count"):
                tool_count = result["tool_usage_count"]
                if tool_count:
                    print(f"🔧 Tools used: {', '.join([f'{tool}: {count}' for tool, count in tool_count.items()])}")
            
            # Actualizar estado para siguiente iteración
            state = result
            
        except Exception as e:
            logger.error(f"Error in conversation: {str(e)}")
            print(f"🤖 I apologize, but I encountered an error: {str(e)}")
            print("Please try rephrasing your question or contact our support team directly.")

if __name__ == "__main__":
    # Verificar configuración
    if not env_config["openai_api_key"]:
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        logger.info("Starting configurable customer support chatbot")
        run_chatbot() 