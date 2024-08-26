import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Product
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Path to your JSON file
json_file_path = "/Users/rakshithds/Desktop/ReactJS/FastAPI-ReactJS-Ecommerce-Project/FastAPI-ReactJS-Ecommerce-Project-Backend/medical_data.json"

# Read JSON file into DataFrame
data = pd.read_json(json_file_path)
data = pd.DataFrame(data)
# data.drop(["creationAt", "updatedAt"], axis=1, inplace=True)
print(len(data))

# Database configuration
dbDetails = {
    "username": "root",
    "password": "Rakshithds1",
    "host": "localhost",
    "port": "3306",
    "dbname": "test",
}

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{dbDetails['username']}:{dbDetails['password']}@{dbDetails['host']}:{dbDetails['port']}/{dbDetails['dbname']}"
)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Function to append DataFrame into SQL
def append_to_existing_table(data):
    j = 0
    # Create a new database session
    db = SessionLocal()
    try:
        # Iterate over DataFrame rows
        for _, row in data.iterrows():
            # Extract values from DataFrame
            new_product = Product(
                id=row["id"],
                title=row["title"],
                price=row["price"],
                name=row["name"],
                description=row.get(
                    "description", ""
                ),  # Use empty string if description is missing
                image_url=(
                    row["images"][0]
                    if isinstance(row["images"], list)
                    else row["images"]
                ),
            )
            db.add(new_product)
            print(new_product)

        db.commit()
        return {"message": "Data inserted successfully"}
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of error
        return {"error": str(e)}
    finally:
        db.close()  # Close the session


# Example usage
result = append_to_existing_table(data)
