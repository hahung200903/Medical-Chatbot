from app.agent.graph import app
from app.untils import get_respone_llm
from app.core.config_loader import *
from langchain.messages import HumanMessage
import json

PARSE_HUMAN_FEEDBACK = system_prompt["PARSE_HUMAN_FEEDBACK"]
class ChatService:
    def __init__(self, query, thread_id):
        self.query = query
        self.thread_id = thread_id
        self.config = {
            "configurable": {
                "thread_id": self.thread_id
            }
        }

    def chat(self):

        input_state = {
            "user_input": self.query,
            "conversation_history": []
        }
        result = app.invoke(input_state, self.config)
        state_snapshot = app.get_state(self.config)

        if state_snapshot.next == ("process_feedback",):
            return {
                "status": "waiting_feedback",
                "response": result.get("final_response", ""),
                "needs_feedback": True,
                "state": result,
                "metadata": result.get("metadata", {})
            }
        
        else:
            return {
                "status": "completed",
                "response": result.get("final_response", ""),
                "needs_feedback": False,
                "metadata": result.get("metadata", {})
            }
    
    def resume_with_feedback(self, feedback: str) -> dict[str, any]:

        state_snapshot = app.get_state(self.config)
        current_state = state_snapshot.values
        history = current_state.get("conversation_history", [])
        history += [HumanMessage(content=feedback)]

        print(f"[DEBUG] History: {history}")
        print(f"[DEBUG] User feedback raw: {feedback}")

        prompt = PARSE_HUMAN_FEEDBACK.format(
            user_reply = feedback
        )

        response = get_respone_llm(feedback, prompt, history)
        content_response = response.content
        final_response = json.loads(content_response.replace('json', '').replace('```', '').strip())
        print(f"[DEBUG] Parsed feedback: {final_response}")

        update_dict = {
            "feedback_type": final_response.get("feedback_type"),
            "user_feedback": final_response.get("user_feedback"),
            "resolved_entities": final_response.get("resolved", []),
            "conversation_history": [HumanMessage(content=feedback)]
        }

        if final_response.get("feedback_type") == "entity_clarified":
            rewrite_query = final_response.get("user_feedback")
            if rewrite_query:
                update_dict["user_input"] = rewrite_query
                print(f"[DEBUG] Updated user_input to: {rewrite_query}")
        
        app.update_state(self.config, update_dict)
        
        result = app.invoke(None, self.config)
        state_snapshot = app.get_state(self.config)
        
        if state_snapshot.next == ("process_feedback",):
            return {
                "response": result.get("final_response", ""),
                "needs_feedback": True,
                "metadata": result.get("metadata", {})
            }
        else:
            return {
                "response": result.get("final_response", ""),
                "needs_feedback": False,
                "metadata": result.get("metadata", {})
            }