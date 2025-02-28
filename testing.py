
from langgraph.graph import END
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Any
from langgraph.graph import StateGraph
from service import research_task, seo_optimization_task, content_writing_task, refine_content, evaluate_content_quality, feedback_improvement

app = FastAPI()
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
# ✅ Define Transitions
workflow.set_entry_point("research_step")
workflow.add_edge("research_step", "seo_step")
workflow.add_edge("seo_step", "writing_step")
workflow.add_edge("writing_step", "refine_content")
workflow.add_edge("refine_content", "evaluate_content_quality")
# Conditional Flow for Quality Check
workflow.add_conditional_edges(
    "evaluate_content_quality",
    lambda state: "feedback_improvement" if state["quality_score"] <= 7 else END,
    {
        "feedback_improvement": "feedback_improvement",
        END: END
    }
)
# ✅ Add Loopback from feedback_improvement to refine_content
workflow.add_edge("feedback_improvement", "evaluate_content_quality")
# ✅ Compile the Graph
content_graph = workflow.compile()
class RequestModel(BaseModel):
    idea: str
    company_name: str
    services: Dict[str, List[str]]
    service_area: List[str]
    service_area_services: Dict[str, Dict[str, List[str]]]

@app.post("/generate-contentsd/")
def generate_content(data: RequestModel):
   
        state = content_graph.invoke({
            "idea": data.idea,
            "company_name": data.company_name,
            "services": data.services,
            "service_area": data.service_area,
            "service_area_services": data.service_area_services,
            "quality_score": 0  # Initialize quality score
        })

        response = {
            "home_page": state["home_page"],
            "about_us_page": state["about_us_page"],
            "service_page": state["service_page"],
            "individual_service_page": state["individual_service_page"],
            "service_area_page": state["service_area_page"]
        }
        
        return response
  
