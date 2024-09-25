import os
import sys
import pandas as pd
from psycopg2.extras import execute_batch
from db_utils import connect_to_db  # Importing the common database connection function

def create_table_yellow_tripdata(cursor):
    """ Create the yellow_tripdata table if it does not exist """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS yellow_tripdata (
        VendorID INT,
        pickup_datetime TIMESTAMP,
        pep_dropoff_datetime TIMESTAMP,
        trip_distance NUMERIC
    );
    """
    cursor.execute(create_table_query)
    print("Checked/created yellow_tripdata table successfully.")

def load_parquet_file(filepath):
    """ Load specific data from a Parquet file into a DataFrame """
    columns_to_load = ['VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'trip_distance']
    return pd.read_parquet(filepath, columns=columns_to_load)


def create_record_count_table(cursor):
    """ Create a table to store the count of records and initialize count to 0 if needed """

    # Create the table if it does not exist
    create_count_table_query = """
    CREATE TABLE IF NOT EXISTS yellow_tripdata_total_records (
        count BIGINT DEFAULT 0
    );
    """
    cursor.execute(create_count_table_query)

    # Check if the table is empty (i.e., count rows in the table)
    cursor.execute("SELECT COUNT(*) FROM yellow_tripdata_total_records;")
    existing_row_count = cursor.fetchone()[0]

    # Only insert a row with count=0 if the table is empty
    if existing_row_count == 0:
        cursor.execute("INSERT INTO yellow_tripdata_total_records (count) VALUES (0);")
        print("Table was empty. Initialized the count to 0.")
    else:
        print(f"Table already contains {existing_row_count} row(s). No initialization needed.")

    print("Checked/created yellow_tripdata_total_records table successfully.")


def create_materialized_view_if_not_exists(cursor):
    """ Create the materialized view if it does not exist """
    create_view_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_yellow_tripdata_desc_trip_distance AS
    SELECT
        VendorID,
        pickup_datetime,
        pep_dropoff_datetime,
        trip_distance
    FROM yellow_tripdata
    ORDER BY trip_distance DESC;
    """
    cursor.execute(create_view_query)
    print("Materialized view created or verified successfully.")

def insert_data_from_dataframe(cursor, df):
    """ Insert new trip data into yellow_tripdata """
    insert_query = "INSERT INTO yellow_tripdata (VendorID, pickup_datetime, pep_dropoff_datetime, trip_distance) VALUES (%s, %s, %s, %s);"
    data_tuples = df.values.tolist()
    execute_batch(cursor, insert_query, data_tuples)
    # Update the record count
    cursor.execute(f"UPDATE yellow_tripdata_total_records SET count = count + {len(data_tuples)};")
    print(f"Data from {len(data_tuples)} records inserted successfully & record count updated.")

def validate_data(df):
    # Remove duplicates
    df = df.drop_duplicates(subset=['VendorID', 'tpep_pickup_datetime'])

    # Fill or drop nulls
    df = df.fillna({'trip_distance': 0})  # Default distance to 0 if null
    df = df.dropna(subset=['VendorID'])   # Drop if critical fields are null

    # Check for valid ranges (example for trip_distance)
    df = df[df['trip_distance'] >= 0]
    return df
def refresh_materialized_view(cursor):
    """ Refresh the materialized view to include recent changes """
    cursor.execute("REFRESH MATERIALIZED VIEW mv_yellow_tripdata_desc_trip_distance;")
    print("Materialized view refreshed successfully.")

#python Ingestion.py yellow_tripdata_2024-01.parquet yellow_tripdata_2024-02.parquet yellow_tripdata_2024-03.parquet
def main():
    if len(sys.argv) < 2:
        print("Usage: python Ingestion.py <path_to_parquet_file1> <path_to_parquet_file2> ...")
        return
    # The script directory, which is the parent directory of 'DataSet'
    dataset_dir = os.path.join(os.path.dirname(__file__), 'DataSet')
    file_paths = [os.path.join(dataset_dir, file_name) for file_name in sys.argv[1:]]
    # Run for testing locally
    # file_paths=['./DataSet/yellow_tripdata_2024-01.parquet', './DataSet/yellow_tripdata_2024-02.parquet']
    connection = connect_to_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        create_table_yellow_tripdata(cursor)
        create_record_count_table(cursor)
        create_materialized_view_if_not_exists(cursor)
        for file_name in file_paths:
            df = load_parquet_file(file_name)
            df = validate_data(df)  # Validate data before insertion
            insert_data_from_dataframe(cursor, df)
        refresh_materialized_view(cursor)
    except Exception as error:
        print(f"Error occurred: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed.")

if __name__ == "__main__":
    main()
