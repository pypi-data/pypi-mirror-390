"""
Utilities
========

Common utility functions for Lexia integration.
"""

import os
import base64
import tempfile
import logging
from typing import List, Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)

def set_env_variables(variables):
    """
    Set environment variables from the variables list.
    
    Lexia sends variables in format: [{"name": "OPENAI_API_KEY", "value": "..."}]
    Supports both Pydantic models and dictionaries.
    
    Args:
        variables: List of Variable objects or dictionaries from request
    """
    if not variables:
        logger.warning("No variables provided to set_env_variables")
        return
        
    for var in variables:
        try:
            # Handle Pydantic models
            if hasattr(var, 'name') and hasattr(var, 'value'):
                os.environ[var.name] = var.value
                logger.info(f"Set environment variable: {var.name}")
            # Handle dictionaries
            elif isinstance(var, dict) and 'name' in var and 'value' in var:
                os.environ[var['name']] = var['value']
                logger.info(f"Set environment variable: {var['name']}")
            else:
                logger.warning(f"Invalid variable format: {var}")
        except Exception as e:
            logger.error(f"Error setting environment variable: {e}")


class MemoryHelper:
    """
    Helper class for easy access to user memory data from Lexia requests.
    
    Usage:
        memory = MemoryHelper(data.memory)
        user_name = memory.get_name()
        user_goals = memory.get_goals()
        user_location = memory.get_location()
    """
    
    def __init__(self, memory_data):
        """
        Initialize with memory data from request.
        
        Args:
            memory_data: Memory object, dictionary, or list from request
        """
        if memory_data is None:
            self.memory = {}
        elif hasattr(memory_data, 'dict'):
            # Pydantic model
            self.memory = memory_data.dict()
        elif isinstance(memory_data, dict):
            # Dictionary
            self.memory = memory_data
        elif isinstance(memory_data, list):
            # Empty list or old format - treat as empty memory
            self.memory = {}
        else:
            # Fallback for any other type
            self.memory = {}
    
    def get_name(self) -> str:
        """Get user's name."""
        return self.memory.get("name", "")
    
    def get_goals(self) -> List[str]:
        """Get user's goals."""
        return self.memory.get("goals", [])
    
    def get_location(self) -> str:
        """Get user's location."""
        return self.memory.get("location", "")
    
    def get_interests(self) -> List[str]:
        """Get user's interests."""
        return self.memory.get("interests", [])
    
    def get_preferences(self) -> List[str]:
        """Get user's preferences."""
        return self.memory.get("preferences", [])
    
    def get_past_experiences(self) -> List[str]:
        """Get user's past experiences."""
        return self.memory.get("past_experiences", [])
    
    def has_name(self) -> bool:
        """Check if user has a name."""
        return bool(self.get_name())
    
    def has_goals(self) -> bool:
        """Check if user has goals."""
        return len(self.get_goals()) > 0
    
    def has_location(self) -> bool:
        """Check if user has a location."""
        return bool(self.get_location())
    
    def has_interests(self) -> bool:
        """Check if user has interests."""
        return len(self.get_interests()) > 0
    
    def has_preferences(self) -> bool:
        """Check if user has preferences."""
        return len(self.get_preferences()) > 0
    
    def has_past_experiences(self) -> bool:
        """Check if user has past experiences."""
        return len(self.get_past_experiences()) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert memory to dictionary.
        
        Returns:
            Dictionary representation of memory
        """
        return {
            "name": self.get_name(),
            "goals": self.get_goals(),
            "location": self.get_location(),
            "interests": self.get_interests(),
            "preferences": self.get_preferences(),
            "past_experiences": self.get_past_experiences()
        }
    
    def is_empty(self) -> bool:
        """
        Check if memory is empty (no data).
        
        Returns:
            True if memory is empty, False otherwise
        """
        return not any([
            self.has_name(),
            self.has_goals(),
            self.has_location(),
            self.has_interests(),
            self.has_preferences(),
            self.has_past_experiences()
        ])


class ForceToolsHelper:
    """
    Helper class for easy access to force_tools data from Lexia requests.
    
    Usage:
        tools = ForceToolsHelper(data.force_tools)
        if tools.has('search'):
            # Perform search
            pass
        if tools.has_code():
            # Use code tool
            pass
    """
    
    def __init__(self, force_tools: Optional[List[str]] = None):
        """
        Initialize with force_tools list from request.
        
        Args:
            force_tools: List of tool names from request (e.g., ['code', 'search', 'xyz'])
        """
        self.tools = force_tools if force_tools is not None else []
    
    def has(self, tool_name: str) -> bool:
        """
        Check if a specific tool is forced.
        
        Args:
            tool_name: Name of the tool to check (e.g., 'code', 'search')
            
        Returns:
            True if tool is forced, False otherwise
        """
        return tool_name in self.tools
    
    
    def get_all(self) -> List[str]:
        """
        Get all forced tools.
        
        Returns:
            List of forced tool names
        """
        return self.tools.copy()
    
    def is_empty(self) -> bool:
        """
        Check if no tools are forced.
        
        Returns:
            True if no tools are forced, False otherwise
        """
        return len(self.tools) == 0
    
    def count(self) -> int:
        """
        Get count of forced tools.
        
        Returns:
            Number of forced tools
        """
        return len(self.tools)


class Variables:
    """
    Helper class for easy access to variables from Lexia requests.
    
    Usage:
        variables = Variables(data.variables)
        openai_key = variables.get("OPENAI_API_KEY")
        anthropic_key = variables.get("ANTHROPIC_API_KEY")
    """
    
    def __init__(self, variables_list):
        """
        Initialize with a list of Variable objects or dictionaries.
        
        Args:
            variables_list: List of Variable objects or dictionaries from request
        """
        self.variables_list = variables_list or []
        self._cache = {}
        
        # Build a cache for faster lookups
        for var in self.variables_list:
            try:
                # Handle Pydantic models
                if hasattr(var, 'name') and hasattr(var, 'value'):
                    self._cache[var.name] = var.value
                # Handle dictionaries
                elif isinstance(var, dict) and 'name' in var and 'value' in var:
                    self._cache[var['name']] = var['value']
            except Exception as e:
                logger.error(f"Error processing variable: {e}")
    
    def get(self, variable_name: str) -> Optional[str]:
        """
        Get a variable value by name.
        
        Args:
            variable_name: Name of the variable to get
            
        Returns:
            Variable value string or None if not found
        """
        return self._cache.get(variable_name)
    
    
    def has(self, variable_name: str) -> bool:
        """
        Check if a variable exists.
        
        Args:
            variable_name: Name of the variable to check
            
        Returns:
            True if variable exists, False otherwise
        """
        return variable_name in self._cache
    
    def list_names(self) -> List[str]:
        """
        Get list of all variable names.
        
        Returns:
            List of variable names
        """
        return list(self._cache.keys())
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert all variables to a dictionary.
        
        Returns:
            Dictionary of variable names to values
        """
        return self._cache.copy()


