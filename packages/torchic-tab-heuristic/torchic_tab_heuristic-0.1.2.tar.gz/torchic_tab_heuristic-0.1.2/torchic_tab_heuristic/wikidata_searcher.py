import requests
import time

class WikidataSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TestBot/1.0 (your_email@example.com)"
        })
        self.url = "https://www.wikidata.org/w/api.php"

    def query_name(self, search_string):
        """Searches Wikidata for extra candidates"""
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": search_string
        }

        for attempt in range(3):
            response = self.session.get(self.url, params=params)

            # 1. Check HTTP status
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for query '{search_string}'")
                time.sleep(1)
                continue

            # 2. Try JSON parsing
            try:
                data = response.json()
            except ValueError:
                print("Non-JSON response from Wikidata:")
                print(response.text[:300])  # preview for debugging
                time.sleep(1)
                continue

        entities = []
        titles = []
        for result in data.get("search", []):
            entity_id = result.get("id")
            try:
                titles.append(result["display"]["label"]["value"])
                entities.append(entity_id)
            except KeyError:
                pass  # Ignore entries that don't have expected fields

        return entities, titles
    
    def query_qid(self, qid, names_search):
        """Wikidata API request for names and aliases of IDs"""

        # Parameters for the API request
        params = {
            "action": "wbgetentities",
            "ids": qid,
            "format": "json"
        }

        if names_search :
            params = {
                "action": "wbgetentities",
                "ids": qid,
                "props": "labels|aliases",
                "format": "json"
            }

        # Send the API request and get the response
        try:
            response = self.session.get(self.url, params=params).json()
        except:
            time.sleep(2)
            entity = self.query_qid(qid, names_search)
            return entity

        # Get the entity corresponding to the Wikidata ID
        entity = response["entities"][qid]

        return entity
    
    def close(self):
        """Closes the session"""
        self.session.close()