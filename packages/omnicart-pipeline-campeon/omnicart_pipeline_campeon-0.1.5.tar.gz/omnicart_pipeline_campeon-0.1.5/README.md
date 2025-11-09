# Omnicart Pipeline Campeon

**Omnicart Pipeline Campeon** is a lightweight, modular ETL (Extract, Transform, Load) data pipeline designed to automate the retrieval, enrichment, and analysis of e-commerce data from the [FakeStore API](https://fakestoreapi.com). It demonstrates clean architecture principles, test-driven development, and configuration management (using poetry) for real-world Python projects. The package also illustrates best practices for packaging, including handling non-Python data files like `.cfg` configurations and distributing via PyPI or TestPyPI.

---

## Project Overview

The pipeline is built with modular components that handle each stage of the ETL process:

### Architecture

```
API ConfigFile → API Client → Data Enricher → Data Analyzer
```

### Workflow Breakdown

1. **Config**

   * Reads the `pipeline.cfg` file.
   * Returns `API_ENDPOINT` URL and limit.

2. **API Client**

   * Fetches data from API endpoints (products, users) using the endpoint from config.
   * Supports pagination and handles errors gracefully.

3. **Data Enricher**

   * Converts product and user data to Pandas DataFrames.
   * Joins product and user data on `id`.
   * Unpacks nested dictionary columns.
   * Adds a new column `revenue = price * count`.
   * Checks for missing product/user IDs.

4. **Data Analyzer**

   * Performs aggregations such as:

     * Total revenue per seller
     * Average product price per category
     * Product count per seller
   * Saves analyzed data as a JSON report.

---

## Installation

You can install the package using pip:

* **TestPyPI**

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple omnicart-pipeline-campeon
```

* **PyPI**

```bash
pip install omnicart-pipeline-campeon
```

---

## Usage Guide

After installation, run the pipeline directly from the command line:

```bash
omnicart-pipeline
```

### CLI Example

"omnicart-pipeline" command for the console is defined in `pyproject.toml`:

```toml
[tool.poetry.scripts]
omnicart-pipeline = "omnicart_pipeline.cli:main"
```

---

## Configuration

`pipeline.cfg` contains the pipeline configuration:

```ini
[API_ENDPOINT]
url = https://fakestoreapi.com
limit = 1
```

**Handling Config After Installation**
A key challenge in packaging was ensuring the `pipeline.cfg` file remained accessible **after installation**, no matter where pip installed the package.
To solve this, the project uses Python’s built-in **`importlib.resources`** module.  
Instead of directly opening the file (which breaks after installation), it safely locates it inside the package.  

```python
from importlib import resources

cfg_file = resources.files("omnicart_pipeline").joinpath("pipeline.cfg").read_text()
ConfigManager.config.read_string(cfg_file)
```

Make sure the config file is included in `pyproject.toml`:

```toml
[[tool.poetry.include]]
path = "omnicart_pipeline/pipeline.cfg"
```

---

## Example Run (with logging)

```text

(venv) PS C:\Users\Personal\data_epic\learn_poetry> omnicart-pipeline
..initializing the main program
2025-11-08 17:21:02,439 - INFO : initiating omnicart pipeline...
2025-11-08 17:21:02,439 - INFO : getting necessary values from the config file
2025-11-08 17:21:02,439 - INFO : ..calling product endpoint
2025-11-08 17:21:02,439 - INFO : ..connecting to https://fakestoreapi.com//products/
2025-11-08 17:21:20,800 - INFO : API request failed: Expecting value: line 1 column 1 (char 0)
2025-11-08 17:21:20,802 - INFO : ..calling users endpoint
2025-11-08 17:21:20,802 - INFO : ..connecting to https://fakestoreapi.com//users/
2025-11-08 17:21:31,219 - INFO : ...encountered space, no more data to fetch from the api endpoint
2025-11-08 17:21:31,221 - INFO : enriching data
2025-11-08 17:21:31,221 - INFO : coverting json data to dataframe
2025-11-08 17:21:31,229 - INFO : creating new products columns from nested dictionary
2025-11-08 17:21:31,245 - INFO : The products dataframe has the shape: (20, 8)
2025-11-08 17:21:31,245 - INFO : The users dataframe has the shape: (10, 9)
2025-11-08 17:21:31,245 - INFO : merging new products and users together
2025-11-08 17:21:31,249 - INFO : The merged df has the shape: (20, 17)
2025-11-08 17:21:31,249 - INFO : checking missing user id
2025-11-08 17:21:31,251 - INFO : Missing id found 10
2025-11-08 17:21:31,251 - INFO : analyzing data...
2025-11-08 17:21:31,266 - INFO : data analyzed and saved as seller_performance_report
2025-11-08 17:21:31,271 - INFO : end of omnicart pipeline
```

---

## Testing Strategy (Poetry + Pytest)

Unit tests are written using `pytest` and `unittest.mock`. Poetry ensures that tests run inside the virtual environment:

### Run All Tests

```bash
poetry run pytest 
```

```text


rootdir: C:\Users\Personal\data_epic\week 5\omnicart-pipeline-campeon
configfile: pyproject.toml
plugins: mock-3.15.1
collected 6 items                                                                                                                                                                                                 

tests\test_api_client.py ..                                                                                                                                                                                 [ 33%]
tests\test_config.py .                                                                                                                                                                                      [ 50%] 
tests\test_data_analyzer.py .                                                                                                                                                                               [ 66%]
tests\test_data_enricher.py ..                                                                                                                                                                              [100%]

=============================================================================================== 6 passed in 0.10s ================================================================================================


```

### Run a Single Test

```bash
poetry run pytest tests/test_data_analyzer.py::test_data_analyzer
```

### Test Coverage Report

```bash
poetry run pytest --cov=omnicart_pipeline --cov-report=term-missing
```

```bash
================================================================================================= tests coverage ================================================================================================= 
________________________________________________________________________________ coverage: platform win32, python 3.13.6-final-0 _________________________________________________________________________________ 

Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
omnicart_pipeline\__init__.py            0      0   100%
omnicart_pipeline\api_client.py         37      9    76%   43-56
omnicart_pipeline\cli.py                 7      7     0%   1-11
omnicart_pipeline\config.py             29      3    90%   44, 48, 55
omnicart_pipeline\data_analyzer.py      11      0   100%
omnicart_pipeline\data_enricher.py      37      1    97%   15
omnicart_pipeline\pipeline.py           26     26     0%   1-46
------------------------------------------------------------------
TOTAL                                  147     46    69%
=============================================================================================== 6 passed in 0.24s ===================================================================================

```

This shows which lines of code are covered by tests.

### Test Table

| Module          | Test Objective                               | Mock Usage                                |
| --------------- | -------------------------------------------- | ----------------------------------------- |
| `api_client`    | Ensure pagination, error handling            | Patch `requests.get`                      |
| `data_enricher` | Test joins, missing IDs, revenue calculation | Pandas DataFrame fixtures                 |
| `data_analyzer` | Verify aggregation correctness               | Pytest parametrize with sample DataFrames |
| `config`        | Confirm reading from temp files              | `tmp_path` fixture                        |

---

## Project Structure

```
omnicart-pipeline-campeon/
├── omnicart_pipeline/
│   ├── __init__.py
│   ├── api_client.py
│   ├── cli.py
│   ├── config.py
│   ├── data_analyzer.py
│   ├── data_enricher.py
│   ├── pipeline.py
│   └── pipeline.cfg
├── tests/
├── pyproject.toml
├── poetry.lock
├── requirements.txt
└── README.md
```

---

## Requirements

* Python 3.9+
* pandas >= 2.3.3, < 3.0.0
* requests >= 2.31
* importlib-resources (for older Python versions)

---

## Author

**Oluwaseyi Ogunlana**

---

## License

This project is licensed under the MIT License.