def get_variable_value(variables, variable_name: str) -> Optional[str]:
    """
    Extract a specific variable value from variables list by name.
    
    Supports both Pydantic models and dictionaries.
    
    Args:
        variables: List of Variable objects or dictionaries from request
        variable_name: Name of the variable to extract (e.g., "OPENAI_API_KEY")
        
    Returns:
        Variable value string or None if not found
    """
    if not variables:
        logger.warning(f"No variables provided to get_variable_value for '{variable_name}'")
        return None
        
    for var in variables:
        try:
            # Handle Pydantic models
            if hasattr(var, 'name') and hasattr(var, 'value'):
                if var.name == variable_name:
                    logger.info(f"Found variable '{variable_name}'")
                    return var.value
            # Handle dictionaries
            elif isinstance(var, dict) and 'name' in var and 'value' in var:
                if var['name'] == variable_name:
                    logger.info(f"Found variable '{variable_name}'")
                    return var['value']
            else:
                logger.warning(f"Invalid variable format: {var}")
        except Exception as e:
            logger.error(f"Error processing variable: {e}")
    
    logger.warning(f"Variable '{variable_name}' not found in variables")
    return None


def get_openai_api_key(variables) -> Optional[str]:
    """
    Extract OpenAI API key from variables list.
    
    This is a convenience function that uses get_variable_value internally.
    
    Args:
        variables: List of Variable objects or dictionaries from request
        
    Returns:
        OpenAI API key string or None if not found
    """
    return get_variable_value(variables, "OPENAI_API_KEY")


