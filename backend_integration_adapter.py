"""
Backend Integration Adapter
Connects the fine-tuned model with the existing backend tool system
"""
import json
import asyncio
from typing import Dict, Any, Optional
from backend.tools.registry import ToolRegistry
from backend.prompts import get_system_prompt

class BackendIntegrationAdapter:
    """Adapter to integrate fine-tuned model with backend tools."""
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.current_persona = "RouterAgent"
        self.conversation_state = {
            "customer_id": None,
            "verification_status": False,
            "active_tools": [],
            "context_history": []
        }
    
    async def process_user_input(self, user_text: str, customer_context: Dict = None) -> Dict:
        """Process user input and return response with tool calls."""
        
        # Update conversation state
        if customer_context:
            self.conversation_state.update(customer_context)
        
        # Parse model response for tool calls and handoffs
        response = await self._get_model_response(user_text)
        
        # Check for tool calls
        if self._contains_tool_call(response):
            tool_result = await self._execute_tool_call(response)
            
            # Get final response after tool execution
            final_response = await self._get_model_response_with_tool_result(
                user_text, response, tool_result
            )
            
            return {
                "type": "tool_call_response",
                "tool_call": self._extract_tool_call(response),
                "tool_result": tool_result,
                "final_response": final_response,
                "persona": self.current_persona
            }
        
        # Check for persona handoff
        elif self._contains_handoff(response):
            handoff_data = self._extract_handoff(response)
            self.current_persona = handoff_data["persona"]
            
            return {
                "type": "handoff_response",
                "handoff": handoff_data,
                "response": handoff_data.get("say", ""),
                "new_persona": self.current_persona
            }
        
        # Regular text response
        else:
            return {
                "type": "text_response",
                "response": response,
                "persona": self.current_persona
            }
    
    async def _get_model_response(self, user_text: str) -> str:
        """Get response from the fine-tuned model."""
        # This would integrate with your actual model inference
        # For demo purposes, showing the interface
        
        system_prompt = get_system_prompt(self.current_persona)
        
        # Construct conversation with current state
        conversation_context = self._build_conversation_context(user_text)
        
        # Model inference would happen here
        # model_response = await model.generate(conversation_context)
        
        # Mock response for demonstration
        if "doğrula" in user_text.lower() or "kimlik" in user_text.lower():
            return json.dumps({
                "tool_call": {
                    "id": "12345",
                    "name": "verify_user",
                    "arguments": {
                        "maiden_name": "extracted_maiden_name",
                        "msisdn": "extracted_phone"
                    }
                }
            }, ensure_ascii=False)
        
        return "Size nasıl yardımcı olabilirim?"
    
    async def _get_model_response_with_tool_result(self, user_text: str, 
                                                  tool_call_response: str, 
                                                  tool_result: Dict) -> str:
        """Get model response after tool execution."""
        # This would call the model again with tool result context
        
        if tool_result.get("success"):
            return "İşlem başarıyla tamamlandı. Başka nasıl yardımcı olabilirim?"
        else:
            return "İşlem sırasında bir sorun oluştu. Tekrar deneyebilir miyiz?"
    
    async def _execute_tool_call(self, model_response: str) -> Dict:
        """Execute the tool call from model response."""
        try:
            tool_call_data = json.loads(model_response)
            tool_call = tool_call_data["tool_call"]
            
            tool_name = tool_call["name"]
            arguments = tool_call["arguments"]
            
            # Execute through tool registry
            result = await self.tool_registry.execute(tool_name, arguments)
            
            # Update conversation state
            self.conversation_state["active_tools"].append(tool_name)
            
            if tool_name == "verify_user" and result.get("success"):
                self.conversation_state["verification_status"] = True
                self.conversation_state["customer_id"] = result["data"].get("customer_id")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def _contains_tool_call(self, response: str) -> bool:
        """Check if response contains a tool call."""
        try:
            data = json.loads(response)
            return "tool_call" in data
        except:
            return False
    
    def _contains_handoff(self, response: str) -> bool:
        """Check if response contains a persona handoff."""
        try:
            data = json.loads(response)
            return "handoff" in data
        except:
            return False
    
    def _extract_tool_call(self, response: str) -> Dict:
        """Extract tool call data from response."""
        try:
            data = json.loads(response)
            return data["tool_call"]
        except:
            return {}
    
    def _extract_handoff(self, response: str) -> Dict:
        """Extract handoff data from response."""
        try:
            data = json.loads(response)
            return data["handoff"]
        except:
            return {}
    
    def _build_conversation_context(self, user_text: str) -> str:
        """Build conversation context for model."""
        context = f"Persona: {self.current_persona}\n"
        context += f"User verified: {self.conversation_state['verification_status']}\n"
        context += f"Customer ID: {self.conversation_state.get('customer_id', 'None')}\n"
        context += f"User: {user_text}\n"
        context += "Assistant:"
        
        return context
    
    def get_conversation_state(self) -> Dict:
        """Get current conversation state."""
        return self.conversation_state.copy()
    
    def reset_conversation(self):
        """Reset conversation state."""
        self.current_persona = "RouterAgent"
        self.conversation_state = {
            "customer_id": None,
            "verification_status": False,
            "active_tools": [],
            "context_history": []
        }

# Example usage
async def demo_backend_integration():
    """Demonstrate backend integration."""
    adapter = BackendIntegrationAdapter()
    
    # Test user verification
    result1 = await adapter.process_user_input("Kimlik doğrulaması yapmak istiyorum")
    print("Test 1 - Verification Request:")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    # Test persona handoff
    result2 = await adapter.process_user_input("Paket değiştirmek istiyorum")
    print("\nTest 2 - Package Change Request:")
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    # Test regular conversation
    result3 = await adapter.process_user_input("Teşekkür ederim")
    print("\nTest 3 - Regular Response:")
    print(json.dumps(result3, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_backend_integration())

print("✅ Backend integration adapter ready")
