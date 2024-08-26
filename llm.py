import os
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from chromadb import Client
from chromadb.config import Settings
from langchain import OpenAI
from langchain.vectorstores import Chroma

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = (
    "sk-proj-qEUSKwAITYypRO1vWnjBT3BlbkFJHw4z44m3rNBGu8U1KUGG"
)

# Load documents from URLs
loader = UnstructuredURLLoader(
    urls=[
        "https://www.moneycontrol.com/technology/google-to-slash-maps-platform-pricing-for-indian-developers-by-up-to-70-from-august-1-article-12771471.html#goog_rewarded",
        "https://www.moneycontrol.com/technology/karnataka-deputy-cm-dk-shivakumar-takes-test-drive-on-bengalurus-1st-double-decker-flyover-article-12771475.html",
    ]
)
data = loader.load()

# Split documents into chunks
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=200,
)
docs = splitter.split_documents(data)

# Initialize Chroma client and settings
client = Client(Settings(persist_directory="/content/sample_data/chroma_data1"))

# Create or get Chroma collection
collection_name = "documents"
collection = client.create_collection(name=collection_name)

# Create OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Add documents to Chroma collection
# Note: We should use `Chroma` to handle document addition
vector_store = Chroma(
    persist_directory="/Users/rakshithds/Desktop/ReactJS/material-ui-project-backend/chroma_data",
    embedding_function=embeddings,
)

# Add documents to the vector store
vector_store.add_documents(docs)

# Persist the collection
vector_store.persist()

# Initialize OpenAI LLM
llm = OpenAI(temperature=0.9, max_tokens=500)

# Create a retrieval-based QA chain with sources
chain = RetrievalQAWithSourcesChain.from_llm(
    llm=llm, retriever=vector_store.as_retriever()
)

# Define the query
query = "who is Karnataka Deputy CM"

# Run the query
result = chain({"question": query})

# Print the result
print(result["answer"])
