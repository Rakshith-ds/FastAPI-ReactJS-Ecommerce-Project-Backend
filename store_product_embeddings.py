import openai
import numpy as np
from cassandra.cluster import Cluster
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Cassandra

# Set your OpenAI API key
AstraDB_application_token = "AstraCS:ccPsQsnDUQupcOQwMqRgzpNn:be3d4d5ba01b912e320bab98b3cbc684be5f316cfc9371443ee00214394aba02"
AstraDB_database_id = "9638aff6-6223-4af8-86c6-d7d841e924e7"
openAi_key = "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"

# Initialize the OpenAI Embeddings and Cassandra vector store
embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
vectorstore = Cassandra(embedding=embeddings, table_name="product_embeddings")


def store_product_embeddings(products):
    for product in products:
        embedding = embeddings.embed_query(product["title"])
        vectorstore.add_texts(
            texts=[product["title"]], embeddings=[embedding], ids=[product["id"]]
        )


store_product_embeddings(products)
