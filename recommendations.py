import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Cassandra
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from models import Product
from connection import SessionLocal
import cassio
import numpy as np

load_dotenv()
# Set your OpenAI API key

openai.api_key = os.getenv("OPENAI_API_KEY")
AstraDB_application_token = os.getenv("AstraDB_application_token")
AstraDB_database_id = os.getenv("AstraDB_database_id")

# Initialize the OpenAI Embeddings and Cassandra vector store
embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize Cassio with your AstraDB credentials
AstraDB_application_token = "AstraCS:ccPsQsnDUQupcOQwMqRgzpNn:be3d4d5ba01b912e320bab98b3cbc684be5f316cfc9371443ee00214394aba02"
AstraDB_database_id = "9638aff6-6223-4af8-86c6-d7d841e924e7"

cassio.init(token=AstraDB_application_token, database_id=AstraDB_database_id)

# Assuming Cassandra is correctly set up to handle vectors
vectorstore = Cassandra(
    embedding=embeddings,
    table_name="product_list_embeddings",
    session=None,
    keyspace=None,
)


def store_product_embeddings(db: Session):
    products = db.query(Product).all()
    product_titles = [product.title for product in products]
    # Add product title and its embedding to the vectorstore
    vectorstore.add_texts(
        texts=product_titles,
    )
    return "Data Inserted Successfully"


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def recommend_similar_products(product_title, db: Session):
    # Embed the product title to get the embedding vector
    product_embedding = embeddings.embed_query(product_title)

    # Perform a similarity search in Cassandra using the embedding vector
    recommended_products = vectorstore.similarity_search_by_vector(
        product_embedding, k=5
    )

    products = []

    for product in recommended_products:
        product_list_embedding = embeddings.embed_query(product.page_content)
        similarity_score = cosine_similarity(product_embedding, product_list_embedding)
        if similarity_score > 0.80:
            products.append(product.page_content)

    products = [product for product in products if product != product_title]

    # Return the similar products found
    product_details = db.query(Product).filter(Product.title.in_(products)).all()

    return product_details
