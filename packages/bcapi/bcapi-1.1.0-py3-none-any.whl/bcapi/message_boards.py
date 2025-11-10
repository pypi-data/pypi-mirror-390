"""Module for interacting with Basecamp 3 Message Board endpoints.

This module provides the MessageBoards class for retrieving information about
message boards within Basecamp projects. It allows fetching details about specific
message boards including their status, visibility settings, and message counts.
"""

from typing import Dict

class MessageBoards:
    """Class for interacting with Basecamp 3 Message Board endpoints."""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def get(self, project_id: int, message_board_id: int) -> Dict:
        """
        Get details about a specific message board.

        Parameters:
            project_id: The ID of the project containing the message board
            message_board_id: The ID of the message board to retrieve

        Returns:
            A dictionary containing the message board details including:
            - title: The name of the message board
            - status: Current status (active, archived, trashed)
            - position: Sort position in the project
            - messages_count: Number of messages in the board
            - created_at: ISO 8601 timestamp of creation
            - updated_at: ISO 8601 timestamp of last update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/message_boards/{message_board_id}.json"
        return self.client.request("GET", url)