# Taxi Assessment

Taxi Assessment is a Python program. Data is available for the first six months of 2024 (January to June).

## Table of Contents
1. [Scope](#Scope-Based-on-Requirements)
2. [Approach](#approach)
   - [Ingestion](#ingestion)
   - [Retrieval](#retrieval)
   - [Validation](#validation)
3. [Program Execution](#program-execution)
4. [Results with Reconciliation](#results-with-reconciliation)
5. [Additional Scalable Considerations for Real-Time Application](#additional-scalable-considerations-for-real-time-application)



## Scope Based on Requirements

- **Point 1**: 2024 data, as available from NYC data, is used.
  - Client Response: Ideally, the query would run over all historical data without filtering by dates or using filters for the whole year.

- **Point 2**: A Python pandas and Postgres-based solution is provided. Python notebooks are scoped out.
  - Client Response: You can use pandas and Postgres. The reason we avoid Python notebooks is that they are more suited for computer scientists, and we need someone with programming skills. However, you can send the `.py` file.

- **Point 3**: Data quality issues are handled (refer to the Validation section in the Approach).

- **Point 4**: Reporting fields captured: `VendorID`, `pickup_datetime`, `pep_dropoff_datetime`, and `trip_distance`. No other filters besides filtering by the 90th percentile of trip distance. These are captured in the file `top_10_percentile_trips.csv`.
  - Client Response: Totally okay with this. You can output the results in a file.

## Approach

### Ingestion

| SR  | Feature                                  | Summary                                                                                                                                                       |
| --- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Materialized View for Performance        | A materialized view is created to store data ordered by `trip_distance` to optimize query performance.                                                         |
| 2   | Incremental Load Handling                | Tracks and updates the total record count incrementally with each data insertion.                                                                              |
| 3   | Avoid Recomputing Count                  | The total record count is stored and updated, eliminating the need to recompute it each time.                                                                  |
| 4   | Handles Full and Incremental Loads       | Supports both full and incremental data loads while maintaining data integrity.                                                                                |
| 5   | Dynamic File Handling                    | Automatically processes Parquet files located in the `DataSet` directory, specified via command-line arguments.                                                |


### Retrieval
- **Fetching Total Record Count**: The script retrieves the total number of records from the `yellow_tripdata_total_records` table.
- **Top 10% Trips Calculation**: Using the total count, the program computes the top 10% based on `trip_distance`.
- **Data Export**: The top 10% of trips are exported to a CSV file (`top_10_percentile_trips.csv`).

### Validation
1. **Duplicate Removal**: Duplicate trips based on `VendorID` and `tpep_pickup_datetime` are removed.
2. **Handling Null Values**: Null values in `trip_distance` are set to 0, and records missing `VendorID` are dropped.
3. **Range Validation**: The program ensures that `trip_distance` is non-negative.

## Program Execution

### Downloads

1. Ensure that Python 3.12.1 is installed. You can download it from the Python official website. Verify the installation:
   ```bash
   python3 --version
   ```

2. Download and install Postgres.

### Cloning the Repository

- **HTTP**:
   ```bash
   git clone https://github.com/miyengar19/TaxiAssessment.git
   cd TaxiAssessment
   ```

- **SSH**:
   ```bash
   git clone git@github.com:miyengar19/TaxiAssessment.git
   cd TaxiAssessment
   ```

### Install Dependencies

Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

### Execution of Ingestion Script

Run the program with predefined arguments for quicker execution:
```bash
python Ingestion.py yellow_tripdata_2024-01.parquet yellow_tripdata_2024-02.parquet yellow_tripdata_2024-03.parquet yellow_tripdata_2024-04.parquet yellow_tripdata_2024-05.parquet yellow_tripdata_2024-06.parquet
```

### Execution of Retrieval Script

To retrieve the top 10% for fields in scope:
```bash
python Retrieval.py
```

### Results with Reconciliation

The following are the tables used during the program execution:

| SR | Table Name                          | Count    | Query                                         | Description                                                                             |
|----|-------------------------------------|----------|-----------------------------------------------|-----------------------------------------------------------------------------------------|
| 1  | `yellow_tripdata`                   | 12,716,897 | `SELECT count(*) FROM yellow_tripdata;`         | Base table holding all trip data after the insertion of 6 months of 2024 data.           |
| 2  | `yellow_tripdata_total_records`     | 12,716,897 | `SELECT * FROM yellow_tripdata_total_records;` | Tracks the count of records to avoid recounting, useful for incremental loads.           |
| 3  | `mv_yellow_tripdata_desc_trip_distance` | 12,716,897 | `SELECT count(*) FROM mv_yellow_tripdata_desc_trip_distance;` | Materialized view intended to avoid recomputation, ordered by trip distance.            |
| 4  | `top_10_percentile_trips.csv`       | 1,271,690 | N/A (CSV file)                                | Holds the top 10% of the data in CSV format excluding the header.                        |

Refer to: `postgresResultsReconciliationScript.sql` for more information on the reconciliation process.

## Additional Scalable Considerations for Real-Time Application

1. **System Architecture and Design**  
   - **Event-driven Design**: Expand the system to an event-driven architecture where file ingestion is automatically triggered upon file arrival in the ingestion folder for real-time data ingestion.

2. **Data Processing and Optimization**  
   - **Indexing**: Apply indexing on the materialized views and/or base tables for faster query performance based on data processing and scanning needs.

3. **Reliability and Consistency**  
   - **Idempotency**: Ensure that processing the same message/event multiple times results in the same output, preventing duplicates during replay or retry scenarios.

4. **Performance Monitoring and Alerts**  
   - **Latency Checks**: Measure and validate processing latency. Set up alerts if processing time exceeds defined thresholds to maintain real-time system performance.

5. **Data Quality Validation**  
   - **Completeness**: Ensure that all necessary fields and data are present in the incoming dataset.
   - **Anomaly Detection**: Implement checks to detect outliers or unusual patterns in the data.
   - **Data Volume Validation**: Monitor the data volume being processed, raising alerts if the volume is unexpectedly high or low, indicating potential data loss or overload.

6. **Security**  
   - **Access Control**: Ensure that data pipelines have proper access controls to protect data integrity and prevent unauthorized access.
   - **Data Encryption**: Implement encryption for sensitive data in transit and at rest to ensure privacy and compliance with industry standards.


