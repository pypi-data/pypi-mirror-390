"""
Tool System for Function Calling
=================================

Enables agents to call external functions/tools to perform actions.
Inspired by OpenAI's function calling and LangChain's tool system.

Features:
- Decorator-based tool definition
- Automatic schema generation from type hints
- Tool execution with error handling
- Tool result formatting
- Built-in common tools

Author: C. Emre Karataş
Version: 2.0.0
"""

import json
import inspect
import re
from typing import Callable, Dict, List, Any, Optional, get_type_hints
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolCallStatus(Enum):
    """Status of tool call execution"""
    SUCCESS = "success"
    ERROR = "error"
    NOT_FOUND = "not_found"
    INVALID_ARGS = "invalid_args"


@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class Tool:
    """Tool definition"""
    name: str
    description: str
    function: Callable
    parameters: List[ToolParameter] = field(default_factory=list)
    return_type: str = "string"
    category: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type,
                        "description": param.description
                    }
                    for param in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            },
            "return_type": self.return_type
        }
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments"""
        try:
            # Validate required parameters
            required_params = [p.name for p in self.parameters if p.required]
            missing = [p for p in required_params if p not in kwargs]
            if missing:
                raise ValueError(f"Missing required parameters: {missing}")
            
            # Execute function
            result = self.function(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Tool execution error ({self.name}): {e}")
            raise


@dataclass
class ToolCallResult:
    """Result of a tool call"""
    tool_name: str
    status: ToolCallStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: str = "general"
) -> Callable:
    """
    Decorator to define a tool/function that the agent can call.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)
        category: Tool category for organization
    
    Example:
        @tool(name="calculate", description="Perform mathematical calculations")
        def calculator(expression: str) -> float:
            '''Evaluate a mathematical expression'''
            return eval(expression)
    """
    def decorator(func: Callable) -> Tool:
        # Get function metadata
        func_name = name or func.__name__
        func_desc = description or (func.__doc__ or "").strip()
        
        # Extract parameters from type hints
        type_hints = get_type_hints(func)
        sig = inspect.signature(func)
        parameters = []
        
        for param_name, param in sig.parameters.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]
                # Map Python types to JSON schema types
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                json_type = type_map.get(param_type, "string")
            else:
                json_type = "string"
            
            param_desc = f"Parameter: {param_name}"
            required = param.default == inspect.Parameter.empty
            
            parameters.append(ToolParameter(
                name=param_name,
                type=json_type,
                description=param_desc,
                required=required,
                default=param.default if param.default != inspect.Parameter.empty else None
            ))
        
        # Get return type
        return_type = "string"
        if "return" in type_hints:
            ret_type = type_hints["return"]
            type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
            return_type = type_map.get(ret_type, "string")
        
        # Create Tool object
        tool_obj = Tool(
            name=func_name,
            description=func_desc,
            function=func,
            parameters=parameters,
            return_type=return_type,
            category=category
        )
        
        # Attach tool metadata to function
        func._tool = tool_obj
        return func
    
    return decorator


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._load_builtin_tools()
    
    def _load_builtin_tools(self):
        """Load built-in tools"""
        # Import built-in tools when available
        try:
            from .builtin_tools import BUILTIN_TOOLS
            for tool_func in BUILTIN_TOOLS:
                if hasattr(tool_func, '_tool'):
                    self.register(tool_func._tool)
        except ImportError:
            pass
    
    def register(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_function(self, func: Callable):
        """Register a function as a tool"""
        if hasattr(func, '_tool'):
            self.register(func._tool)
        else:
            # Auto-create tool from function
            tool_obj = tool()(func)
            if hasattr(tool_obj, '_tool'):
                self.register(tool_obj._tool)
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Tool]:
        """List all tools, optionally filtered by category"""
        tools = list(self.tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get schema for all tools (for LLM prompt)"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def execute(self, tool_name: str, **kwargs) -> ToolCallResult:
        """Execute a tool by name"""
        import time
        start_time = time.time()
        
        # Get tool
        tool = self.get(tool_name)
        if not tool:
            return ToolCallResult(
                tool_name=tool_name,
                status=ToolCallStatus.NOT_FOUND,
                error=f"Tool '{tool_name}' not found",
                execution_time=time.time() - start_time
            )
        
        # Execute tool
        try:
            result = tool.execute(**kwargs)
            return ToolCallResult(
                tool_name=tool_name,
                status=ToolCallStatus.SUCCESS,
                result=result,
                execution_time=time.time() - start_time
            )
        except ValueError as e:
            return ToolCallResult(
                tool_name=tool_name,
                status=ToolCallStatus.INVALID_ARGS,
                error=str(e),
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ToolCallResult(
                tool_name=tool_name,
                status=ToolCallStatus.ERROR,
                error=str(e),
                execution_time=time.time() - start_time
            )


class ToolCallParser:
    """Parse LLM output to detect and extract tool calls"""
    
    # Pattern to detect tool calls in LLM output
    # Format: TOOL_CALL: tool_name(arg1="value1", arg2="value2")
    TOOL_CALL_PATTERN = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
    
    @staticmethod
    def parse(text: str) -> List[Dict[str, Any]]:
        """
        Parse text to extract tool calls.
        
        Returns:
            List of dicts with 'tool' and 'arguments' keys
        """
        tool_calls = []
        
        # Find all tool call matches
        matches = re.finditer(ToolCallParser.TOOL_CALL_PATTERN, text, re.MULTILINE)
        
        for match in matches:
            tool_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments
            arguments = {}
            if args_str.strip():
                try:
                    # Try to parse as Python kwargs
                    # Handle both key="value" and positional args
                    args_dict = {}
                    
                    # Split by comma, but respect quotes and parentheses
                    parts = []
                    current = ""
                    in_quotes = False
                    paren_depth = 0
                    quote_char = None
                    
                    for char in args_str:
                        if char in ['"', "'"] and quote_char is None:
                            quote_char = char
                            in_quotes = True
                            current += char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = None
                            current += char
                        elif char == '(' and not in_quotes:
                            paren_depth += 1
                            current += char
                        elif char == ')' and not in_quotes:
                            paren_depth -= 1
                            current += char
                        elif char == ',' and not in_quotes and paren_depth == 0:
                            if current.strip():
                                parts.append(current.strip())
                            current = ""
                        else:
                            current += char
                    
                    if current.strip():
                        parts.append(current.strip())
                    
                    # Parse each part
                    for i, part in enumerate(parts):
                        if '=' in part and not part.strip().startswith('"'):
                            key, value = part.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            args_dict[key] = value
                        else:
                            # Positional argument - use index as key
                            value = part.strip().strip('"\'')
                            # Try to infer parameter name from common patterns
                            if i == 0 and value:
                                # First arg is usually the main parameter
                                if tool_name == 'calculate':
                                    args_dict['expression'] = value
                                elif tool_name in ['count_words', 'reverse_text', 'to_uppercase', 'to_lowercase']:
                                    args_dict['text'] = value
                                elif tool_name == 'get_weather':
                                    args_dict['city'] = value
                                elif tool_name in ['read_file', 'write_file']:
                                    args_dict['filepath'] = value
                                else:
                                    args_dict[f'arg{i}'] = value
                    
                    arguments = args_dict
                except Exception as e:
                    logger.warning(f"Failed to parse arguments: {args_str} - Error: {e}")
            
            tool_calls.append({
                "tool": tool_name,
                "arguments": arguments
            })
        
        return tool_calls
    
    @staticmethod
    def has_tool_call(text: str) -> bool:
        """Check if text contains a tool call"""
        return bool(re.search(ToolCallParser.TOOL_CALL_PATTERN, text))
    
    @staticmethod
    def remove_tool_calls(text: str) -> str:
        """Remove tool call syntax from text, keeping only natural language"""
        return re.sub(ToolCallParser.TOOL_CALL_PATTERN, '', text).strip()


def format_tools_for_prompt(tools: List[Tool]) -> str:
    """
    Format tools as a string for LLM prompt.
    
    Returns:
        Formatted string describing available tools
    """
    if not tools:
        return ""
    
    lines = ["You have access to the following tools:"]
    lines.append("")
    
    for tool in tools:
        lines.append(f"- **{tool.name}**: {tool.description}")
        
        if tool.parameters:
            lines.append("  Parameters:")
            for param in tool.parameters:
                req = "required" if param.required else "optional"
                lines.append(f"    - {param.name} ({param.type}, {req}): {param.description}")
        
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("TOOL USAGE INSTRUCTIONS:")
    lines.append("-" * 80)
    lines.append("To call a tool, use EXACTLY this format:")
    lines.append('  TOOL_CALL: tool_name(param1="value1", param2="value2")')
    lines.append("")
    lines.append("EXAMPLES:")
    lines.append('  TOOL_CALL: calculate(expression="(25 * 4) + 10")')
    lines.append('  TOOL_CALL: count_words(text="Hello world from AI")')
    lines.append('  TOOL_CALL: get_current_time()')
    lines.append('  TOOL_CALL: read_file(filepath="data.txt")')
    lines.append("")
    lines.append("IMPORTANT RULES:")
    lines.append("  1. Always use named parameters (param=\"value\")")
    lines.append("  2. Put ALL parameters inside the parentheses")
    lines.append("  3. Use double quotes for string values")
    lines.append("  4. One tool call per line")
    lines.append("  5. After tool execution, you will receive results to continue your response")
    lines.append("=" * 80)
    lines.append("")
    
    return "\n".join(lines)

