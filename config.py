"""
Configuración del Customer Support Chatbot
Externaliza configuraciones para facilitar el mantenimiento
"""

import os
from typing import Dict, Any

# Configuración del modelo de lenguaje
LLM_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "max_tokens": 1000
}

# Base de conocimientos simulada
KNOWLEDGE_BASE = {
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

# Datos de clientes simulados
CUSTOMER_DATA = {
    "john@example.com": {
        "name": "John Smith",
        "orders": 5,
        "total_spent": "$450.00",
        "last_order": "2024-01-15",
        "preferences": ["electronics", "books"],
        "loyalty_tier": "silver"
    },
    "jane@example.com": {
        "name": "Jane Doe", 
        "orders": 12,
        "total_spent": "$1,200.00",
        "last_order": "2024-01-20",
        "preferences": ["clothing", "home"],
        "loyalty_tier": "gold"
    },
    "mike@example.com": {
        "name": "Mike Johnson",
        "orders": 2,
        "total_spent": "$150.00",
        "last_order": "2024-01-10",
        "preferences": ["sports"],
        "loyalty_tier": "bronze"
    }
}

# Configuración de tickets de soporte
TICKET_CONFIG = {
    "priority_levels": {
        "low": "24-48 hours",
        "medium": "12-24 hours", 
        "high": "4-8 hours",
        "urgent": "1-2 hours"
    },
    "default_priority": "medium",
    "ticket_prefix": "TICKET"
}

# Configuración de estados de pedidos
ORDER_STATUSES = {
    "processing": "Your order is being processed and will ship within 2-3 business days.",
    "shipped": "Your order has been shipped! You should receive a tracking number shortly.",
    "delivered": "Your order has been delivered. Please check your doorstep or mailbox.",
    "returned": "Your order has been returned and a refund is being processed.",
    "cancelled": "Your order has been cancelled. If you were charged, a refund will be processed within 5-7 business days."
}

# Configuración de la interfaz
UI_CONFIG = {
    "welcome_message": "🤖 Customer Support Chatbot",
    "exit_commands": ["quit", "exit", "bye", "goodbye"],
    "max_conversation_length": 50,
    "show_tool_usage": True
}

# Configuración de prompts del sistema
SYSTEM_PROMPTS = {
    "main_agent": """You are a helpful and professional customer support agent for an e-commerce company. 
    
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
    
    Use tools when appropriate to provide accurate information.""",
    
    "summary": "Summarize this customer support conversation in 2-3 sentences, highlighting the main issue and resolution."
}

# Configuración de herramientas
TOOL_CONFIG = {
    "search_knowledge_base": {
        "description": "Search the knowledge base for relevant information about products and services.",
        "parameters": {
            "query": "The search query to look up in the knowledge base"
        }
    },
    "create_support_ticket": {
        "description": "Create a support ticket for complex issues that require human intervention.",
        "parameters": {
            "issue": "Description of the issue",
            "customer_email": "Customer's email address",
            "priority": "Priority level (low, medium, high, urgent)"
        }
    },
    "check_order_status": {
        "description": "Check the status of an order using the order number.",
        "parameters": {
            "order_number": "The order number to check"
        }
    },
    "get_customer_info": {
        "description": "Retrieve customer information and order history.",
        "parameters": {
            "customer_email": "Customer's email address"
        }
    }
}

# Configuración de validación
VALIDATION_CONFIG = {
    "min_order_number_length": 6,
    "email_domains": ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"],
    "max_issue_description_length": 500
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "customer_support.log"
}

def get_config() -> Dict[str, Any]:
    """Obtiene toda la configuración del sistema."""
    return {
        "llm": LLM_CONFIG,
        "knowledge_base": KNOWLEDGE_BASE,
        "customer_data": CUSTOMER_DATA,
        "ticket": TICKET_CONFIG,
        "order_statuses": ORDER_STATUSES,
        "ui": UI_CONFIG,
        "prompts": SYSTEM_PROMPTS,
        "tools": TOOL_CONFIG,
        "validation": VALIDATION_CONFIG,
        "logging": LOGGING_CONFIG
    }

def get_environment_config() -> Dict[str, Any]:
    """Obtiene configuración basada en variables de entorno."""
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("LLM_MODEL", LLM_CONFIG["model"]),
        "temperature": float(os.getenv("LLM_TEMPERATURE", str(LLM_CONFIG["temperature"]))),
        "debug_mode": os.getenv("DEBUG_MODE", "False").lower() == "true"
    } 