def format_system_prompt(system_message: str = None, project_system_message: str = None) -> str:
    """
    Format the system prompt for OpenAI API.
    
    Args:
        system_message: Custom system message
        project_system_message: Project-specific system message
        
    Returns:
        Formatted system prompt string
    """
    default_system_prompt = """You are a helpful AI assistant. You provide clear, accurate, and helpful responses.
    
Guidelines:
- Be concise but informative
- Use markdown formatting when helpful
- If you don't know something, say so
- Be friendly and professional
- Provide examples when helpful"""

    # Use project system message if available, then custom system message, then default
    return project_system_message or system_message or default_system_prompt


def format_messages_for_openai(system_prompt: str, conversation_history: List[Dict[str, str]], current_message: str) -> List[Dict[str, str]]:
    """
    Format messages for OpenAI API call.
    
    Args:
        system_prompt: System prompt to use
        conversation_history: Previous conversation messages
        current_message: Current user message
        
    Returns:
        List of messages formatted for OpenAI API
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history (excluding the current user message)
    for hist_msg in conversation_history[:-1]:  # Exclude the last message (current user message)
        messages.append(hist_msg)
    
    # Add current user message
    messages.append({"role": "user", "content": current_message})
    
    return messages


def decode_base64_file(file_base64: str, filename: str = None) -> Tuple[str, bool]:
    """
    Decode a base64 encoded file and save to temporary file.
    
    Args:
        file_base64: Base64 encoded file data (data URI format: "data:mime;base64,...")
        filename: Optional filename to use for extension detection
        
    Returns:
        Tuple of (file_path, is_temp_file)
        
    Example:
        file_path, is_temp = decode_base64_file(data.file_base64, data.file_name)
        # Use the file
        if is_temp:
            os.unlink(file_path)  # Clean up
    """
    if not file_base64:
        raise ValueError("file_base64 is empty")
    
    try:
        # Parse data URI: "data:audio/wav;base64,UklGRiQAAABXQVZF..."
        if file_base64.startswith('data:'):
            # Split header and data
            header, base64_data = file_base64.split(',', 1)
            # Extract MIME type
            mime_type = header.split(':')[1].split(';')[0]
            logger.info(f"Detected MIME type: {mime_type}")
        else:
            # Assume it's just base64 without data URI prefix
            base64_data = file_base64
            mime_type = None
        
        # Decode base64
        file_bytes = base64.b64decode(base64_data)
        logger.info(f"Decoded {len(file_bytes)} bytes from base64")
        
        # Determine file extension
        if filename:
            # Use extension from provided filename
            ext = os.path.splitext(filename)[1]
        elif mime_type:
            # Derive extension from MIME type
            mime_to_ext = {
                'audio/wav': '.wav',
                'audio/mpeg': '.mp3',
                'audio/mp3': '.mp3',
                'audio/ogg': '.ogg',
                'audio/flac': '.flac',
                'video/mp4': '.mp4',
                'video/avi': '.avi',
                'video/quicktime': '.mov',
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'application/pdf': '.pdf',
                'text/plain': '.txt',
            }
            ext = mime_to_ext.get(mime_type, '.bin')
        else:
            ext = '.bin'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        temp_file.write(file_bytes)
        temp_file.close()
        
        logger.info(f"Saved decoded file to: {temp_file.name}")
        return temp_file.name, True
        
    except Exception as e:
        logger.error(f"Error decoding base64 file: {e}")
        raise ValueError(f"Failed to decode base64 file: {e}")
