import pandas as pd
import math
from db_utils import connect_to_db  # Importing the common database connection function

def extract_top_percentile_to_csv(cursor):
    """ Extract top 10% of the records from the materialized view and save to CSV """
    cursor.execute("SELECT count FROM yellow_tripdata_total_records;")
    total_count = cursor.fetchone()[0]
    limit = math.ceil(total_count * 0.1)
    cursor.execute(f"SELECT * FROM mv_yellow_tripdata_desc_trip_distance LIMIT {limit};")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['VendorID', 'pickup_datetime', 'pep_dropoff_datetime', 'trip_distance'])
    df.to_csv('top_10_percentile_trips.csv', index=False)
    print("Data exported to CSV successfully.")

def main():
    connection = connect_to_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        extract_top_percentile_to_csv(cursor)
    except Exception as error:
        print(f"Error occurred: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed.")

if __name__ == "__main__":
    main()
