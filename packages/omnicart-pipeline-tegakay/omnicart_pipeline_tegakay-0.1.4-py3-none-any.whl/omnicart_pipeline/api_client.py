import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class APIClient:
    def __init__(self, base_url):
        if not base_url:
            raise ValueError("Base URL cannot be empty.")
        
        self.base_url = base_url
    
    def _make_request(self,endpoint:str):
        url = self.base_url + endpoint
        try:
            response = requests.get(url)   
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An unexpected error occurred: {req_err}")
        
        return None
    def get_all_products(self,start=1,limit=10):
       response = self._make_request("/products")

       product_count = (start - 1) * limit
       if response is not None:
           return response[product_count:product_count+limit]
    
    def get_all_users(self):
        return self._make_request("/users")

