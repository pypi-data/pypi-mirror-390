"""Module for interacting with Basecamp 3 Message endpoints.

This module provides the Messages class for managing messages within Basecamp message boards.
It allows creating, updating, listing, pinning and unpinning messages, as well as retrieving
details about specific messages.
"""

from typing import List, Dict, Optional
import json

class Messages:
    """Class to interact with Basecamp 3 Messages endpoints"""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def list(self, project_id: int, message_board_id: int, status: Optional[str] = None) -> List[Dict]:
        """
        Get a list of messages in a project's message board.

        Parameters:
            project_id (int): The ID of the project containing the message board
            message_board_id (int): The ID of the message board to list messages from
            status (str, optional): Filter by status - can be 'archived' or 'trashed'.
                                  If not specified, returns active messages.

        Returns:
            List[Dict]: A list of messages with their details including title, content,
                       creator, created/updated timestamps, and status
        """
        url = f"{self.client.api_url}/buckets/{project_id}/message_boards/{message_board_id}/messages.json"
        params = {}
        if status:
            params["status"] = status
        return self.client.request("GET", url, params=params)

    def get(self, project_id: int, message_id: int) -> Dict:
        """
        Get details about a specific message.

        Parameters:
            project_id (int): The ID of the project containing the message
            message_id (int): The ID of the message to retrieve

        Returns:
            Dict: Message information including title, content, creator, category,
                 created/updated timestamps, and status
        """
        url = f"{self.client.api_url}/buckets/{project_id}/messages/{message_id}.json"
        return self.client.request("GET", url)

    def create(self, project_id: int, message_board_id: int, subject: str, 
               content: Optional[str] = None, category_id: Optional[int] = None,
               status: str = "active", subscriptions: Optional[List[int]] = None) -> Dict:
        """
        Create a new message in a message board.

        Parameters:
            project_id (int): The ID of the project containing the message board
            message_board_id (int): The ID of the message board to create the message in
            subject (str): The title of the message
            content (str, optional): The body of the message in HTML format
            category_id (int, optional): The ID of the message type category
            status (str): Set to 'active' to publish immediately, 'drafted' to save as draft.
                         Defaults to 'active'
            subscriptions (List[int], optional): List of people IDs to notify and subscribe

        Returns:
            Dict: The created message's information including ID, title, content,
                 creator, and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/message_boards/{message_board_id}/messages.json"
        
        data = {
            "subject": subject,
            "status": status if status == "active" else "drafted"
        }
        
        if content is not None:
            data["content"] = content
        if category_id is not None:
            data["category_id"] = category_id
        if subscriptions is not None:
            data["subscriptions"] = subscriptions

        json_str = json.dumps(data)
        encoded_data = json_str.encode()

        return self.client.request("POST", url, data=encoded_data, 
                                 headers={"Content-Type": "application/json"})

    def update(self, project_id: int, message_id: int, subject: str, 
               content: Optional[str] = None, category_id: Optional[int] = None) -> Dict:
        """
        Update an existing message.

        Parameters:
            project_id (int): The ID of the project containing the message
            message_id (int): The ID of the message to update
            subject (str): The updated title of the message
            content (str, optional): The updated body of the message in HTML format
            category_id (int, optional): The updated message type category ID

        Returns:
            Dict: The updated message's information including title, content,
                 category, and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/messages/{message_id}.json"
        
        data = {"subject": subject}
        if content is not None:
            data["content"] = content
        if category_id is not None:
            data["category_id"] = category_id

        return self.client.request("PUT", url, json=data)

    def pin(self, project_id: int, message_id: int) -> None:
        """
        Pin a message to make it appear at the top of the message board.

        Parameters:
            project_id (int): The ID of the project containing the message
            message_id (int): The ID of the message to pin
        """
        url = f"{self.client.api_url}/buckets/{project_id}/recordings/{message_id}/pin.json"
        self.client.request("POST", url)

    def unpin(self, project_id: int, message_id: int) -> None:
        """
        Unpin a previously pinned message.

        Parameters:
            project_id (int): The ID of the project containing the message
            message_id (int): The ID of the message to unpin
        """
        url = f"{self.client.api_url}/buckets/{project_id}/recordings/{message_id}/pin.json"
        self.client.request("DELETE", url)