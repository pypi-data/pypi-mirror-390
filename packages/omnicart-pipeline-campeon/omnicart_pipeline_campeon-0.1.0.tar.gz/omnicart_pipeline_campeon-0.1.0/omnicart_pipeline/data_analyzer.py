from typing import List, Dict, Any, Iterable
import pandas as pd
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format= "%(asctime)s - %(levelname)s : %(message)s")


class DataAnalyzer:
  """The class Analyzer that generate a summary for the api data that has been converted to dataframe"""
  
  
  def analyze(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    logging.info('analyzing data...')
    agg_df = df.groupby('name').agg(
    total_revenue=('revenue', 'sum'),
    product_count=('id', 'count'),
    average_price=('price', 'mean')
    )
    
    logging.info('data analyzed and saved as seller_performance_report')
    return agg_df.to_dict() #agg_df.to_json('seller_performance_report.json')#agg_df.to_dict()
    