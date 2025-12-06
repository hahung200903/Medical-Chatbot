from app.core.config_loader import *
import os
import ast
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import requests
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")
DISEASE_ENTITY_EXTRACTION = system_prompt['MULTI_ENTITY_PROMPT']
GENERATION_OUTPUT = system_prompt['KG_RAG_GENERATION_IMPROVED_V3']
CHAT_MODEL_ID = system_config['CHAT_MODEL_ID']
SPOKE_BASE_URL = system_config['SPOKE_BASE_URL']
DATA_SPOKE_TYPES_PATH = system_config['DATA_SPOKE_TYPES_PATH']
SENTENCE_EMBEDDING_MODEL = system_config["VECTOR_DB_SENTENCE_EMBEDDING_MODEL"]

_embedding_model = None

def get_embedding_model():
    """Singleton pattern để tránh load model nhiều lần"""
    global _embedding_model
    if _embedding_model is None:
        # logger.info(f"Loading embedding model: {SENTENCE_EMBEDDING_MODEL}")
        _embedding_model = HuggingFaceEmbeddings(model_name=SENTENCE_EMBEDDING_MODEL)
    return _embedding_model

def get_respone_llm(text:str, prompt: str, conversation_history: list = None):
    llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_ID,
    api_key=GEMINI_API_KEY,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # streaming=True
    )
    messages = [SystemMessage(content=prompt)]

    if conversation_history:
        messages += conversation_history
        
        # for msg in conversation_history:
        #     if msg.type == "human":
        #         messages.append(HumanMessage(content=msg.content))
        #     elif msg.type == "ai":
        #         messages.append(AIMessage(content=msg.content))
    
    messages.append(HumanMessage(content=text))
    ai_msg = llm.invoke(messages)
    # print(ai_msg) -> debug
    return ai_msg

def entities_extraction(query: str):
    try:
        prompt = DISEASE_ENTITY_EXTRACTION
        # prompt_updated = DISEASE_ENTITY_EXTRACTION + "\n" + "Sentence : " + query
        respone = get_respone_llm(query, prompt)
        res_formated = respone.replace('json', '').replace('```', '').strip()
        # print(res_formated) -> debug
        entities = json.loads(res_formated)
        print(entities)
        return entities
    except Exception as e:
        print(f'Error when call api: {e}')
        return {
            "Diseases": [],
            "Compounds": [],
            "Genes": [],
            "Proteins": [],
            "Symptoms": [],
            "SideEffects": []
        }
        
    
def get_spoke_api(value: str, node_type: str, neighborhood: bool = True,  attribute: str = 'name', params = None):
    if neighborhood:
        end_point = f"neighborhood/{node_type}/{attribute}/{value}"
    else:
        end_point = f"node/{node_type}/{attribute}/{value}"
    url = SPOKE_BASE_URL + end_point
    try:
        response = requests.get(url, params=params)
        return response.json()

    except requests.exceptions.HTTPError:
        return {
            "success": False,
            "status_code": response.status_code,
            "error": f"Server returned status {response.status_code}"
        }


def get_context_from_spoke_api(value: str, node_type: str):

    with open(DATA_SPOKE_TYPES_PATH, 'r') as file:
        content = file.read()
        content_json = json.loads(content)

    node_filters = list(content_json["nodes"].keys())
    edge_filters = list(content_json["edges"].keys())

    params = {
        'node_filters' : node_filters,
        'edge_filters': edge_filters,
        'cutoff_Compound_max_phase': system_config['cutoff_Compound_max_phase'],
        'cutoff_Protein_source': system_config['cutoff_Protein_source'],
        'cutoff_DaG_diseases_sources': system_config['cutoff_DaG_diseases_sources'],
        'cutoff_DaG_textmining': system_config['cutoff_DaG_textmining'],
        'cutoff_CtD_phase': system_config['cutoff_CtD_phase'],
        'cutoff_PiP_confidence': system_config['cutoff_PiP_confidence'],
        'cutoff_ACTeG_level': system_config['cutoff_ACTeG_level'],
        'cutoff_DpL_average_prevalence': system_config['cutoff_DpL_average_prevalence'],
        'depth' : system_config['depth']
    }
    results = get_spoke_api(value = value, node_type=node_type, params= params)
    return results


