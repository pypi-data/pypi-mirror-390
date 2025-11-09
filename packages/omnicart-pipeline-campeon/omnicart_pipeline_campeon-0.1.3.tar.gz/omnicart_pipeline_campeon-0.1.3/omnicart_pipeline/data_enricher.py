from typing import List, Dict, Any, Iterable
import pandas as pd
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format= "%(asctime)s - %(levelname)s : %(message)s")



class DataEnricher:
  """the enrisher class to clean and enrich the user and product dataframe"""
  
  def __innit__(self):
    self.missing_user_products = pd.DataFrame
  
  def data_enrich(self, products_list :List[Dict[str, Any]], users_list: List[Dict[str, Any]] )  -> pd.DataFrame:

    logging.info('enriching data')

    logging.info('coverting json data to dataframe')
    
    products_df = pd.DataFrame(products_list)
    users_df = pd.DataFrame(users_list)

    logging.info('The head of product dataframe has the shape: %s', products_df.head())

    #breaking down products df
    logging.info('creating new products columns from nested dictionary')
    products_df['rate'] =  products_df['rating'].apply(lambda dict: dict['rate'])
    products_df['count'] =  products_df['rating'].apply(lambda dict: dict['count'])
    products_cols =  [ col for col in products_df.columns if col not in [ 'rating', 'password' ,'username','__v'] ]
    #print(products_cols)
    new_products_df = products_df[products_cols]
    #print(new_productd_df.columns)

    #breaking down users df
    
    
    users_df['lat']=users_df['address'].apply(lambda dict: dict['geolocation']['lat'])
    users_df['long']=users_df['address'].apply(lambda dict: dict['geolocation']['long'])
    users_df['firstname'] = users_df['name'].apply(lambda dict: dict['firstname'])
    users_df['lastname'] = users_df['name'].apply(lambda dict: dict['lastname'])
    users_df['name'] = users_df['firstname'] + ' ' + users_df['lastname']
    
    users_cols =  [ col for col in users_df.columns if col not in ['firstname', 'lastname','__v','image'] ]
    #print(users_cols)
    new_users_df = users_df[users_cols]

    logging.info('The products dataframe has the shape: %s', new_products_df.shape)
    #print(new_products_df.head())
    
    logging.info('The users dataframe has the shape: %s', new_users_df.shape)

    #print(new_users_df.head())

    logging.info('merging new products and users together')

    merged_df = pd.merge(new_products_df, new_users_df, left_on='id', right_on='id', how='left')
    merged_df['revenue'] = merged_df['price'] * merged_df['count'] #apply(lambda dict: dict['count'])

    logging.info('The merged df has the shape: %s', merged_df.shape)


    logging.info('checking missing user id')

    known_user_ids = set(new_users_df['id']) if not new_users_df.empty else set()

    missing_user_products = new_products_df[~new_products_df['id'].isin(known_user_ids)]
    
    self.missing_user_products  = missing_user_products 
    logging.info('Missing id found %s', missing_user_products.shape[0])
    

    #merged_df.to_csv('merged_df.csv')

    return  merged_df