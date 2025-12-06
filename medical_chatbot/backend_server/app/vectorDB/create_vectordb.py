from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config_loader import *
from langchain_core.documents import Document
from uuid import uuid4
import pandas as pd
import os
from dotenv import load_dotenv
from pinecone import Pinecone
import itertools

load_dotenv()

SENTENCE_EMBEDDING_MODEL = system_config["VECTOR_DB_SENTENCE_EMBEDDING_MODEL"]
COLLECTION_NAME = system_config["VECTOR_DB_COLLECTION_NAME"]
PERSIST_DIRECTORY = system_config["VECTOR_DB_COLLECTION_PATH"]
DOCUMENT_DATA_PATH = system_config['DOCUMENT_DATA_PATH']
DOCUMENT_DATA_TEST_PATH = system_config['DOCUMENT_DATA_TEST_PATH']
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")


embeddings = HuggingFaceEmbeddings(model_name=SENTENCE_EMBEDDING_MODEL)

def get_documents(path: str):
    df = pd.read_csv(path, encoding='utf-8')
    documents = []
    for index, row in df.iterrows():
        disease_name = row['disease_name']
        disease_id = row['disease_id']
        documents.append(
            Document(
                page_content=disease_name, 
                metadata={'source': disease_id}, 
                id=index 
            )
        )
    return documents
 

# local
def vectordb_create():
    vector_store = Chroma(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY
    )
    documents = get_documents(DOCUMENT_DATA_TEST_PATH)
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids = uuids)

# chroma server
def vectordb_cloud_create():
    vector_store = Chroma(
        collection_name="ake",
        embedding_function=embeddings,
        chroma_cloud_api_key=os.getenv("CHROMA_API_KEY"),
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE"),
    )
    documents = get_documents(DOCUMENT_DATA_PATH)[:300]
    uuids = [str(uuid4()) for _ in range(len(documents))]
    batch_size = 1000
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i: i + batch_size]
        batch_ids = uuids[i: i + batch_size]
        vector_store.add_documents(documents=batch_docs, ids = batch_ids)  
        print(f"Added batch {i//batch_size + 1} ({len(batch_docs)} docs)")

def chunks(iterable, batch_size=96):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = list(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = list(itertools.islice(it, batch_size))

def get_records(path: str, type: str):
    df = pd.read_csv(path, encoding='utf-8')
    records = []
    for index, row in df.iterrows():
        if type == row["type"]:
            disease_name = row['disease_name']
            disease_id = row['disease_id']
            records.append(
                {
                    "_id": str(index),
                    "chunk_text": disease_name,
                    "source": disease_id
                }
            )
    return records 

# pinecone cloud
def vectordb_cloud_create_v2():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    types = ["Disease", "Symptom", "Compound", "SideEffect", "Gene", "Protein"]
    index_name = "ake-v2" 

    if pc.has_index(index_name):
        pc.delete_index(index_name)

    pc.create_index_for_model(
        name = index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"multilingual-e5-large",
            "field_map":{"text":"chunk_text"}
        }
    )

    index = pc.Index(index_name)
    for type in types:
        records = get_records(DOCUMENT_DATA_TEST_PATH, type)
        for batch in chunks(records):
            index.upsert_records(type.lower(), batch)
        print(f'Created space {type}')

def vectordb_cloud_create_v3():
    pass