def get_nodes_edges_from_spoke_api(value: str, node_type: str):
    nbr_nodes = []
    nbr_edges = []
    node_context = get_context_from_spoke_api(value, node_type)

    try:
        for item in node_context:
        # parse nodes
            if "_" not in item["data"]["neo4j_type"]:
                try:
                    if item["data"]["neo4j_type"] == "Protein":
                        nbr_nodes.append((item["data"]["neo4j_type"], item["data"]["id"], item["data"]["properties"]["description"]))
                    else:
                        nbr_nodes.append((item["data"]["neo4j_type"], item["data"]["id"], item["data"]["properties"]["name"]))       
                except:
                    nbr_nodes.append((item["data"]["neo4j_type"], item["data"]["id"], item["data"]["properties"]["identifier"]))

        # parse edges
            elif "_" in item["data"]["neo4j_type"]:
                try:
                    # if sources are a list
                    provenance = ", ".join(item["data"]["properties"]["sources"])
                except:
                    # source is str
                    try:
                        provenance = item["data"]["properties"]["source"]
                        if isinstance(provenance, list):
                            provenance = ", ".join(provenance) 
                    except:
                        try:                    
                            preprint_list = ast.literal_eval(item["data"]["properties"]["preprint_list"])
                            if len(preprint_list) > 0:                                                    
                                provenance = ", ".join(preprint_list)
                            else:
                                pmid_list = ast.literal_eval(item["data"]["properties"]["pmid_list"])
                                pmid_list = map(lambda x:"pubmedId:"+x, pmid_list)
                                if len(pmid_list) > 0:
                                    provenance = ", ".join(pmid_list)
                                else:
                                    provenance = "Based on data from Institute For Systems Biology (ISB)"
                        except:                                
                            provenance = "SPOKE-KG"
                try:
                    evidence = item["data"]["properties"]
                except:
                    evidence = None
                nbr_edges.append((item["data"]["source"], item["data"]["neo4j_type"], item["data"]["target"], provenance, evidence))

        return nbr_nodes, nbr_edges, node_context[0]['data']['properties']
    
    except:
        return nbr_nodes, nbr_nodes, node_context 

def graph_to_nature_language(value: str, node_type: str):
    nodes, edges, node_context = get_nodes_edges_from_spoke_api(value, node_type)
    try: 
        df_nodes = pd.DataFrame(nodes, columns=['node_type', 'node_id', 'node_name'])
        df_edges = pd.DataFrame(edges, columns=['source', 'edge_type', 'target', 'provenance', 'evidence'])

        # merge node source
        df_merged_first = pd.merge(df_nodes, df_edges, left_on='node_id', right_on='source', how='right')
        df_merged_first.drop(labels=['node_id', 'source'], inplace=True, axis=1)
        df_merged_first['node_source'] = df_merged_first['node_type'] + ' ' + df_merged_first['node_name']
        new_columns = ['node_source'] + [col for col in df_merged_first.columns if col not in ['node_type', 'node_name', 'node_source']]
        df_merged_first = df_merged_first[new_columns]

        # merge node target
        df_merged_second = pd.merge(df_nodes, df_merged_first, left_on='node_id', right_on='target', how='right')
        df_merged_second.drop(labels=['node_id', 'target'], axis=1, inplace=True)
        df_merged_second['target'] = df_merged_second['node_type'] + ' ' + df_merged_second['node_name']
        df_merged_second.drop(labels=['node_type', 'node_name'], axis=1, inplace=True)
        df_merged_second = df_merged_second[["node_source", "edge_type", "target", "provenance", "evidence"]]

        # create natural language context
        df_merged_second.loc[:, "predicate"] = df_merged_second.edge_type.apply(lambda x:x.split("_")[0])
        df_merged_second.loc[:, "context"] = (
            df_merged_second.node_source + " " + 
            df_merged_second.predicate.str.lower() + " " + 
            df_merged_second.target + 
            " and Provenance of this association is " + 
            df_merged_second.provenance + "."
        )

        # concate context
        context = df_merged_second.context.str.cat(sep=' ')

        try:
            evidence = node_context["source"]
        except:
            evidence = ", ".join(node_context["sources"])

        context += value + " has a " + evidence + " identifier of " + str(node_context["identifier"]) + " and Provenance of this is from " + evidence + "."
        node_context_list = context.split(". ")
        # res = pd.DataFrame(node_context_list, columns=['context'])
        return node_context_list
    except:
        return node_context

