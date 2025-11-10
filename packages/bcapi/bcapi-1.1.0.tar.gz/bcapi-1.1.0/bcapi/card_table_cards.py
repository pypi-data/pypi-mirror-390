"""Module for interacting with Basecamp 3 Card Table Card endpoints.

This module provides the CardTableCards class for managing cards within Basecamp
card table columns. It allows creating, updating, moving, and listing cards.
"""

from typing import List, Dict, Optional


class CardTableCards:
    """Class for interacting with Basecamp 3 Card Table Card endpoints."""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def list(self, project_id: int, column_id: int) -> List[Dict]:
        """
        Get a paginated list of cards in a column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column to list cards from

        Returns:
            A list of cards with their details including title, content, assignees,
            due dates, position, and completion status
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/lists/{column_id}/cards.json"
        return self.client.request("GET", url)

    def get(self, project_id: int, card_id: int) -> Dict:
        """
        Get details about a specific card.

        Parameters:
            project_id: The ID of the project containing the card
            card_id: The ID of the card to retrieve

        Returns:
            Card information including:
            - title: Card title
            - content: Card description/content
            - completed: Whether card is completed
            - due_on: Due date if set
            - assignees: List of assigned people
            - steps: List of steps/sub-tasks in the card
            - parent: The column containing this card
            - created_at: ISO 8601 timestamp of creation
            - updated_at: ISO 8601 timestamp of last update
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/cards/{card_id}.json"
        return self.client.request("GET", url)

    def create(self, project_id: int, column_id: int, title: str, 
               content: Optional[str] = None, due_on: Optional[str] = None,
               notify: bool = False) -> Dict:
        """
        Create a new card in a column.

        Parameters:
            project_id: The ID of the project containing the column
            column_id: The ID of the column to create the card in
            title: The title of the card
            content: Card content/description. See Basecamp Rich text guide for allowed HTML tags
            due_on: Due date in ISO 8601 format (YYYY-MM-DD)
            notify: Whether to notify assignees. Defaults to False

        Returns:
            The created card's information including ID, title, content,
            assignees, due date, and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/lists/{column_id}/cards.json"
        
        data = {"title": title, "notify": notify}
        if content is not None:
            data["content"] = content
        if due_on is not None:
            data["due_on"] = due_on

        return self.client.request("POST", url, json=data)

    def update(self, project_id: int, card_id: int, title: Optional[str] = None,
               content: Optional[str] = None, due_on: Optional[str] = None,
               assignee_ids: Optional[List[int]] = None) -> Dict:
        """
        Update an existing card.

        Parameters:
            project_id: The ID of the project containing the card
            card_id: The ID of the card to update
            title: The updated title of the card
            content: The updated content/description. See Basecamp Rich text guide for allowed HTML
            due_on: Updated due date in ISO 8601 format (YYYY-MM-DD)
            assignee_ids: Array of people IDs to assign to this card

        Returns:
            The updated card's information including title, content,
            assignees, due date, and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/cards/{card_id}.json"
        
        data = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if due_on is not None:
            data["due_on"] = due_on
        if assignee_ids is not None:
            data["assignee_ids"] = assignee_ids

        return self.client.request("PUT", url, json=data)

    def move(self, project_id: int, card_id: int, column_id: int) -> None:
        """
        Move a card to a different column.

        Parameters:
            project_id: The ID of the project containing the card
            card_id: The ID of the card to move
            column_id: The ID of the destination column
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/cards/{card_id}/moves.json"
        data = {"column_id": column_id}
        self.client.request("POST", url, json=data)

