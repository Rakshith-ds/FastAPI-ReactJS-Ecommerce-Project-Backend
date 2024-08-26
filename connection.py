import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import pymysql


def database_connection():
    dbDetails = {
        "username": "root",
        "password": "Rakshithds1",
        "host": "localhost",  # Use 127.0.0.1 instead of localhost
        "port": "3306",
        "dbname": "test",
    }

    try:
        engine = sq.create_engine(
            "mysql+pymysql://{user}:{password}@{ip}:{port}/{dbname}".format(
                user=dbDetails["username"],
                password=dbDetails["password"],
                ip=dbDetails["host"],
                port=dbDetails["port"],
                dbname=dbDetails["dbname"],
            )
        )
        return engine
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        raise


# Initialize the database connection
try:
    engine = database_connection()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("Database connection established successfully")
except OperationalError:
    print("Failed to establish a database connection")
    engine = None
    SessionLocal = None
