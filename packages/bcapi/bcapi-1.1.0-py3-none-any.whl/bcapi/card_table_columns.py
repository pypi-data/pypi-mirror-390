"""Module for interacting with Basecamp 3 Card Table Column endpoints.

This module provides the CardTableColumns class for managing columns within Basecamp
card tables (Kanban boards). It allows creating, updating, moving columns, as well as
managing subscriptions, on-hold sections, and column colors.
"""

from typing import Dict, Optional


class CardTableColumns:
    """Class for interacting with Basecamp 3 Card Table Column endpoints."""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def get(self, project_id: int, column_id: int) -> Dict:
        """
        Get details about a specific column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column to retrieve

        Returns:
            A dictionary containing the column details including:
            - title: The name of the column
            - status: Current status (active, archived, trashed)
            - description: Column description
            - color: Column color if set
            - cards_count: Number of cards in the column
            - cards_url: URL to retrieve cards in this column
            - created_at: ISO 8601 timestamp of creation
            - updated_at: ISO 8601 timestamp of last update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/columns/{column_id}.json"
        return self.client.request("GET", url)

    def create(self, project_id: int, card_table_id: int, title: str, 
               description: Optional[str] = None) -> Dict:
        """
        Create a new column in a card table.

        Parameters:
            project_id: The ID of the project containing the card table
            card_table_id: The ID of the card table to create the column in
            title: The title of the column
            description: Optional description containing information about the column

        Returns:
            The created column's information including ID, title, description,
            and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/{card_table_id}/columns.json"
        
        data = {"title": title}
        if description is not None:
            data["description"] = description

        return self.client.request("POST", url, json=data)

    def update(self, project_id: int, column_id: int, title: Optional[str] = None, 
               description: Optional[str] = None) -> Dict:
        """
        Update an existing column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column to update
            title: The updated title of the column
            description: The updated description of the column

        Returns:
            The updated column's information including title, description,
            and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/columns/{column_id}.json"
        
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description

        return self.client.request("PUT", url, json=data)

    def move(self, project_id: int, card_table_id: int, source_id: int, 
             target_id: int, position: int = 1) -> None:
        """
        Move a column to a new position in the card table.

        Parameters:
            project_id: The ID of the project containing the card table
            card_table_id: The ID of the card table
            source_id: The ID of the column to move
            target_id: The ID of the card table (target)
            position: Index among the columns (ignoring Triage, Not Now or Done). 
                     Defaults to 1
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/{card_table_id}/moves.json"
        
        data = {
            "source_id": source_id,
            "target_id": target_id,
            "position": position
        }

        self.client.request("POST", url, json=data)

    def subscribe(self, project_id: int, column_id: int) -> None:
        """
        Subscribe to a column (start watching).

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column to subscribe to
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/lists/{column_id}/subscription.json"
        self.client.request("POST", url)

    def unsubscribe(self, project_id: int, column_id: int) -> None:
        """
        Unsubscribe from a column (stop watching).

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column to unsubscribe from
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/lists/{column_id}/subscription.json"
        self.client.request("DELETE", url)

    def add_on_hold(self, project_id: int, column_id: int) -> Dict:
        """
        Create an on_hold section in the column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column

        Returns:
            The updated column information with on_hold section added
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/columns/{column_id}/on_hold.json"
        return self.client.request("POST", url)

    def remove_on_hold(self, project_id: int, column_id: int) -> Dict:
        """
        Remove the on_hold section from the column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column

        Returns:
            The updated column information with on_hold section removed
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/columns/{column_id}/on_hold.json"
        return self.client.request("DELETE", url)

    def set_color(self, project_id: int, column_id: int, color: str) -> Dict:
        """
        Change the color of a column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column
            color: The color to set. Available values:
                  white, red, orange, yellow, green, blue, aqua, purple, gray, pink, brown

        Returns:
            The updated column information with new color

        Raises:
            BasecampAPIError: If an invalid color is provided
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/columns/{column_id}/color.json"
        data = {"color": color}
        return self.client.request("PUT", url, json=data)

