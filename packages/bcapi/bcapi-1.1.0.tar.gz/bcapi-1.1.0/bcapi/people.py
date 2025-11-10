from bcapi.client import BasecampAPIError

class People(object):
    def __init__(self, client):
        '''
        Interacts with people and user profiles in Basecamp.

        Parameters:
            client (Client): An initialized Client object.
        '''
        self.client = client
 
    def get_profile(self) -> dict:
        '''
        Retrieves information about the authenticated user.
        
        Returns:
            dict: User profile information including name, email, title, etc.
        '''
        url = f"{self.client.api_url}/my/profile.json"
        return self.client.request("GET", url)
