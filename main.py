
from langgraph.graph import END
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any
from langgraph.graph import StateGraph
from service import research_task, seo_optimization_task, content_writing_task, refine_content, evaluate_content_quality, feedback_improvement
from langchain_google_genai import ChatGoogleGenerativeAI


app = FastAPI()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
class ContentState(Dict):
    idea: str
    company_name: str
    services: Dict[str, List[str]]  # Main services with their sub-services
    service_area: Dict[str, Dict[str, str]]  # Each area has multiple sub-service pages
    research_data: str
    seo_optimization: str
    home_page: str
    about_us_page: str
    service_page: str
    individual_service_page: Dict[str, str]  # Single service pages
    service_area_page: Dict[str, Dict[str, str]]  # Each area with its sub-services
    quality_score: int
    feedback: str
    content: str
    service_area_services: Dict[str, Dict[str, List[str]]]
workflow = StateGraph(ContentState)

# ✅ Define Workflow Steps
workflow.add_node("research_step", research_task)
workflow.add_node("seo_step", seo_optimization_task)
workflow.add_node("writing_step", content_writing_task)
workflow.add_node("refine_content", refine_content)
workflow.add_node("evaluate_content_quality", evaluate_content_quality)
workflow.add_node("feedback_improvement", feedback_improvement)  # New Node
workflow.add_node("human_review", lambda state: state)  # Human-in-the-loop review
# ✅ Define Transitions
workflow.set_entry_point("research_step")
workflow.add_edge("research_step", "seo_step")
workflow.add_edge("seo_step", "writing_step")
workflow.add_edge("writing_step", "refine_content")
workflow.add_edge("refine_content", "evaluate_content_quality")

# Conditional Flow for Quality Check & Human Review
workflow.add_conditional_edges(
    "evaluate_content_quality",
    lambda state: "feedback_improvement" if state["quality_score"] <= 7 else "human_review",
    {
        "feedback_improvement": "feedback_improvement",
        "human_review": "human_review"
    }
)

# ✅ Add Loopback from feedback_improvement to refine_content
workflow.add_edge("feedback_improvement", "evaluate_content_quality")

# ✅ Add Human-in-the-loop approval before finalization
workflow.add_edge("human_review", END)
# ✅ Compile the Graph
content_graph = workflow.compile()
class RequestModel(BaseModel):
    idea: str
    company_name: str
    services: Dict[str, List[str]]
    service_area: List[str]
    service_area_services: Dict[str, Dict[str, List[str]]]
class UpdateRequest(BaseModel):
    page_key: List[str]
    user_query: str   
def generate_content(data):  # Remove @app.post to make it an importable function
    state = content_graph.invoke({
        "idea": data["idea"],
        "company_name": data["company_name"],
        "services": data["services"],
        "service_area": data["service_area"],
        "quality_score": 0
    })

    response = {
        "home_page": state.get("home_page", ""),
        "about_us_page": state.get("about_us_page", ""),
        "service_page": state.get("service_page", ""),
        "individual_service_page": state.get("individual_service_page", {}),
        "service_area_page": state.get("service_area_page", {})
    }
    
    return response  # Return dictionary instead of JSONResponse

@app.put("/update-page/")
def update_page(state: dict, user_query: str):
    """
    Updates the selected page content based on user feedback.
    """
    current_content = state.get("page_content", "")

    # Define the prompt for updating the content
    prompt = f"""You are an expert content editor. Modify the content according to this exact request: {user_query}. 

    - If the request asks to remove specific text, completely delete it while keeping the content natural and professional.
    - If the request involves replacing text, swap it exactly as instructed.
    - If the request requires rewording, refine the text while keeping the meaning intact.
    - Do not add explanations, comments, formatting hints, or additional modifications—only return the updated version of the content.
    - Ensure that only the requested changes are made. Do not include the previous version or additional variations.
    
    Here is the content before modification:
    ---
    {current_content}
    ---

    Return only the fully updated content without any extra details.
    and update only the content that needs to be changed and shown with all content.
    """

    # Call Gemini to process the update
    updated_content = llm.invoke(prompt).content.strip()

    # Ensure the modified content is updated correctly
    return {"page_content": updated_content}

  
