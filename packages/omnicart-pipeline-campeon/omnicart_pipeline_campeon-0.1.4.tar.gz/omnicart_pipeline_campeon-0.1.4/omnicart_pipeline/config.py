import configparser as cp
from typing import List, Dict, Any, Iterable
import logging
from importlib import resources
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format= "%(asctime)s - %(levelname)s : %(message)s")




"""
config_write = cp.ConfigParser()

config_write['API_ENDPOINT'] = {}

config_write['API_ENDPOINT']['limit'] = '1' 
config_write['API_ENDPOINT']['url'] = 'https://fakestoreapi.com/'
with open('pipeline.cfg', 'w') as config_file:
  config_write.write(config_file)

config_read = configparser.ConfigParser()
config_read.read('pipeline.cfg')
config_read['API_ENDPOINT']['limit']

"""
 

class ConfigManager:
  """A configg manager class that reads the configuration file"""

  #a class variacle to instantiate the config parser
  config = cp.ConfigParser()

  def __init__(self, config_path: str,section: str):
    self._cfg_file = resources.files("omnicart_pipeline").joinpath("pipeline.cfg").read_text()
    self.config_path = config_path
    self.section = section
    self._url = ''
    self._limit = 0

  @property
  def url(self):
    return self._url
  
  @property
  def limit(self):
    return self._limit

  def read_api_config(self) -> Dict[str, Any]:
    """The method that read variables from the config files"""
    #ConfigManager.config.read(self.config_path)
    ConfigManager.config.read_string(self._cfg_file)
    if self.section not in ConfigManager.config:
        raise ValueError(f"{self.section} section not found in config.ini")
    else:
      logging.info('getting necessary values from the config file')
      self._url = ConfigManager.config[self.section]['url']
      self._limit = ConfigManager.config[self.section]['limit']
      return {'url': self._url,  'limit': self._limit}