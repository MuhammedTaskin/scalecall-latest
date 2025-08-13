"""
LLM Orchestrator with Function Calling and Prompt-Swap Handoff.
"""
import json
import uuid
import re
from typing import AsyncIterator, Dict, Any, List, Optional
import logging

from backend.llm_abi import LLMProvider
from backend.tools.registry import ToolRegistry
from backend.prompts import get_system_prompt

logger = logging.getLogger(__name__)


class Orchestrator:
    """Handles LLM streaming, function calling, and persona handoffs."""
    
    def __init__(self):
        self.llm = LLMProvider()
        self.tools = ToolRegistry()
        self.pending_tool_calls = {}
        
    async def stream(self, messages: List[Dict], current_persona: str = "RouterAgent") -> AsyncIterator[Dict]:
        """
        Stream LLM responses with function calling and handoff support.
        
        Yields:
            {"delta": "text"} - Partial model text
            {"tool_call": {"id": "...", "name": "...", "arguments": {...}}} - Function call
            {"handoff": {"persona": "..."}} - Persona change request
            {"complete": "full_text"} - Complete response for TTS
        """
        # Prepare messages with system prompt
        system_prompt = get_system_prompt(current_persona)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        accumulated_text = ""
        current_tool_call = None
        tool_call_buffer = ""
        
        try:
            async for chunk in self.llm.stream(full_messages):
                text = chunk.get("text", "")
                
                if not text:
                    continue
                    
                # Check for function call JSON
                tool_call_match = self._extract_tool_call(accumulated_text + text)
                if tool_call_match:
                    tool_call_data = tool_call_match
                    call_id = str(uuid.uuid4())
                    
                    # Store pending call
                    self.pending_tool_calls[call_id] = tool_call_data
                    
                    yield {
                        "tool_call": {
                            "id": call_id,
                            "name": tool_call_data["name"],
                            "arguments": tool_call_data["arguments"]
                        }
                    }
                    
                    # Execute tool and continue
                    continue
                
                # Check for handoff request
                handoff_match = self._extract_handoff(accumulated_text + text)
                if handoff_match:
                    yield {"handoff": {"persona": handoff_match["persona"]}}
                    # Update messages with new persona and continue
                    return
                
                # Regular text streaming
                accumulated_text += text
                yield {"delta": text}
                
        except Exception as e:
            logger.error(f"Orchestrator stream error: {e}")
            yield {"delta": "Üzgünüm, bir hata oluştu."}
            
        # Send complete text for TTS
        if accumulated_text.strip():
            yield {"complete": accumulated_text.strip()}
    
    def _extract_tool_call(self, text: str) -> Optional[Dict]:
        """Extract tool call JSON from text."""
        try:
            # Look for {"tool_call": ...} pattern
            pattern = r'\{"tool_call":\s*\{[^}]+\}\s*\}'
            match = re.search(pattern, text)
            if match:
                json_str = match.group()
                data = json.loads(json_str)
                return data.get("tool_call")
                
            # Also check for direct tool call format
            pattern = r'\{\s*"name":\s*"[^"]+",\s*"arguments":\s*\{[^}]*\}\s*\}'
            match = re.search(pattern, text)
            if match:
                json_str = match.group()
                return json.loads(json_str)
                
        except (json.JSONDecodeError, KeyError):
            pass
        return None
    
    def _extract_handoff(self, text: str) -> Optional[Dict]:
        """Extract handoff request from text."""
        try:
            pattern = r'\{"handoff":\s*\{\s*"persona":\s*"([^"]+)"\s*\}\s*\}'
            match = re.search(pattern, text)
            if match:
                return {"persona": match.group(1)}
        except Exception:
            pass
        return None
    
    async def execute_tool(self, tool_call: Dict) -> Dict:
        """Execute a tool call and return the result."""
        try:
            tool_name = tool_call["name"]
            arguments = tool_call["arguments"]
            
            # Execute tool via registry
            result = await self.tools.execute(tool_name, arguments)
            
            return result
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def feed_tool_result(self, call_id: str, result: Dict) -> None:
        """Feed tool result back into context (for future implementations)."""
        if call_id in self.pending_tool_calls:
            # Store result for context continuation
            self.pending_tool_calls[call_id]["result"] = result
