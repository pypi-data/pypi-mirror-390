from bcapi.client import BasecampAPIError


class ScheduleEntries(object):
    def __init__(self, client):
        """
        Interacts with Schedule Entries in a Basecamp project.

        Parameters:
            client (Client): An initialized Client object.
        """
        self.client = client

    def list(self, project_id: int, schedule_id: int, status: str = None) -> list:
        """
        Returns all schedule entries in a schedule.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the schedule.
            schedule_id (int): ID of the schedule containing the entries.
            status (str, optional): Filter by status - can be 'archived' or 'trashed'

        Returns:
            list: A list of all schedule entries matching the filter
        """
        url = f"{self.client.api_url}/buckets/{project_id}/schedules/{schedule_id}/entries.json"
        params = {}
        if status:
            params["status"] = status
        return self.client.request("GET", url, params=params)

    def get(self, project_id: int, entry_id: int) -> dict:
        """
        Returns information about a specific schedule entry.

        Parameters:
            project_id (int): The ID of the Basecamp project containing the entry.
            entry_id (int): The ID of the schedule entry to retrieve.

        Returns:
            dict: Schedule entry information including title, description, timing details etc.
        """
        url = f"{self.client.api_url}/buckets/{project_id}/schedule_entries/{entry_id}.json"
        return self.client.request("GET", url)

    def create(
        self,
        project_id: int,
        schedule_id: int,
        summary: str,
        starts_at: str,
        ends_at: str,
        description: str = None,
        participant_ids: list = None,
        all_day: bool = None,
        notify: bool = None,
    ) -> dict:
        """
        Creates a new schedule entry.

        Parameters:
            project_id (int): The ID of the Basecamp project.
            schedule_id (int): The ID of the schedule to create the entry in.
            summary (str): What this schedule entry is about.
            starts_at (str): Date-time (ISO 8601) for when this schedule entry begins.
            ends_at (str): Date-time (ISO 8601) for when this schedule entry ends.
            description (str, optional): Additional details about the entry. Can contain HTML tags.
            participant_ids (list, optional): List of people IDs that will participate.
            all_day (bool, optional): Whether this is an all-day event.
            notify (bool, optional): Whether to notify participants.

        Returns:
            dict: The created schedule entry object
        """
        url = f"{self.client.api_url}/buckets/{project_id}/schedules/{schedule_id}/entries.json"

        data = {"summary": summary, "starts_at": starts_at, "ends_at": ends_at}

        if description is not None:
            data["description"] = description
        if participant_ids is not None:
            data["participant_ids"] = participant_ids
        if all_day is not None:
            data["all_day"] = all_day
        if notify is not None:
            data["notify"] = notify

        return self.client.request("POST", url, json=data)

    def update(
        self,
        project_id: int,
        entry_id: int,
        summary: str = None,
        starts_at: str = None,
        ends_at: str = None,
        description: str = None,
        participant_ids: list = None,
        all_day: bool = None,
        notify: bool = None,
    ) -> dict:
        """
        Updates an existing schedule entry.

        Parameters:
            project_id (int): The ID of the Basecamp project.
            entry_id (int): The ID of the schedule entry to update.
            summary (str, optional): Updated summary of what this entry is about.
            starts_at (str, optional): Updated start date-time (ISO 8601).
            ends_at (str, optional): Updated end date-time (ISO 8601).
            description (str, optional): Updated description. Can contain HTML tags.
            participant_ids (list, optional): Updated list of participant IDs.
            all_day (bool, optional): Whether this is an all-day event.
            notify (bool, optional): Whether to notify participants.

        Returns:
            dict: The updated schedule entry object
        """
        url = f"{self.client.api_url}/buckets/{project_id}/schedule_entries/{entry_id}.json"

        data = {}
        if summary is not None:
            data["summary"] = summary
        if starts_at is not None:
            data["starts_at"] = starts_at
        if ends_at is not None:
            data["ends_at"] = ends_at
        if description is not None:
            data["description"] = description
        if participant_ids is not None:
            data["participant_ids"] = participant_ids
        if all_day is not None:
            data["all_day"] = all_day
        if notify is not None:
            data["notify"] = notify

        return self.client.request("PUT", url, json=data)
