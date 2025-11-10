"""Module for interacting with Basecamp 3 Message Type endpoints.

This module provides the MessageTypes class for managing message type categories
within Basecamp projects. It allows creating, updating, listing and deleting 
message types that can be assigned to messages in message boards.
"""

from typing import List, Dict, Optional

class MessageTypes:
    """Class to interact with Basecamp 3 Message Types endpoints"""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def list(self, project_id: int) -> List[Dict]:
        """
        Get a list of all message types in a project.

        Parameters:
            project_id: The ID of the project containing the message types

        Returns:
            A list of message types with their details including:
            - id: Unique identifier for the message type
            - name: Display name of the message type
            - icon: Emoji icon used for the message type
            - created_at: ISO 8601 timestamp of creation
            - updated_at: ISO 8601 timestamp of last update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/categories.json"
        return self.client.request("GET", url)

    def get(self, project_id: int, category_id: int) -> Dict:
        """
        Get details about a specific message type.

        Parameters:
            project_id: The ID of the project containing the message type
            category_id: The ID of the message type to retrieve

        Returns:
            Message type information including:
            - id: Unique identifier for the message type
            - name: Display name of the message type
            - icon: Emoji icon used for the message type
            - created_at: ISO 8601 timestamp of creation
            - updated_at: ISO 8601 timestamp of last update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/categories/{category_id}.json"
        return self.client.request("GET", url)

    def create(self, project_id: int, name: str, icon: str) -> Dict:
        """
        Create a new message type in a project.

        Parameters:
            project_id: The ID of the project to create the message type in
            name: The display name of the message type
            icon: The emoji icon for the message type

        Returns:
            The created message type's information including:
            - id: Unique identifier for the new message type
            - name: Display name of the message type
            - icon: Emoji icon used for the message type
            - created_at: ISO 8601 timestamp of creation
        """
        url = f"{self.client.api_url}/buckets/{project_id}/categories.json"
        data = {
            "name": name,
            "icon": icon
        }
        return self.client.request("POST", url, json=data)

    def update(self, project_id: int, category_id: int, name: str, icon: str) -> Dict:
        """
        Update an existing message type.

        Parameters:
            project_id: The ID of the project containing the message type
            category_id: The ID of the message type to update
            name: The updated name for the message type
            icon: The updated emoji icon for the message type

        Returns:
            The updated message type's information including:
            - id: Unique identifier for the message type
            - name: Updated display name
            - icon: Updated emoji icon
            - updated_at: ISO 8601 timestamp of update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/categories/{category_id}.json"
        data = {
            "name": name,
            "icon": icon
        }
        return self.client.request("PUT", url, json=data)

    def delete(self, project_id: int, category_id: int) -> None:
        """
        Delete a message type.

        Parameters:
            project_id: The ID of the project containing the message type
            category_id: The ID of the message type to delete
        """
        url = f"{self.client.api_url}/buckets/{project_id}/categories/{category_id}.json"
        self.client.request("DELETE", url)