#OmniCart Pipeline
OmniCart Data Pipeline is a Python-based tool designed to extract, transform, and load (ETL) product data from the OmniCart API into a clean and structured dataset. It automates data retrieval, cleaning, and integration processes while ensuring consistent performance and scalability. The project demonstrates an advanced data engineering pipeline suitable for analytics and integration tasks within modern retail systems.

Installation Instructions:
You can install the package using pip after building it locally or from an internal repository.
Command: pip install omnicart-pipeline

Usage Guide:
After installation, you can run the pipeline directly from the command line using the CLI entry point.
Command: omnicart-pipeline
This will trigger the main data extraction and processing workflow as defined in the CLI module.

Package Data Solution:
To ensure that the configuration file (pipeline.cfg) is always accessible after installation, even when the package is installed through pip, the project uses Python’s importlib.resources module. This approach dynamically locates the configuration file within the installed package, instead of relying on hardcoded file paths like open('pipeline.cfg'), which would break after installation. Additionally, the pyproject.toml file has been configured to include the .cfg file in the final package distribution so that the application can always find and load it at runtime, regardless of where the package is installed on the system.

This project implements an end-to-end data pipeline for OmniCart — a fictional e-commerce analytics platform.  
It’s designed to demonstrate robust, modular data engineering principles using Python, Poetry, and modern configuration management.

---



 Key Features
- Configurable pipeline with a centralized `pipeline.cfg` file
- Modular architecture with independent components (API client, data analyzer, transformer, etc.)
- Reliable configuration loading using `importlib.resources` (so the config file is always accessible after packaging)
- CLI-based orchestration (`cli.py`) for running the full pipeline
- Pytest test suite under `/tests`
- Poetry-managed environment for dependency isolation

---
Project Structure

omnicart-pipeline-project/
├── omnicart_pipeline/
│ ├── init.py
│ ├── cli.py
│ ├── config.py
│ ├── api_client.py
│ ├── data_analyzer.py
│ ├── data_transformer.py
│ ├── pipeline.cfg
│ └── ...
│
├── tests/
│ ├── test_config.py
│ ├── test_data_analyzer.py
│ ├── test_data_transformer.py
│ └── ...
│
├── poetry.lock
├── pyproject.toml
├── README.md
└── .gitignore

To run
python -m omnicart_pipeline.pipeline.cli(In bash terminal)

Configuration Management
The pipeline reads configuration values from pipeline.cfg using importlib.resources, ensuring it works in both development and packaged environments.

Running Tests
Tests are located under the tests/ directory.


poetry run pytest -v or python -m pytest -v

API Integration
The pipeline can make live API calls for data ingestion.
If your API requires credentials, update the corresponding section in pipeline.cfg.

Author
Obaloluwa Adeleke
Omnicart Pipeline Project

Notes
Ensure internet access for live API tests.
Avoid hardcoding local paths — the configuration loader handles cross-environment access.

