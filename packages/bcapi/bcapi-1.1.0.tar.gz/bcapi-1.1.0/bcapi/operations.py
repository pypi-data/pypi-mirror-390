"""Helper module for multi-step Basecamp operations with caching.

This module provides higher-level operations that combine multiple Basecamp API calls,
with caching to improve performance. It includes functionality for working with
projects, message boards, message types, and other Basecamp tools.

The Operations class provides methods to:
- Get tool IDs from a project's dock
- Get message type IDs 
- List and create messages
- Manage project data caching
"""

from typing import Dict, List, Optional

from .client import Client
from .message_types import MessageTypes
from .messages import Messages
from .projects import Projects

class Operations:
    """Helper class for multi-step Basecamp operations with caching"""

    def __init__(self, client: Client):
        """Initialize with a Basecamp client instance and empty project cache"""
        self.client = client
        self._project_cache: Dict[int, Dict] = {}

    def get_tool_id(self, project_id: int, tool_name: str) -> int:
        """
        Get the ID of a specific tool from a project's dock.
        Loads and caches project data if not already cached.

        Parameters:
            project_id (int): The ID of the project
            tool_name (str): Name of the tool to find (e.g., 'message_board', 'todoset')

        Returns:
            int: ID of the requested tool

        Raises:
            KeyError: If tool_name is not found in project's dock
        """
        if project_id not in self._project_cache:
            self._project_cache[project_id] = Projects(self.client).get(project_id)

        project = self._project_cache[project_id]
        return next(tool["id"] for tool in project["dock"] if tool["name"] == tool_name)

    def get_message_type_id(self, project_id: int, message_type_name: str) -> int:
        """
        Get the ID of a specific message type from a project's message types.
        
        Parameters:
            project_id (int): The ID of the project
            message_type_name (str): Name of the message type to find

        Returns:
            int: ID of the requested message type

        Raises:
            KeyError: If message_type_name is not found in project's message types
        """
        if project_id not in self._project_cache:
            self._project_cache[project_id] = Projects(self.client).get(project_id)
        if "message_types" not in self._project_cache[project_id]:
            self._project_cache[project_id]["message_types"] = MessageTypes(
                self.client
            ).list(project_id)

        return next(
            message_type["id"]
            for message_type in self._project_cache[project_id]["message_types"]
            if message_type["name"] == message_type_name
        )

    def get_messages_for_project(
        self, project_id: int, status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all messages from a project's message board.

        Parameters:
            project_id (int): The ID of the project
            status (str, optional): Filter messages by status ('archived' or 'trashed')

        Returns:
            List[Dict]: All messages from the project's message board matching the status filter
        """
        message_board_id = self.get_tool_id(project_id, "message_board")
        return Messages(self.client).list(project_id, message_board_id, status=status)

    def create_message(
        self,
        project_id: int,
        subject: str,
        content: str,
        message_type_name: Optional[str] = None,
        publish: bool = True,
    ) -> Dict:
        """
        Create a message in a project's message board.

        Parameters:
            project_id (int): The ID of the project
            subject (str): Subject line for the message
            content (str): Content of the message in HTML format
            message_type_name (str, optional): Name of message type/category to assign
            publish (bool): Whether to publish immediately (True) or save as draft (False)

        Returns:
            Dict: The created message's data
        """
        message_board_id = self.get_tool_id(project_id, "message_board")

        # Get message type ID if specified
        category_id = None
        if message_type_name:
            category_id = self.get_message_type_id(project_id, message_type_name)

        # Create the message
        return Messages(self.client).create(
            project_id=project_id,
            message_board_id=message_board_id,
            subject=subject,
            content=content,
            category_id=category_id,
            status="active" if publish else "drafted",
        )

    def clear_project_cache(self, project_id: Optional[int] = None) -> None:
        """
        Clear cached project data.

        Parameters:
            project_id (int, optional): Specific project ID to clear from cache.
                                      If None, clears the entire project cache.
        """
        if project_id is None:
            self._project_cache.clear()
        else:
            self._project_cache.pop(project_id, None)
