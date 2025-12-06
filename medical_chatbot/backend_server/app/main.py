from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

def get_application() -> FastAPI:
    application = FastAPI(
        title="Medical QA System",
        description="KG_RAG-based medical question answering system",
        version="1.0.0"   
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.api.api_router import router
    # application.add_middleware(DBSessionMiddleware, db_url=settings.DATABASE_URL)
    application.include_router(router)
    # application.add_exception_handler(CustomException, http_exception_handler)

    return application

app = get_application()

if __name__ == '__main__':
      
  port = int(os.environ.get("PORT", 8000))
  uvicorn.run(
      "app.main:app",
      host="127.0.0.1",
      port=port,
      reload=True,
      log_level="info"
  )

# from app.untils import context_matching
# from app.disease_entity_recognition import vectordb_client_retrival_v3

# query = "What are the symptoms of erythroleukemia?"
# entities_dict = [{'node_type': 'Disease', 'value': ['erythroleukemia']}]

# context = context_matching(query, entities_dict)
# print(context)

# enities =     {
#       "Disease": ["heart disease", "diabetes"],
#       "Compound": ["aspirin", "metformin"],
#       "Gene": [],
#       "Protein": [],
#       "Symptom": [],
#       "SideEffect": []
#     }

# result = vectordb_client_retrival_v3(enities)
# print(result)

# from app.agent.graph import app
# png_bytes = app.get_graph(xray=True).draw_mermaid_png()
# with open("workflow_graph.png", "wb") as f:
#     f.write(png_bytes)

# from app.agent.graph import app
# import gradio as gr

# # png_bytes = app.get_graph(xray=True).draw_mermaid_png()
# # with open("workflow_graph.png", "wb") as f:
# #     f.write(png_bytes)
    
# # print("Saved to workflow_graph.png")
# config = {"configurable": {"thread_id": "customer_123"}}

# def chat(user_message: str):
#   result = app.invoke({"user_input": user_message}, config)
#   state_snapshot = app.get_state(config)
#   NEXT_WAITING_NODES = {"kg_retrieve", "chitchat", "entity_resolver"}
#   if state_snapshot.next and state_snapshot.next[0] in NEXT_WAITING_NODES:
#     return {
#       "response": result.get("final_response", ""),
#       "needs_feedback": True,
#       "clarification_options": result.get("clarification_options"),
#       "state": result,
#       "metadata": result.get("metadata", {})
#     }
#   else:
#     return {
#                 "response": result.get("final_response", ""),
#                 "needs_feedback": False,
#                 "metadata": result.get("metadata", {})
#             }


# if __name__ == "__main__":
#   # gr.ChatInterface(chat, type='messages').launch()
#   # user = input("nhập gì đó: ")
#   while True:
#     user = input("nhập gì đó: ")
#     chat(user)
