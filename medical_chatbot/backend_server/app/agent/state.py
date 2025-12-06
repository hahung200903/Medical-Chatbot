from typing import TypedDict, Literal, Optional, List, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    # input
    user_input: str
    conversation_history: Annotated[list, add_messages]

    # điều phối
    intent: Literal["biomedical" , "chitchat" , "unclear" ]
    next_action: Literal["biomedical_query", "chitchat", "answer_ready"]
    confidence_score: Optional[float] 

    # thực thể
    entities_mentioned: Optional[dict]
    resolved_entities: Optional[list]
    entity_confidence: Optional[float]
    needs_clarification: bool
    clarification_options: Optional[list]
    
    # KG
    kg_context: Optional[str]
    context_quality: Optional[float]

    # Human
    feedback_type: Literal["entity_clarified" , "change_question" , "un_clarified"]
    user_feedback: Optional[str]

    # Cache
    cache_key: Optional[str]
    cache_hit: bool

    # respone
    final_response: str
    metadata: Optional[dict]

