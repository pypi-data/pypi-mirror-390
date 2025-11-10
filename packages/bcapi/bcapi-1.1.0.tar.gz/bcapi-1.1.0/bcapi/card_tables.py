"""Module for interacting with Basecamp 3 Card Table endpoints.

A card table is the main Kanban board container made of multiple columns which contain cards.
This module provides the CardTables class for retrieving information about card tables
within Basecamp projects.
"""

from typing import Dict


class CardTables:
    """Class for interacting with Basecamp 3 Card Table endpoints."""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def get(self, project_id: int, card_table_id: int) -> Dict:
        """
        Get details about a specific card table (Kanban board).

        Parameters:
            project_id: The ID of the project containing the card table
            card_table_id: The ID of the card table to retrieve

        Returns:
            A dictionary containing the card table details including:
            - title: The name of the card table
            - status: Current status (active, archived, trashed)
            - lists: Array of columns in the board (Triage, custom columns, Done)
            - subscribers: List of people subscribed to the board
            - created_at: ISO 8601 timestamp of creation
            - updated_at: ISO 8601 timestamp of last update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/{card_table_id}.json"
        return self.client.request("GET", url)