def load_sentence_transformers(model_name: str):
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )
    return embeddings

def context_matching(query: str, entities: list[dict]):
    embeding_function = load_sentence_transformers(SENTENCE_EMBEDDING_MODEL)
    query_embedding = embeding_function.embed_query(query)
    max_number_of_high_similarity_context_per_node = int(150/len(entities))
    edge_evidence = False
    context = ''

    for entity in entities:   
        node_context_extracted = ''
        for name in entity['value']:
            list_context = graph_to_nature_language(name, entity['node_type'])
            print(f"List comtext: {list_context}")
            try:
                docs_embedding = embeding_function.embed_documents(list_context)
            except:
                return list_context
            
            context_matched = [
                cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(doc_embedding).reshape(1, -1) 
                )
                for doc_embedding in docs_embedding
            ]
            # đoạn ni chưa hiểu
            similarities = sorted([(e, i) for i, e in enumerate(context_matched)], reverse=True)
            print(f"Similarities: {similarities}")
            percentile_threshold = np.percentile([s[0] for s in similarities], 75)
            high_similarity_indices = [s[1] for s in similarities if s[0] > percentile_threshold and s[0] > 0.5]
            if len(high_similarity_indices) > max_number_of_high_similarity_context_per_node:
                high_similarity_indices = high_similarity_indices[:max_number_of_high_similarity_context_per_node]
            high_similarity_context = [list_context[index] for index in high_similarity_indices]            
            if edge_evidence:
                high_similarity_context = list(map(lambda x:x+'.', high_similarity_context)) 
                context_table = context_table[context_table.context.isin(high_similarity_context)]
                context_table.loc[:, "context"] =  context_table.source + " " + context_table.predicate.str.lower() + " " + context_table.target + " and Provenance of this association is " + context_table.provenance + " and attributes associated with this association is in the following JSON format:\n " + context_table.evidence.astype('str') + "\n\n"                
                node_context_extracted += context_table.context.str.cat(sep=' ')
            else:
                node_context_extracted += ". ".join(high_similarity_context)
                node_context_extracted += ". "


        context += node_context_extracted
    return context
