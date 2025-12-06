from app.agent.state import AgentState
from app.core.config_loader import *
from app.untils import get_respone_llm
import json
from langgraph.types import Command
from typing import Literal
from app.disease_entity_recognition import vectordb_client_retrival_v3
from app.untils import get_generated_output
from langgraph.graph import END
from langchain.messages import AIMessage, HumanMessage, SystemMessage

INTENT_PROMPT = system_prompt['CLASSIFICATION_PROMPT_V2']
CLARIFY_PROMPT = system_prompt['CLARIFY_PROMPT']
CHITCHAT_PROMPT = system_prompt['CHITCHAT_PROMPT']
ORCHESTRATOR_PROMPT = system_prompt['ORCHESTRATOR_PROMPT']
ENTITY_RESOLUTION_PROMPT = system_prompt['ENTITY_RESOLUTION_PROMPT']
CONTEXT_QUALITY_PROMPT = system_prompt['CONTEXT_QUALITY_PROMPT']
CONTEXT_QUALITY_THRESHOLDS = system_config['CONTEXT_QUALITY_THRESHOLDS']
HUMAN_FEEDBACK_MESSAGE_GENERATION = system_prompt["HUMAN_FEEDBACK_MESSAGE_GENERATION"]


def agent_orchestrator_node(state: AgentState) -> Command[Literal['chitchat', 'entity_resolver']]:
    user_input = state['user_input']
    history = state.get('conversation_history', [])
    print(f"User input: {user_input}")
    print(f"History: {history}")

    safe_history = [
        {"role": msg.type, "content": msg.content}
        for msg in history[-3:]
    ]

    prompt = ORCHESTRATOR_PROMPT.format(
        user_input=user_input,
        history=json.dumps(safe_history, ensure_ascii=False)
    )
    response = get_respone_llm(user_input, prompt, history)
    content_response = response.content
    analysis = json.loads(content_response.replace('```json', '').replace('```', '').strip())
    # print(f"agent_orchestrator_node : {analysis}")

    if analysis["next_action"] == "chitchat":
        goto="chitchat"
        print("Going to the chichat node...")
    elif analysis["next_action"] == "biomedical_query":
        goto="entity_resolver"
        print("Going to the entity_resolver node...")

    return Command(
        goto=goto,
        update= {
            "intent": analysis["intent"],
            "next_action": analysis["next_action"],
            "confidence_score": analysis["confidence"],
            "entities_mentioned": analysis.get("entities_mentioned"),
            "cache_hit": False,
            "metadata": {"reasoning": analysis.get("reasoning")},
            "conversation_history": [HumanMessage(content=user_input)]
        }
    )
        

