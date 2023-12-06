import requests


class CustomSearch:
    """
    Class which allows the application to do a web search by using the
    Google Custom Search API.

    Attributes:
        api_key (str): API key for accessing the Google Custom Search
        API.

        search_engine_id (str): The custom search engine ID for Google
        Custom Search.

        root_url (str): root URL for the Google Custom Search API.
    """

    def __init__(self):
        """
        Initializes the CustomSearch instance with default attribute
        values.
        """
        self.api_key = None
        self.search_engine_id = None
        self.root_url = 'https://www.googleapis.com/customsearch/v1'

    def read_api_key_and_search_engine_id(self):
        """
        Reads the API Key and Search Engine ID from the 'API_KEY.key'
        and 'SEARCH_ENGINE_ID.key' files.

        Raises:
            IOError: Gets triggered if the .key files are not found.
        """
        try:
            with open('API_KEY.key', 'r') as f:
                self.api_key = f.readline().strip()

            with open('SEARCH_ENGINE_ID.key', 'r') as f:
                self.search_engine_id = f.readline().strip()

        except FileNotFoundError:
            raise IOError('search.key file not found')

    def run_query(self, search_terms):
        """
        Runs a search query using the Google Custom Search API.

        Args:
            search_terms (str): The term that the user wants to search.
        
        Returns:
            results (list): A list of dictionaries containing search
            results with 'title', 'link', and 'snippet' keys.
        """
        self.read_api_key_and_search_engine_id()

        if not self.api_key and not self.search_engine_id:
            raise KeyError('API key not found')

        params = {
            'q': search_terms,
            'key': self.api_key,
            'cx': self.search_engine_id,
            'num': "10"
        }

        results = []

        try:
            response = requests.get(self.root_url, params=params)
            print(response)
            json_response = response.json()

            for item in json_response.get('items'):
                results.append({'title': item['title'],
                                'link': item['link'],
                                'snippet': item['snippet']})
        except requests.exceptions.RequestException as e:
            print(e)

        return results
