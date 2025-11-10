"""Module for interacting with Basecamp 3 To-do endpoints.

This module provides the Todos class for managing individual to-do items within Basecamp
to-do lists. It allows creating, updating, completing, repositioning and listing to-dos,
as well as retrieving details about specific to-do items.
"""

from bcapi.client import BasecampAPIError

class Todos:
    """Class to interact with Basecamp 3 To-do endpoints"""
    
    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client
        
    def list(self, project_id: int, todolist_id: int, status: str = None, completed: bool = None) -> list:
        """
        Get a list of to-dos in a to-do list with optional filtering.

        Parameters:
            project_id: The ID of the project containing the to-do list
            todolist_id: The ID of the to-do list to get items from
            status: Filter by status - can be 'archived' or 'trashed'
            completed: Filter for completed (True) or incomplete (False) to-dos

        Returns:
            A list of to-dos with their details including content, assignees,
            completion status, due dates and position
        """
        params = {}
        if status:
            params['status'] = status
        if completed is not None:
            params['completed'] = str(completed).lower()
            
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{todolist_id}/todos.json"
        return self.client.request("GET", url, params=params)

    def get(self, project_id: int, todo_id: int) -> dict:
        """
        Get details about a specific to-do.

        Parameters:
            project_id: The ID of the project containing the to-do
            todo_id: The ID of the to-do to retrieve

        Returns:
            To-do information including content, description, assignees,
            completion status, due dates and position
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todos/{todo_id}.json"
        return self.client.request("GET", url)

    def create(self, project_id: int, todolist_id: int, content: str, description: str = None, 
               assignee_ids: list = None, completion_subscriber_ids: list = None, notify: bool = None,
               due_on: str = None, starts_on: str = None) -> dict:
        """
        Create a new to-do in a to-do list.

        Parameters:
            project_id: The ID of the project containing the to-do list
            todolist_id: The ID of the to-do list to create the item in
            content: The title/content of the to-do
            description: Additional details about the to-do in HTML format
            assignee_ids: List of user IDs to assign the to-do to
            completion_subscriber_ids: List of user IDs to notify on completion
            notify: Whether to notify assignees
            due_on: Due date in YYYY-MM-DD format
            starts_on: Start date in YYYY-MM-DD format

        Returns:
            The created to-do's information including ID, content, assignees and dates
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{todolist_id}/todos.json"
        
        data = {"content": content}
        if description:
            data["description"] = description
        if assignee_ids:
            data["assignee_ids"] = assignee_ids
        if completion_subscriber_ids:
            data["completion_subscriber_ids"] = completion_subscriber_ids
        if notify is not None:
            data["notify"] = notify
        if due_on:
            data["due_on"] = due_on
        if starts_on:
            data["starts_on"] = starts_on

        return self.client.request("POST", url, json=data)

    def update(self, project_id: int, todo_id: int, content: str, description: str = None, 
               assignee_ids: list = None, completion_subscriber_ids: list = None,
               notify: bool = None, due_on: str = None, starts_on: str = None) -> dict:
        """
        Update an existing to-do.

        Parameters:
            project_id: The ID of the project containing the to-do
            todo_id: The ID of the to-do to update
            content: The updated title/content of the to-do
            description: Updated details about the to-do in HTML format
            assignee_ids: Updated list of user IDs to assign the to-do to
            completion_subscriber_ids: Updated list of user IDs to notify on completion
            notify: Whether to notify assignees of changes
            due_on: Updated due date in YYYY-MM-DD format
            starts_on: Updated start date in YYYY-MM-DD format

        Returns:
            The updated to-do's information including content, assignees and dates
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todos/{todo_id}.json"
        
        data = {"content": content}
        if description is not None:
            data["description"] = description
        if assignee_ids is not None:
            data["assignee_ids"] = assignee_ids
        if completion_subscriber_ids is not None:
            data["completion_subscriber_ids"] = completion_subscriber_ids
        if notify is not None:
            data["notify"] = notify
        if due_on is not None:
            data["due_on"] = due_on
        if starts_on is not None:
            data["starts_on"] = starts_on

        return self.client.request("PUT", url, json=data)

    def complete(self, project_id: int, todo_id: int):
        """
        Mark a to-do as completed.

        Parameters:
            project_id: The ID of the project containing the to-do
            todo_id: The ID of the to-do to complete
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todos/{todo_id}/completion.json"
        self.client.request("POST", url)

    def uncomplete(self, project_id: int, todo_id: int):
        """
        Mark a completed to-do as incomplete.

        Parameters:
            project_id: The ID of the project containing the to-do
            todo_id: The ID of the to-do to uncomplete
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todos/{todo_id}/completion.json"
        self.client.request("DELETE", url)

    def reposition(self, project_id: int, todo_id: int, position: int):
        """
        Change the position of a to-do in its list.

        Parameters:
            project_id: The ID of the project containing the to-do
            todo_id: The ID of the to-do to reposition
            position: The new position (must be >= 1)

        Raises:
            ValueError: If position is less than 1
        """
        if position < 1:
            raise ValueError("Position must be greater than or equal to 1")
            
        url = f"{self.client.api_url}/buckets/{project_id}/todos/{todo_id}/position.json"
        data = {"position": position}
        self.client.request("PUT", url, json=data)