"""Module for interacting with Basecamp 3 Card Table Step endpoints.

This module provides the CardTableSteps class for managing steps (sub-tasks) within
Basecamp card table cards. It allows creating, updating, completing, and repositioning steps.
Steps are returned as part of the card payload but can also be managed individually.
"""

from typing import Dict, Optional


class CardTableSteps:
    """Class for interacting with Basecamp 3 Card Table Step endpoints."""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def create(self, project_id: int, card_id: int, title: str,
               due_on: Optional[str] = None, assignees: Optional[str] = None) -> Dict:
        """
        Create a new step within a card.

        Parameters:
            project_id: The ID of the project containing the card
            card_id: The ID of the card to create the step in
            title: The title of the step
            due_on: Due date in ISO 8601 format (YYYY-MM-DD)
            assignees: Comma-separated list of people IDs to assign to this step

        Returns:
            The created step's information including ID, title, assignees,
            due date, completion status, and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/cards/{card_id}/steps.json"
        
        data = {"title": title}
        if due_on is not None:
            data["due_on"] = due_on
        if assignees is not None:
            data["assignees"] = assignees

        return self.client.request("POST", url, json=data)

    def update(self, project_id: int, step_id: int, title: Optional[str] = None,
               due_on: Optional[str] = None, assignees: Optional[str] = None) -> Dict:
        """
        Update an existing step.

        Parameters:
            project_id: The ID of the project containing the step
            step_id: The ID of the step to update
            title: The updated title of the step
            due_on: Updated due date in ISO 8601 format (YYYY-MM-DD)
            assignees: Updated comma-separated list of people IDs to assign

        Returns:
            The updated step's information including title, assignees,
            due date, completion status, and timestamps
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/steps/{step_id}.json"
        
        data = {}
        if title is not None:
            data["title"] = title
        if due_on is not None:
            data["due_on"] = due_on
        if assignees is not None:
            data["assignees"] = assignees

        return self.client.request("PUT", url, json=data)

    def complete(self, project_id: int, step_id: int) -> Dict:
        """
        Mark a step as completed.

        Parameters:
            project_id: The ID of the project containing the step
            step_id: The ID of the step to complete

        Returns:
            The updated step information with completed status set to true
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/steps/{step_id}/completions.json"
        data = {"completion": "on"}
        return self.client.request("PUT", url, json=data)

    def uncomplete(self, project_id: int, step_id: int) -> Dict:
        """
        Mark a step as uncompleted.

        Parameters:
            project_id: The ID of the project containing the step
            step_id: The ID of the step to uncomplete

        Returns:
            The updated step information with completed status set to false
        """
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/steps/{step_id}/completions.json"
        data = {"completion": "off"}
        return self.client.request("PUT", url, json=data)

    def reposition(self, project_id: int, card_id: int, source_id: int, 
                   position: int) -> None:
        """
        Change the position of a step within a card.

        Parameters:
            project_id: The ID of the project containing the card
            card_id: The ID of the card containing the step
            source_id: The ID of the step to reposition
            position: Zero-indexed position for the step

        Raises:
            ValueError: If position is less than 0
        """
        if position < 0:
            raise ValueError("Position must be greater than or equal to 0")
            
        url = f"{self.client.api_url}/buckets/{project_id}/card_tables/cards/{card_id}/positions.json"
        data = {
            "source_id": source_id,
            "position": position
        }
        self.client.request("POST", url, json=data)

