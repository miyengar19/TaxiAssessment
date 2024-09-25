import psycopg2

# Database connection configuration
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "bbbb"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_to_db():
    """ Establish a connection to the PostgreSQL database """
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        connection.autocommit = True
        return connection
    except Exception as error:
        print(f"Error connecting to database: {error}")
        return None