def entity_resolver_node(state: AgentState) -> Command[Literal['kg_retrieval', 'human_feedback']]:
    print("Arrived at the entity_resolver_node...")
    entities = state.get('entities_mentioned', {})
    query = state['user_input']
    print(f"User input: {query}")

    if not entities or not any(entities.values()):
        print(f"Need clarification? : {True}")
        print("Going to the human_feedback node because empty entities...")
        return Command(
            goto="human_feedback",
            update={
                "entity_confidence": 0.0,
                "needs_clarification": True,
                "clarification_options": [{
                    "type": "unclear_query",
                    "message": "Can you be more specific about what disease, medication, or gene you are asking about?"
                }]
            }
        )
    
    vector_results = vectordb_client_retrival_v3(entities, k=5)
    prompt = ENTITY_RESOLUTION_PROMPT.format(
        entities=json.dumps(entities, ensure_ascii=False),
        query=query,
        vector_results=json.dumps(vector_results, ensure_ascii=False, indent=2)
    )
    
    response = get_respone_llm(query, prompt)
    content_response = response.content
    resolution = json.loads(content_response.replace('```json', '').replace('```', '').strip())
    print(resolution)

    needs_clarification = resolution["needs_clarification"]
    clarification_options = []
    print(f"Need clarification? : {needs_clarification}")


    if needs_clarification:
        for amb in resolution.get('ambiguous', []):
            clarification_options.append({
                "type": "ambiguous_entity",
                "entity_type": amb["type"],
                "candidates": amb["candidates"],
                "reason": amb["reason"],
                "message": f"Which entity are you asking about?\n" + 
                          "\n".join([f"{i+1}. {c}" for i, c in enumerate(amb["candidates"])])
            })

        for unres in resolution.get('unresolved', []):
            clarification_options.append({
                "type": "unresolved_entity",
                "entity_type": unres["type"],
                "reason": unres["reason"],
                "message": f"'{unres['original']}' not found in database. Can you be more specific?"
            })

    if needs_clarification:
        goto="human_feedback"
        print("Going to the human_feedback node bacause there are many similar entities...")
    else:
        goto="kg_retrieval"
        print("Going to the kg_retrieval node because the entity name has been accurately identified...")

    return Command(
        goto=goto,
        update={
            "resolved_entities": resolution["resolved"],
            "entity_confidence": resolution["overall_confidence"],
            "needs_clarification": needs_clarification,
            "clarification_options": clarification_options,
            "metadata": {
                "ambiguous_count": len(resolution.get("ambiguous", [])),
                "unresolved_count": len(resolution.get("unresolved", []))
            }
        }
    )


def kg_retrieval_node(state: AgentState) -> Command[Literal['response_generator', 'human_feedback']]:
    from app.untils import context_matching_v2

    print("Arrived at the kg_retrieval_node...")
    resolved_entities = state.get("resolved_entities", [])
    print(f"[DEBUG] resolved_entities: {resolved_entities}")
    query = state['user_input']

    if not resolved_entities:
        print("empty resolved_entities...")
        return Command(
            goto="human_feedback",
            update={
                "kg_context": "",
                "context_quality": 0.0,
                "needs_clarification": True
            }
        )
    
    entities_dict = {}
    for ent in resolved_entities:
        ent_type = ent["type"]
        ent_value = ent["matched"]

        if ent_type not in entities_dict:
            entities_dict[ent_type] = []

        entities_dict[ent_type].append(ent_value)

    result = [
        {"node_type": k, "value": v}
        for k, v in entities_dict.items()
    ]

    print(f"[DEBUG] Entities for SPOKE: {result}")
    context = context_matching_v2(query, result)
    print(f"[DEBUG] Context retrieved: {context}")

    prompt = CONTEXT_QUALITY_PROMPT.format(
        question = query,
        context = context
    )
    response = get_respone_llm(query, prompt)
    content_response = response.content
    quality_eval = json.loads(content_response.replace('```json', '').replace('```', '').strip())
    print(f"[DEBUG] Context quality: {quality_eval}")

    if quality_eval['quality_score'] >= CONTEXT_QUALITY_THRESHOLDS:
        goto="response_generator"
    else:
        goto="human_feedback"

    return Command(
        goto=goto,
        update={
            "context_quality": quality_eval['quality_score'],
            "kg_context": context,
            "clarification_options": [], # nếu đến đây rồi thì không cần làm rõ nữa nên set trường ni là rỗng
            "metadata": {
                "is_sufficient": quality_eval["is_sufficient"],
                "missing_aspects": quality_eval.get("missing_aspects", []),
                "available_info": quality_eval.get("available_info", [])
            }
        }
    )

def response_generator_node(state: AgentState) -> dict:
    context = state['kg_context']
    query = state['user_input']
    context_quality = state.get("context_quality", 1.0)
    metadata = state.get("metadata", {})

    response = get_generated_output(context, query)

    if context_quality < 0.8:
        response += "\n\nNote: Information may be incomplete. "
        if metadata.get("missing_aspects"):
            response += f"Missing aspects: {', '.join(metadata['missing_aspects'])}. "
        response += "You can ask for more detailed information."

    return {
        "final_response": response,
        "metadata": {
            **metadata,
            "context_quality": context_quality,
        },
        "conversation_history": [
           AIMessage(content=response)
        ]
    }