def context_matching_v2(
    query: str, 
    entities: list[dict[str, any]], 
    max_contexts_per_entity: int = 50,
    similarity_threshold: float = 0.65,
    use_adaptive_threshold: bool = True,
    deduplicate: bool = True
) -> str:
    
    if not entities:
        # logger.warning("No entities provided for context matching")
        return ""
    
    embedding_model = get_embedding_model()
    
    try:
        query_embedding = embedding_model.embed_query(query)
    except Exception as e:
        # logger.error(f"Error embedding query: {e}")
        return ""
    
    all_contexts = []
    entity_context_map = {}  # Track which context belongs to which entity
    
    # Step 1: Retrieve contexts for all entities
    for entity_dict in entities:
        node_type = entity_dict.get('node_type')
        entity_values = entity_dict.get('value', [])
        
        if not entity_values:
            continue
        
        for entity_name in entity_values:
            # logger.info(f"Processing entity: {entity_name} (type: {node_type})")
            
            # Get context from SPOKE
            context_list = graph_to_nature_language(entity_name, node_type)
            
            if not context_list:
                # logger.warning(f"No context found for {entity_name}")
                continue
            
            # Filter empty strings
            context_list = [ctx.strip() for ctx in context_list if ctx.strip()]
            
            if not context_list:
                continue
            
            try:
                # Embed all contexts
                docs_embeddings = embedding_model.embed_documents(context_list)
            except Exception as e:
                # logger.error(f"Error embedding documents for {entity_name}: {e}")
                continue
            
            # Calculate similarities
            similarities = []
            for idx, doc_embedding in enumerate(docs_embeddings):
                sim_score = cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(doc_embedding).reshape(1, -1)
                )[0][0]
                
                similarities.append({
                    'context': context_list[idx],
                    'score': sim_score,
                    'entity': entity_name,
                    'entity_type': node_type
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['score'], reverse=True)
            
            # Adaptive threshold
            if use_adaptive_threshold and len(similarities) > 0:
                # Lấy top scores
                top_scores = [s['score'] for s in similarities[:10]]
                if top_scores:
                    # Dynamic threshold: mean of top 10 - 0.1
                    adaptive_threshold = max(
                        np.mean(top_scores) - 0.15, 
                        similarity_threshold
                    )
                else:
                    adaptive_threshold = similarity_threshold
            else:
                adaptive_threshold = similarity_threshold
            
            # Filter by threshold
            high_similarity_contexts = [
                s for s in similarities 
                if s['score'] >= adaptive_threshold
            ]
            
            # Limit number
            high_similarity_contexts = high_similarity_contexts[:max_contexts_per_entity]
            
            # logger.info(
            #     f"Entity '{entity_name}': {len(high_similarity_contexts)} contexts selected "
            #     f"(threshold: {adaptive_threshold:.3f})"
            # )
            
            all_contexts.extend(high_similarity_contexts)
            entity_context_map[entity_name] = high_similarity_contexts
    
    if not all_contexts:
        # logger.warning("No relevant contexts found for any entity")
        return ""
    
    # Step 2: Deduplicate (nếu bật)
    if deduplicate:
        seen_contexts = set()
        unique_contexts = []
        
        for ctx_obj in all_contexts:
            # Normalize context để so sánh
            normalized = ctx_obj['context'].lower().strip()
            
            if normalized not in seen_contexts:
                seen_contexts.add(normalized)
                unique_contexts.append(ctx_obj)
        
        # logger.info(f"Deduplication: {len(all_contexts)} -> {len(unique_contexts)} contexts")
        all_contexts = unique_contexts
    
    # Step 3: Re-rank và prioritize
    # Ưu tiên contexts có score cao và từ entity quan trọng
    all_contexts.sort(key=lambda x: x['score'], reverse=True)
    
    # Step 4: Build final context string
    final_context_parts = []
    
    for ctx_obj in all_contexts:
        # Format: "Context about {entity}: {content}"
        formatted = f"{ctx_obj['context']}"
        final_context_parts.append(formatted)
    
    final_context = " ".join(final_context_parts)
    
    # logger.info(f"Final context length: {len(final_context)} characters")
    
    return final_context


def get_generated_output(context: str, question: str):
    if isinstance(context, dict):
        return 'Lỗi từ API SPOKE'
    
    enriched_prompt = "Context: "+ context + "\n" + "Question: "+ question
    result = get_respone_llm(enriched_prompt, GENERATION_OUTPUT)
    return result.content

# def get_generated_output_stream(context: str, question: str):
#     enriched_prompt = "Context: "+ context + "\n" + "Question: "+ question
    
#     llm = ChatGoogleGenerativeAI(
#         model=CHAT_MODEL_ID,
#         api_key=GEMINI_API_KEY,
#         temperature=0,
#         streaming=True 
#     )
    
#     messages = [
#         SystemMessage(content=GENERATION_OUTPUT),
#         HumanMessage(content=enriched_prompt),
#     ]
    
#     for chunk in llm.stream(messages):
#         yield chunk.content
