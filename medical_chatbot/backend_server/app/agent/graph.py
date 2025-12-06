from langgraph.graph import START, END, StateGraph
from app.agent.state import AgentState
from app.agent.nodes import (
    agent_orchestrator_node, 
    chitchat_node, 
    entity_resolver_node, 
    kg_retrieval_node, 
    human_feedback_node, 
    response_generator_node, 
    route_after_human_feedback
)

from langgraph.checkpoint.memory import MemorySaver

workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", agent_orchestrator_node)
workflow.add_node("chitchat", chitchat_node)
workflow.add_node("entity_resolver", entity_resolver_node)
workflow.add_node("kg_retrieval", kg_retrieval_node)
workflow.add_node("human_feedback", human_feedback_node)
workflow.add_node("process_feedback", route_after_human_feedback)
workflow.add_node("response_generator", response_generator_node)

workflow.add_edge(START, "orchestrator")
workflow.add_edge("human_feedback", "process_feedback")



memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["process_feedback"])