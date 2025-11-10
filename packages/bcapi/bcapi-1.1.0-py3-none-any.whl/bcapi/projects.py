from bcapi.client import BasecampAPIError


class Projects:
    def __init__(self, client):
        """
        Interacts with Basecamp Projects.

        Parameters:
            client (Client): An initialized Client object.
        """
        self.client = client

    def list(self, status: str = None) -> list:
        """
        Returns all projects visible to the current user.

        Parameters:
            status (str, optional): Filter by status - can be 'archived' or 'trashed'

        Returns:
            list: A list of all projects matching the filter
        """
        params = {}
        if status:
            params["status"] = status

        url = f"{self.client.api_url}/projects.json"
        return self.client.request("GET", url, params=params)

    def get(self, project_id: int) -> dict:
        """
        Returns information about a specific project.

        Parameters:
            project_id (int): The ID of the project to retrieve.

        Returns:
            dict: Project information including name, description, dock tools etc.
        """
        url = f"{self.client.api_url}/projects/{project_id}.json"
        return self.client.request("GET", url)

    def create(self, name: str, description: str = "") -> dict:
        """
        Creates a new project.

        Parameters:
            name (str): Name of the project.
            description (str, optional): Description of the project.

        Returns:
            dict: The created project object

        Raises:
            BasecampAPIError: If project creation fails, including if project limit is reached
        """
        data = {"name": name, "description": description}
        url = f"{self.client.api_url}/projects.json"
        return self.client.request("POST", url, json=data)

    def update(
        self,
        project_id: int,
        name: str,
        description: str = None,
        admissions: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> dict:
        """
        Updates an existing project.

        Parameters:
            project_id (int): The ID of the project to update
            name (str): Updated name for the project
            description (str, optional): Updated description
            admissions (str, optional): Access policy - can be 'invite', 'employee', or 'team'
            start_date (str, optional): Project start date in YYYY-MM-DD format
            end_date (str, optional): Project end date in YYYY-MM-DD format

        Returns:
            dict: The updated project object
        """
        data = {"name": name}

        if description is not None:
            data["description"] = description
        if admissions:
            data["admissions"] = admissions

        if start_date or end_date:
            if not (start_date and end_date):
                raise ValueError(
                    "Both start_date and end_date must be provided together"
                )
            data["schedule_attributes"] = {
                "start_date": start_date,
                "end_date": end_date,
            }

        url = f"{self.client.api_url}/projects/{project_id}.json"
        return self.client.request("PUT", url, json=data)

    def delete(self, project_id: int):
        """
        Moves a project to trash. Projects in trash will be deleted after 30 days.

        Parameters:
            project_id (int): The ID of the project to trash
        """
        url = f"{self.client.api_url}/projects/{project_id}.json"
        self.client.request("DELETE", url)
