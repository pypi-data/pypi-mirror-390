import requests
from typing import List, Dict, Any, Iterable
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format= "%(asctime)s - %(levelname)s : %(message)s")

class ApiClient:
  """ Ths class connect to an API endpoint to fetch data"""

  def get_endpoint_data(self, endpoint: str, url: str, limit: str) -> Iterable[Dict[str, Any]]:
    """ The is a generic method that uses the endpoint , url and limit passed to get data from the api"""

    endpoint_url = f"{url}/{endpoint}/"
    logging.info('..connecting to %s', endpoint_url)
    #print(endpoint_url)
    #print(type(limit))
    endpoint_limit:int =  int(limit)  #= 1 # limit
    #print('----', type(int(endpoint_limit)))
   # max_product_limit = limit

    while endpoint_limit:
      try: 
        new_endpoint_link = f"{endpoint_url}/{endpoint_limit}"
        logging.debug('..connecting to %s', endpoint_url)
        #print(new_endpoint_link)
        response = requests.get(new_endpoint_link)
        response.raise_for_status()
       
        endpoint_data = response.json()

        if not endpoint_data:

        #if len(response.json()) > 0:
          #yield response.json()
        #else:
          logging.info('...encountered space, no more data to fetch from the api endpoint')
          break
        
        yield  endpoint_data
        endpoint_limit += 1
      except requests.exceptions.HTTPError as http_err:
        #print(f"HTTP error occurred: {http_err}")
        logging.info('HTTP error occurred: %s', http_err)
        return []

      except requests.exceptions.RequestException as resq_err:
        #print(f"API request failed: {resq_err}")
        logging.info('API request failed: %s', resq_err)
        return []

      except Exception as err:
        logging.info('%s error occurred', err)
        #print(f"Other error occurred: {err}")
        return []
      
  def get_all_products(self, product_endpoint: str, url: str, limit: str) -> List[Dict[str, Any]]:
    """The get product method that i called to fetch products data from the API"""
    logging.info('..calling product endpoint')
    return self.get_endpoint_data(product_endpoint, url, limit)

  def get_all_users(self, user_endpoint: str, url: str, limit: str) -> List[Dict[str, Any]]:
    """The get users method that i called to fetch products data from the API"""
    logging.info('..calling users endpoint')
    return self.get_endpoint_data(user_endpoint, url, limit)