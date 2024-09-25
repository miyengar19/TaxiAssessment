# Taxi Trip Data Ingestion and Retrieval System

This project is designed to ingest and retrieve taxi trip data stored in Parquet files using a PostgreSQL database. It supports batch loading of multiple Parquet files and exporting specific results based on a materialized view.

## Project Structure

- `db_utils.py`: Contains utility functions for connecting to the PostgreSQL database.
- `Ingestion.py`: Script to load data from Parquet files into the PostgreSQL database.
- `Retrieval.py`: Script to retrieve the top 10% of trip data based on trip distance and export it to a CSV file.
- `requirements.txt`: Lists the Python packages required to run the project.

## Prerequisites

Before running the scripts, you need to have the following installed:

1. **Python 3.8+**
2. **PostgreSQL** (Ensure PostgreSQL is running and configured properly)

### Python Dependencies

Install the necessary Python libraries using `pip`:

```bash
pip install -r requirements.txt
