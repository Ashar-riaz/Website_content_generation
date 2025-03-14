from langgraph.graph import END
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any
from langgraph.graph import StateGraph
from service import research_task, seo_optimization_task, content_writing_task, refine_content, evaluate_content_quality, feedback_improvement, meeting_insights, upload_file
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
    data: str
    text:str
    meeting_point:str
    file_path:str
workflow = StateGraph(ContentState)

# ✅ Define Workflow Steps
workflow.add_node("research_step", research_task)
workflow.add_node("seo_step", seo_optimization_task)
workflow.add_node("writing_step", content_writing_task)
workflow.add_node("refine_content", refine_content)
workflow.add_node("evaluate_content_quality", evaluate_content_quality)
workflow.add_node("feedback_improvement", feedback_improvement)  # Node for quality rework
workflow.add_node("human_review", lambda state: state)  # Human-in-the-loop review
workflow.add_node("meeting_insights",meeting_insights)
workflow.add_node("upload_file",upload_file)
# ✅ Define Transitions
workflow.set_entry_point("research_step")
workflow.set_entry_point("upload_file")
workflow.add_edge("upload_file", "meeting_insights")
workflow.add_edge("research_step", "seo_step")
workflow.add_edge("seo_step", "writing_step")
workflow.add_edge("meeting_insights", "writing_step")
workflow.add_edge("writing_step", "refine_content")
workflow.add_edge("refine_content", "evaluate_content_quality")

# Conditional Flow for Quality Check & Human Review
workflow.add_conditional_edges(
    "evaluate_content_quality",
    lambda state: "feedback_improvement" if state["quality_score"] <= 8 else "human_review",
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
class UpdateRequest(BaseModel):
    page_key: List[str]
    user_query: str   
def generate_content(data):  # Remove @app.post to make it an importable function
    state = content_graph.invoke({
        "idea": data["idea"],
        "company_name": data["company_name"],
        "services": data["services"],
        "service_area": data["service_area"],
        "quality_score": 0,
        "file_path": data["file_path"]
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
    prompt = f"""
    You are a professional content editor. Modify the content strictly according to the user request below.
    
    ### **Rules for Modification**  
    - Apply the requested changes **EXACTLY as specified** in the user request.  
    - **Return the entire content** with only the requested modifications applied.  
    - **DO NOT return only the changed section**—always return the full content with modifications integrated.  
    - **DO NOT rephrase or modify anything that is not explicitly requested to change.**  
    - Ensure the modified content reads naturally and maintains professional quality.  
    - **DO NOT include explanations, formatting hints, or extra commentary—only return the final updated content.**  

    ### **User Request:**  
    {user_query}

    ### **Original Content:**  
    {current_content}

    ### **Updated Content (Return Full Updated Version Below):**
    """

    # Call Gemini to process the update
    updated_content = llm.invoke(prompt).content.strip()

    # Ensure the modified content is updated correctly
    return {"page_content": updated_content}

  
