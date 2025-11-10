from bcapi.client import BasecampAPIError


class TodolistGroups:
    def __init__(self, client):
        self.client = client

    def list(self, project_id, todolist_id, status=None):
        """
        Get a list of active to-do list groups in a project's to-do list.
        """
        params = {}
        if status:
            params["status"] = status
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{todolist_id}/groups.json"
        return self.client.request("GET", url, params=params)

    def get(self, project_id, todolist_id):
        """
        Get a specific to-do list group.
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{todolist_id}/groups.json"
        return self.client.request("GET", url)

    def create(self, project_id, todolist_id, name, color=None):
        """
        Create a new to-do list group.
        """
        url = f"{self.client.api_url}/buckets/{project_id}/todolists/{todolist_id}/groups.json"
        data = {"name": name}
        if color:
            data["color"] = color

        return self.client.request("POST", url, json=data)

    def reposition(self, project_id, group_id, position):
        """
        Change the position of a to-do list group.
        """
        if position < 1:
            raise ValueError("Position must be greater than or equal to 1")

        url = f"{self.client.api_url}/buckets/{project_id}/todolists/groups/{group_id}/position.json"
        data = {"position": position}

        return self.client.request("PUT", url, json=data)
