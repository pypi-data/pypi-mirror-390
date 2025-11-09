from  omnicart_pipeline.api_client import ApiClient
from  omnicart_pipeline.config import ConfigManager
from  omnicart_pipeline.data_enricher import DataEnricher
from  omnicart_pipeline.data_analyzer import DataAnalyzer
import json

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format= "%(asctime)s - %(levelname)s : %(message)s")

#config_path = 'C:\Users\Personal\data_epic\week_4\omnicart_pipeline\pipeline.cfg'

class Pipeline:
  def __init__(self, config_path: str = r'C:\Users\Personal\data_epic\week_4\omnicart_pipeline\pipeline.cfg', end_point: str ='API_ENDPOINT'):
    self.conf_man = ConfigManager(config_path, end_point)
    self.api_client = ApiClient()
    self.enrich_api_data = DataEnricher() 
    self.ana_api_data = DataAnalyzer() 
 
  
  def run(self):

    logging.info('initiating omnicart pipeline...')

    api_config = self.conf_man.read_api_config()
    #print(type(api_config.get('limit')))
    api_prod_data = list(self.api_client.get_all_products('products',api_config.get('url'), api_config.get('limit')))
    
    #print(len(api_prod_data))
    api_users_data = list(self.api_client.get_all_users('users',api_config.get('url'), api_config.get('limit')))
    #print(len(api_users_data))
    enrich_api_df = self.enrich_api_data.data_enrich(api_prod_data, api_users_data)
    #print(enrich_api_df) 
    self.ana_api_data.analyze(enrich_api_df)

    
    with open('users.json','w') as file:
      json.dump(api_users_data, file)

    with open('products.json','w') as file:
      json.dump(api_prod_data, file)
    

    logging.info('end of omnicart pipeline')

    
    