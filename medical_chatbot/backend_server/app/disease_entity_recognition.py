from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config_loader import *
import chromadb
from langchain_chroma import Chroma
from pinecone import Pinecone
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

SENTENCE_EMBEDDING_MODEL = system_config["VECTOR_DB_SENTENCE_EMBEDDING_MODEL"]
COLLECTION_NAME = system_config["VECTOR_DB_COLLECTION_NAME"]
PERSIST_DIRECTORY = system_config["VECTOR_DB_COLLECTION_PATH"]
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_HOST = system_config["PINECONE_INDEX_HOST_V2"]
PINECONE_NAME_SPACE = system_config["PINECONE_NAME_SPACE"]
SIMILARITY_THRESHOLDS = system_config["SIMILARITY_THRESHOLDS"]
AMBIGUITY_THRESHOLD = system_config["AMBIGUITY_THRESHOLD"]


embeddings = HuggingFaceEmbeddings(model_name=SENTENCE_EMBEDDING_MODEL)

def vectordb_client_retrival(entities: list, k: int = 1) -> list:
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    client.get_or_create_collection(COLLECTION_NAME)
    vector_store_from_client = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )
    list_entities = []
    for entity in entities:
        results = vector_store_from_client.similarity_search_with_score(query=entity, k=k)
        list_entities.append(results[0][0].page_content)
    # print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
    return list_entities
    # for res, score in results:
    #     print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")


def vectordb_client_retrival_v2(entities: dict, k: int = 1) -> list[dict]:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(host=PINECONE_INDEX_HOST)
    dict_entities = []

    for key, values in entities.items():
        # print(key, values)
        if values:
            list_entities = []
            for value in values:
                results = index.search(
                    namespace=key.lower(),
                    query={
                        "top_k": k,
                        "inputs": {
                            'text': value
                        }
                    }
                )
                print(results)
                list_entities.append(results['result']['hits'][0]['fields']['chunk_text'])

            dict_entities.append({
                "node_type": key,
                "value": list_entities
            })

    print(dict_entities)
    return dict_entities

def vectordb_client_retrival_v3(entities: dict, k: int = 3) -> dict:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(host=PINECONE_INDEX_HOST)
    validated_entities = []
    ambiguous_entities = []
    rejected_entities = []

    for entity_type, entities_values in entities.items():
        # print(key, values)
        if not entities_values:
            continue

        for entity_name in entities_values:
            results = index.search(
                namespace=entity_type.lower(),
                query={
                    "top_k": k,
                    "inputs": {
                        'text': entity_name
                    }
                }
            )
            hits = results['result']['hits']
            top_score = hits[0]['_score']
            top_match = hits[0]['fields']['chunk_text']

            # case 1: nhở hơn ngưỡng
            if top_score < SIMILARITY_THRESHOLDS:
                rejected_entities.append({
                    "original": entity_name,
                    "type": entity_type,
                    "top_match": top_match,
                    "score": top_score,
                    "reason": f"Low confidence (score: {top_score:.3f} < threshold: {SIMILARITY_THRESHOLDS})"
                })
                continue

            # case 2: cao hơn and nhiều kết quả
            if top_score > SIMILARITY_THRESHOLDS and len(hits) >= 2:
                candidates = []
                for hit in hits:
                    if top_score - hit["_score"] < AMBIGUITY_THRESHOLD:
                        candidates.append({
                            "name": hit["fields"]["chunk_text"],
                            "score": hit["_score"]
                        })

                ambiguous_entities.append({
                    "original": entity_name,
                     "type": entity_type,
                     "top_match": candidates,
                     "reason": "Multiple similar matches found",      
                })
                continue

            # case 3:
            validated_entities.append({
                "original": entity_name,
                "matched": top_match,
                "type": entity_type,
                "score": top_score
            })          

    return {
        "validated_entities": validated_entities,
        "ambiguous_entities": ambiguous_entities,
        "rejected_entities": rejected_entities
    }


async def vectordb_client_retrival_v2_async(entities: dict, k: int = 1):
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(host=PINECONE_INDEX_HOST)
    
    async def search_entity(key, values):
        if not values:
            return None
        
        tasks = []
        for value in values:
            task = asyncio.to_thread(
                index.search,
                namespace=key.lower(),
                query={"top_k": k, "inputs": {'text': value}}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        list_entities = [r['result']['hits'][0]['fields']['chunk_text'] for r in results]
        
        return {"node_type": key, "value": list_entities}
    
    tasks = [search_entity(k, v) for k, v in entities.items()]
    dict_entities = await asyncio.gather(*tasks)
    return [e for e in dict_entities if e is not None]