def chitchat_node(state: AgentState) -> dict:
    print("Arrived at the chitchat node...")
    user_input = state["user_input"]
    conversation_history = state.get("conversation_history", [])
    metadata = state.get("metadata", {})
    print(f"User input: {user_input}")
    print(f"History: {conversation_history}")

    response = get_respone_llm(user_input, CHITCHAT_PROMPT, conversation_history)
    content_response = response.content
    final_response = content_response.replace('json', '').replace('```', '').strip()
    print(f"chitchat_node : {final_response}")

    return {
        "final_response": final_response,
        "metadata": {
            **metadata,
            "type": "chitchat"
        },
        "conversation_history": [response]
    }

def human_feedback_node(state: AgentState) -> dict:
    print("Arrived at the human_feedback_node...")
    user_input = state["user_input"]
    clarification_options = state.get("clarification_options", [])
    context_quality = state.get("context_quality", 0.0)
    metadata = state.get("metadata", {})

    prompt = HUMAN_FEEDBACK_MESSAGE_GENERATION.format(
        clarification_options = json.dumps(clarification_options, ensure_ascii=False, indent=2),
        context_quality = context_quality,
        threshold = CONTEXT_QUALITY_THRESHOLDS,
        metadata = metadata
    )
    try:
        response = get_respone_llm(user_input, prompt)
        message = response.content.strip()

    except:

        if clarification_options:
            print("Want to clarify the question...")
            message = "I need you to help clarify some information:\n"
            for idx, option in enumerate(clarification_options):
                if option["type"] == "ambiguous_entity":
                    message += f"**{idx}. {option['message']}**\n"
                elif option["type"] == "unresolved_entity":
                    message += f"**{idx}. {option['message']}**\n"
                elif option["type"] == "unclear_query":
                    message += f"**{option['message']}**\n"

        elif context_quality < CONTEXT_QUALITY_THRESHOLDS:   
            print("Want to ask more about the context...")
            metadata = state.get("metadata", {})
            message = "I have found some information, but it may not be enough to answer your question.\n"

            if metadata.get("available_info"):
                message += "**Available information:**\n"
                for info in metadata["available_info"]:
                    message += f"- {info}\n"
                message += "\n"

            if metadata.get("missing_aspects"):
                message += "**Missing information:**\n"
                for aspect in metadata["missing_aspects"]:
                    message += f"- {aspect}\n"
                message += "\n"    

            message += "Do you want me to continue answering based on the existing data, help you ask more specific questions, or expand the search to other sources?"

        else:
            message = "I need more information to answer your question accurately. Can you describe it in more detail?"


    return {
        "final_response": message,
        "needs_clarification": True,
        "metadata": {
            "waiting_for_feedback": True,
            "clarification_options": clarification_options
        },
        "conversation_history": [
            AIMessage(content=message)
        ]
    }

def route_after_human_feedback(state: AgentState) -> Command[Literal["entity_resolver", "kg_retrieval", "orchestrator"]]:
    feedback_type = state.get("feedback_type")
    user_feedback = state.get("user_feedback")

    print(f"[DEBUG] Route feedback_type: {feedback_type}")
    print(f"[DEBUG] User feedback: {user_feedback}")
    # needs_clarification = state.get("needs_clarification")
    # cập nhật history 
    
    if feedback_type == "entity_clarified":
        goto = "kg_retrieval"
    elif feedback_type == "change_question":
        goto = "orchestrator"
    elif feedback_type == "un_clarified":
        goto = "entity_resolver"
    else:
        goto = "orchestrator"

    print(f"[DEBUG] Routing to: {goto}")

    return Command(
        goto=goto,
        update = {
            "needs_clarification": False,
            "user_input": user_feedback if user_feedback else state.get("user_input")
        }
    )

