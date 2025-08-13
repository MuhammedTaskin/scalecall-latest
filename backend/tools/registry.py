"""
Tool registry with JSON schemas and execution dispatcher.
"""
import json
import logging
from typing import Dict, Any, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .types import OperationResult
from .telecom import TelecomTools
from .esim_extra import ESIMTools

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for all available tools with JSON schema validation."""
    
    def __init__(self):
        self.telecom_tools = TelecomTools()
        self.esim_tools = ESIMTools()
        self._init_schemas()
    
    def _init_schemas(self):
        """Initialize tool schemas for validation."""
        self.schemas = {
            "verify_user": {
                "name": "verify_user",
                "description": "Verify customer identity with maiden name and phone number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "maiden_name": {"type": "string", "description": "Customer's mother's maiden name"},
                        "msisdn": {"type": "string", "description": "Customer's phone number"}
                    },
                    "required": ["maiden_name", "msisdn"]
                }
            },
            "get_user_info": {
                "name": "get_user_info",
                "description": "Get customer account information and current status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer ID from verification"}
                    },
                    "required": ["customer_id"]
                }
            },
            "check_device_registration": {
                "name": "check_device_registration",
                "description": "Check if device IMEI is registered and activation status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "imei": {"type": "string", "description": "Device IMEI number"}
                    },
                    "required": ["imei"]
                }
            },
            "reissue_activation_code": {
                "name": "reissue_activation_code",
                "description": "Generate new eSIM activation code (LPA)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer ID"}
                    },
                    "required": ["customer_id"]
                }
            },
            "get_activation_steps": {
                "name": "get_activation_steps",
                "description": "Get device-specific eSIM activation instructions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "os_type": {"type": "string", "enum": ["iOS", "Android"], "description": "Device operating system"}
                    },
                    "required": ["os_type"]
                }
            },
            "get_activation_status": {
                "name": "get_activation_status",
                "description": "Check eSIM activation progress and current state",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer ID"}
                    },
                    "required": ["customer_id"]
                }
            },
            "get_available_packages": {
                "name": "get_available_packages",
                "description": "List available data packages for customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer ID"},
                        "country_code": {"type": "string", "description": "Country code for international packages"}
                    },
                    "required": ["customer_id"]
                }
            },
            "change_package": {
                "name": "change_package",
                "description": "Change customer's data package",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer ID"},
                        "package_id": {"type": "string", "description": "New package ID"}
                    },
                    "required": ["customer_id", "package_id"]
                }
            },
            "create_support_ticket": {
                "name": "create_support_ticket",
                "description": "Create customer support ticket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer ID"},
                        "subject": {"type": "string", "description": "Ticket subject"},
                        "description": {"type": "string", "description": "Detailed description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Ticket priority"}
                    },
                    "required": ["customer_id", "subject", "description", "priority"]
                }
            }
        }
    
    def get_allowed_tools(self) -> List[str]:
        """Get list of allowed tool names."""
        return list(self.schemas.keys())
    
    def get_tool_schema(self, tool_name: str) -> Dict:
        """Get JSON schema for a specific tool."""
        return self.schemas.get(tool_name)
    
    def validate_arguments(self, tool_name: str, arguments: Dict) -> bool:
        """Validate tool arguments against schema."""
        schema = self.get_tool_schema(tool_name)
        if not schema:
            return False
        
        # Basic validation - check required fields
        required = schema["parameters"].get("required", [])
        for field in required:
            if field not in arguments:
                logger.error(f"Missing required field '{field}' for tool '{tool_name}'")
                return False
        
        return True
    
    async def execute(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool with the given arguments."""
        try:
            # Validate tool exists
            if tool_name not in self.schemas:
                return OperationResult(
                    success=False,
                    error=f"Unknown tool: {tool_name}"
                ).to_dict()
            
            # Validate arguments
            if not self.validate_arguments(tool_name, arguments):
                return OperationResult(
                    success=False,
                    error=f"Invalid arguments for tool: {tool_name}"
                ).to_dict()
            
            # Route to appropriate tool implementation
            if tool_name in ["verify_user", "get_user_info", "check_device_registration", 
                           "reissue_activation_code", "get_available_packages", 
                           "change_package", "create_support_ticket"]:
                result = await self.telecom_tools.execute(tool_name, arguments)
                
            elif tool_name in ["get_activation_steps", "get_activation_status"]:
                result = await self.esim_tools.execute(tool_name, arguments)
                
            else:
                result = OperationResult(
                    success=False,
                    error=f"Tool '{tool_name}' not implemented"
                )
            
            # Ensure result is in correct format
            if isinstance(result, OperationResult):
                return result.to_dict()
            elif isinstance(result, dict):
                return result
            else:
                return OperationResult(
                    success=False,
                    error="Tool returned invalid result format"
                ).to_dict()
                
        except Exception as e:
            logger.error(f"Tool execution error for '{tool_name}': {e}")
            return OperationResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            ).to_dict()
