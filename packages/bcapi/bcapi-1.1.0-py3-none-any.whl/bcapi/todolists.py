from bcapi.client import BasecampAPIError


class TodoLists(object):
    def __init__(self, client):
        """
        Interacts with Todo Lists in a Basecamp project.

        Parameters:
            client (Client): An initialized Client object.
        """
        self.client = client

    def list(self, project_id: int, todoset_id: int, status: str = None) -> list:
        """
        Returns all todo lists in the todoset.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the Todo Lists.
            todoset_id (int): ID of the Todo Set containing the lists.
            status (str, optional): Filter by status - can be 'archived' or 'trashed'

        Returns:
            list: A list of all todo lists
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todosets/{todoset_id}/todolists.json"
        params = {}
        if status:
            params["status"] = status
        return self.client.request("GET", url, params=params)

    def get(self, project_id: int, list_id: int) -> dict:
        """
        Returns information about a specific todo list.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the Todo Lists.
            list_id (int): The ID of the todo list to retrieve.

        Returns:
            dict: Todo list information including title, description, completion status etc.
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{list_id}.json"
        return self.client.request("GET", url)

    def create(
        self, project_id: int, todoset_id: int, name: str, description: str = ""
    ) -> dict:
        """
        Creates a new todo list.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the Todo Lists.
            todoset_id (int): ID of the Todo Set containing the lists.
            name (str): Name of the todo list.
            description (str, optional): Description of the todo list. Can contain HTML tags.

        Returns:
            dict: The created todo list object
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todosets/{todoset_id}/todolists.json"
        data = {"name": name, "description": description}
        return self.client.request("POST", url, json=data)

    def update(
        self, project_id: int, list_id: int, name: str, description: str = ""
    ) -> dict:
        """
        Updates an existing todo list.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the Todo Lists.
            list_id (int): The ID of the todo list to update.
            name (str): Updated name for the todo list.
            description (str, optional): Updated description for the todo list.

        Returns:
            dict: The updated todo list object
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{list_id}.json"
        data = {"name": name, "description": description}
        return self.client.request("PUT", url, json=data)
