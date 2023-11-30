import requests


def read_webhose_key():
    api_key = None
    try:
        with open('API_KEY.key', 'r') as f:
            api_key = f.readline().strip()

        with open('SEARCH_ENGINE_ID.key', 'r') as f:
            search_engine_id = f.readline().strip()

    except Exception:
        raise IOError('search.key file not found')

    return api_key, search_engine_id


def run_query(search_terms):
    api_key, search_engine_id = read_webhose_key()

    if not api_key and not search_engine_id:
        raise KeyError('API key not found')

    root_url = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': search_terms,
        'key': api_key,
        'cx': search_engine_id,
        'num': "10"
    }

    results = []

    try:
        response = requests.get(root_url, params=params)
        print(response)
        json_response = response.json()

        for item in json_response.get('items'):
            results.append({'title': item['title'],
                            'link': item['link'],
                            'snippet': item['snippet']})   
    except requests.exceptions.RequestException as e:
        print(e)

    return results
