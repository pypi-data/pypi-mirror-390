from bcapi.client import BasecampAPIError


class Schedules(object):
    def __init__(self, client):
        """
        Interacts with Schedules in a Basecamp project.

        Parameters:
            client (Client): An initialized Client object.
        """
        self.client = client

    def get(self, project_id: int, schedule_id: int) -> dict:
        """
        Returns information about a specific schedule.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the schedule.
            schedule_id (int): The ID of the schedule to retrieve.

        Returns:
            dict: Schedule information including status, visibility, entries count etc.
        """
        url = f"{self.client.api_url}/buckets/{project_id}/schedules/{schedule_id}.json"
        return self.client.request("GET", url)

    def update(
        self, project_id: int, schedule_id: int, include_due_assignments: bool
    ) -> dict:
        """
        Updates an existing schedule.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the schedule.
            schedule_id (int): The ID of the schedule to update.
            include_due_assignments (bool): Whether to include due dates from to-dos, cards and steps.

        Returns:
            dict: The updated schedule object
        """
        url = f"{self.client.api_url}/buckets/{project_id}/schedules/{schedule_id}.json"
        data = {
            "schedule": {
                "include_due_assignments": str(include_due_assignments).lower()
            }
        }
        return self.client.request("PUT", url, json=data)
