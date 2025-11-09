
# Omnicart Data Pipeline

## Overview
The **Omnicart Data Pipeline** is a modular ETL (Extract, Transform, Load) system designed to automate the fetching, transformation, enrichment, and analysis of e-commerce data from the FakeStore API.  
It demonstrates how to structure a real-world data pipeline using clean architecture principles, configuration management, and test-driven development. It uses logging to show the modules interactions.

---

## Architecture Overview

```
API ConfigFile → Api Client → Data Enricher → Data Analyzer 
```

## Workflow Breakdown

### 1. **Config**
- Reads the API pipeline config file.
- Return the API_ENDPOINT url and limit

### 2. **API Client**
- Uses the API_ENDPOINT values to fetches data from API endpoints ( `products`, `users`).
- Supports pagination and graceful error handling using try-except blocks.

### 3. **Data Enricher**
- Convert extracted product and user data to a dataframe.
- Joins product and user dataframe on `id`.
- Checks if there are product id that is not in the user dataframe.
- Also unpack the columns that are nested in a dictionary (using apply and lambda)
- Adds a new columns revenue (`price * count`).

### 4. **Data Analyzer**
 - Performs group-by aggregations such as:
  - Total revenue per seller
  - Average product price per category
  - Product count per seller
  - Saves the analyzed data to a json file.
 

---

## Testing Strategy

###  Unit Tests (Pytest + Mocking)
Each pipeline stage is tested in isolation using **pytest** and **unittest.mock** to simulate dependencies.

| Module | Test Objective | Mock Usage | 
|--------|----------------|------------|
| `test_api_client` | Ensure API pagination, side effect, and a breakout when there is no data and response handling | `requests.get` patched |
| `test_data_enricher` | Test joins with matching and missing id.test the calculated column (revenue) | Pandas DataFrame fixtures |
| `test_data_analyzer` | Verify aggregation correctness | Pytest Parametrize (Sample DataFrame comparison) |
| `test_config` | Confirm config reading from temp file and if the url and limit values are correct | Uses `tmp_path` fixture |

---

## Folder Structure

```
omnicart_pipeline/
├── pipeline/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config.py
│   ├── data_analyzer.py
│   ├── data_enricher.py
│   └── pipeline.py
│
├── tests/
│   ├── test_api_client.py
│   ├── test_data_enricher.py
│   ├── test_data_analyzer.py
│   ├── test_config.py
│   └── conftest.py
├── main.py
├── pipeline.cfg       
├── requirements.txt
├── .gitignore
└── README.md

```
 
## Running the Project

### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate 
```

### Install Requirements
```bash
pip install -r requirements.txt
```

### Run the Pipeline
```bash
python  main.py 
```

### Configuration (pipeline.cfg)

```ini
[API_ENDPOINT]
url = https://fakestoreapi.com
limit = 1
```

### Example Output (with logging.info)
```
PS C:\Users\Personal\data_epic\week_4\omnicart_pipeline> python  main.py  
2025-11-01 13:39:21,851 - INFO : initiating omnicart pipeline...
2025-11-01 13:39:21,862 - INFO : getting necessary values from the config file
2025-11-01 13:39:21,862 - INFO : ..calling product endpoint
2025-11-01 13:39:21,863 - INFO : ..connecting to https://fakestoreapi.com//products/
2025-11-01 13:39:49,104 - INFO : API request failed: Expecting value: line 1 column 1 (char 0)
2025-11-01 13:39:49,108 - INFO : ..calling users endpoint
2025-11-01 13:39:49,108 - INFO : ..connecting to https://fakestoreapi.com//users/
2025-11-01 13:40:04,099 - INFO : ...encountered space, no more data to fetch from the api endpoint
2025-11-01 13:40:04,102 - INFO : enriching data
2025-11-01 13:40:04,102 - INFO : coverting json data to dataframe
2025-11-01 13:40:04,132 - INFO : creating new products columns from nested dictionary
2025-11-01 13:40:04,167 - INFO : The products dataframe has the shape: (20, 8)
2025-11-01 13:40:04,168 - INFO : The users dataframe has the shape: (10, 9)
2025-11-01 13:40:04,168 - INFO : merging new products and users together
2025-11-01 13:40:04,183 - INFO : The merged df has the shape: (20, 17)
2025-11-01 13:40:04,183 - INFO : checking missing user id
2025-11-01 13:40:04,188 - INFO : Missing id found 10
2025-11-01 13:40:04,189 - INFO : analyzing data...
2025-11-01 13:40:04,223 - INFO : data analyzed and saved as seller_performance_report
2025-11-01 13:40:04,231 - INFO : end of omnicart pipeline
```

### Run All Tests
```bash
pytest --cov=pipeline tests/

pytest -v
```

```
tests/test_api_client.py::test_api_client_pyt PASSED                                                                            [16%] 
tests/test_api_client.py::test_api_client_unt PASSED                                                                                                                                                                                                     [33%] 
tests/test_config.py::test_config_manager_reads_values PASSED                                                                                                                                                                                            [50%]
tests/test_data_analyzer.py::test_data_analyzer[expected_action0] PASSED                                                                                                                                                                                 [66%]
tests/test_data_enricher.py::test_data_enricher PASSED                                                                                                                                                                                                   [83%] 
tests/test_data_enricher.py::test_data_enricher_edge_case PASSED    
```

---
## Requirements.txt

- Python==3.13.6  
- pytest==8.4.2 (for testing)
- pytest-mock==3.15.1 (for mocking)
- pluggy==1.6.0 (dependency for pytest)
- request==2.32.5 (to connect to API endpoint)
- pytest-cov==7.0.0 (check the pytest coverage)
- pandas==2.3.3 (dataframe and analysis)
 