import requests

from typing import Generator, Any



class APIClient():
    """Handles all API communication"""    

    def get_products(self, base_url: str, limit: int) -> Generator[list[dict[str, Any]], None, None]:
        try:
            response =  requests.get(base_url + '/products', timeout=5)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise TimeoutError("The request time out while trying to reach the server")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to establish connection to the server")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error occurred: {e.response.status_code}")

        products = response.json()
        #pagination logic
        for i in range(0, len(products), limit):
            yield products[i:i+limit]
            
    def get_users(self, base_url: str) -> list[dict[str, Any]]:
        try:
            response =  requests.get(base_url + '/users')
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise TimeoutError("The request time out while trying to reach the server")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to establish connection to the server")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error occurred: {e.response.status_code}")

        users = response.json()
        return users          
        
        