"""Module for interacting with Basecamp 3 Recording endpoints.

This module provides the Recordings class for managing generic recordings in Basecamp
projects. Recordings represent most data structures in Basecamp including comments,
documents, messages, todos, etc. The class allows listing recordings by type and
managing their status (active, archived, trashed).
"""

from typing import List, Dict, Optional, Union
from enum import Enum


class RecordingType(Enum):
    """Valid recording types that can be queried."""

    COMMENT = "Comment"
    DOCUMENT = "Document"
    MESSAGE = "Message"
    QUESTION_ANSWER = "Question::Answer"
    SCHEDULE_ENTRY = "Schedule::Entry"
    TODO = "Todo"
    TODOLIST = "Todolist"
    UPLOAD = "Upload"
    VAULT = "Vault"


class RecordingStatus(Enum):
    """Valid status values for recordings."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    TRASHED = "trashed"


class RecordingSortField(Enum):
    """Valid sort fields for listing recordings."""

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class RecordingSortDirection(Enum):
    """Valid sort directions for listing recordings."""

    ASC = "asc"
    DESC = "desc"


class Recordings:
    """Class to interact with Basecamp 3 Recording endpoints"""

    def __init__(self, client):
        """
        Initialize with a Basecamp client instance.

        Parameters:
            client: An authenticated Basecamp Client instance for making API requests
        """
        self.client = client

    def list(
        self,
        recording_type: Union[RecordingType, str],
        bucket_ids: Optional[Union[int, List[int]]] = None,
        status: Optional[Union[RecordingStatus, str]] = None,
        sort: Optional[Union[RecordingSortField, str]] = None,
        direction: Optional[Union[RecordingSortDirection, str]] = None,
    ) -> List[Dict]:
        """
        Get a list of recordings filtered by type and other criteria.

        Parameters:
            recording_type: Type of recording to list - must be one of RecordingType values
            bucket_ids: Optional project ID(s) to filter by. Can be single ID or list.
            status: Optional status filter - one of RecordingStatus values
            sort: Optional field to sort by - one of RecordingSortField values
            direction: Optional sort direction - one of RecordingSortDirection values

        Returns:
            List of recording objects matching the specified criteria

        Raises:
            ValueError: If an invalid recording type is provided
        """
        # Convert enum members to their values if needed
        if isinstance(recording_type, RecordingType):
            recording_type = recording_type.value
        if isinstance(status, RecordingStatus):
            status = status.value
        if isinstance(sort, RecordingSortField):
            sort = sort.value
        if isinstance(direction, RecordingSortDirection):
            direction = direction.value

        # Validate recording type
        if recording_type not in [t.value for t in RecordingType]:
            raise ValueError(f"Invalid recording type: {recording_type}")

        params = {"type": recording_type}

        # Handle bucket IDs
        if bucket_ids:
            if isinstance(bucket_ids, (list, tuple)):
                params["bucket"] = ",".join(str(id) for id in bucket_ids)
            else:
                params["bucket"] = str(bucket_ids)

        if status:
            params["status"] = status
        if sort:
            params["sort"] = sort
        if direction:
            params["direction"] = direction

        url = f"{self.client.api_url}/projects/recordings.json"
        return self.client.request("GET", url, params=params)

    def trash(self, project_id: int, recording_id: int) -> None:
        """
        Mark a recording as trashed.

        Parameters:
            project_id: The ID of the project containing the recording
            recording_id: The ID of the recording to trash
        """
        url = f"{self.client.api_url}/buckets/{project_id}/recordings/{recording_id}/status/trashed.json"
        self.client.request("PUT", url)

    def archive(self, project_id: int, recording_id: int) -> None:
        """
        Mark a recording as archived.

        Parameters:
            project_id: The ID of the project containing the recording
            recording_id: The ID of the recording to archive
        """
        url = f"{self.client.api_url}/buckets/{project_id}/recordings/{recording_id}/status/archived.json"
        self.client.request("PUT", url)

    def unarchive(self, project_id: int, recording_id: int) -> None:
        """
        Mark a recording as active (unarchive it).

        Parameters:
            project_id: The ID of the project containing the recording
            recording_id: The ID of the recording to unarchive
        """
        url = f"{self.client.api_url}/buckets/{project_id}/recordings/{recording_id}/status/active.json"
        self.client.request("PUT", url)
