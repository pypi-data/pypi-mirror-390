from bcapi.client import BasecampAPIError

class TodoSets:
    """Class to interact with Basecamp 3 To-do Sets endpoints"""
    
    def __init__(self, client):
        """Initialize with a Basecamp client instance"""
        self.client = client

    def get(self, bucket_id, todoset_id):
        """
        Get a specific to-do set from a project.
        
        Args:
            bucket_id (int): The ID of the project
            todoset_id (int): The ID of the to-do set
            
        Returns:
            Dict containing to-do set details including:
                - id (int)
                - status (str)
                - visible_to_clients (bool)
                - created_at (str)
                - updated_at (str)
                - title (str)
                - type (str)
                - completed (bool)
                - completed_ratio (str)
                - todolists_count (int)
                - todolists_url (str)
                - and other metadata
        """
        url = f"{self.client.api_url}/buckets/{bucket_id}/todosets/{todoset_id}.json"
        return self.client.request("GET", url)