"""
Ejemplo de uso del Customer Support Chatbot
Demuestra cómo usar el chatbot programáticamente
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from advanced_customer_support import app

# Cargar variables de entorno
load_dotenv()

def test_conversation():
    """Ejemplo de conversación con el chatbot."""
    
    # Verificar que la API key esté configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY no está configurada")
        print("Por favor, crea un archivo .env con tu API key de OpenAI")
        return
    
    print("🧪 Probando el Customer Support Chatbot")
    print("=" * 50)
    
    # Ejemplos de conversación
    test_cases = [
        "What is your return policy?",
        "Can you check the status of order 123456789?",
        "How long does shipping take?",
        "I need help with a complex issue with my account",
        "Thank you for your help, goodbye!"
    ]
    
    # Inicializar el estado
    state = {
        "messages": [],
        "customer_info": {},
        "conversation_summary": ""
    }
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"👤 Usuario: {user_input}")
        
        # Agregar mensaje del usuario
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            # Ejecutar el workflow
            result = app.invoke(state)
            
            # Obtener la respuesta del asistente
            ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'content') and msg.content]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                print(f"🤖 Asistente: {last_ai_message.content}")
            
            # Actualizar estado para la siguiente iteración
            state = result
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Mostrar resumen final si está disponible
    if state.get("conversation_summary"):
        print(f"\n📝 Resumen de la conversación: {state['conversation_summary']}")

def test_specific_scenarios():
    """Prueba escenarios específicos del chatbot."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY no está configurada")
        return
    
    print("\n🔍 Probando escenarios específicos")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Consulta de política de devoluciones",
            "input": "What is your return policy?",
            "expected_keywords": ["return", "30 days", "receipt"]
        },
        {
            "name": "Verificación de pedido válido",
            "input": "Check order status for 123456789",
            "expected_keywords": ["order", "processed", "ship"]
        },
        {
            "name": "Verificación de pedido inválido",
            "input": "Check order status for 123",
            "expected_keywords": ["invalid", "order number"]
        },
        {
            "name": "Información de envío",
            "input": "How long does shipping take?",
            "expected_keywords": ["shipping", "business days", "express"]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        # Inicializar estado
        state = {
            "messages": [HumanMessage(content=scenario["input"])],
            "customer_info": {},
            "conversation_summary": ""
        }
        
        try:
            # Ejecutar workflow
            result = app.invoke(state)
            
            # Obtener respuesta
            ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'content') and msg.content]
            if ai_messages:
                response = ai_messages[-1].content.lower()
                print(f"Respuesta: {response}")
                
                # Verificar palabras clave esperadas
                found_keywords = [keyword for keyword in scenario["expected_keywords"] if keyword in response]
                if found_keywords:
                    print(f"✅ Palabras clave encontradas: {found_keywords}")
                else:
                    print(f"⚠️ Palabras clave esperadas no encontradas: {scenario['expected_keywords']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_tool_usage():
    """Prueba el uso de herramientas específicas."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY no está configurada")
        return
    
    print("\n🔧 Probando uso de herramientas")
    print("=" * 50)
    
    # Probar búsqueda en base de conocimientos
    print("\n--- Probando search_knowledge_base ---")
    from advanced_customer_support import search_knowledge_base
    
    test_queries = ["return policy", "shipping", "warranty", "nonexistent topic"]
    
    for query in test_queries:
        result = search_knowledge_base(query)
        print(f"Query: '{query}' -> {result}")
    
    # Probar verificación de pedidos
    print("\n--- Probando check_order_status ---")
    from advanced_customer_support import check_order_status
    
    test_orders = ["123456789", "123", ""]
    
    for order in test_orders:
        result = check_order_status(order)
        print(f"Order: '{order}' -> {result}")

if __name__ == "__main__":
    print("🚀 Ejemplos de uso del Customer Support Chatbot")
    print("=" * 60)
    
    # Ejecutar pruebas
    test_conversation()
    test_specific_scenarios()
    test_tool_usage()
    
    print("\n✅ Todas las pruebas completadas")
    print("\n💡 Para usar el chatbot interactivamente, ejecuta:")
    print("   python advanced_customer_support.py") 