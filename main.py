from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
from utils import generate_content

app = FastAPI(title="AI-Powered Website Content Generator")
# ✅ Request Model
class ContentRequest(BaseModel):
    idea: str
    company_name: str
    services: Dict[str, List[str]]  # Dict with Services & Sub-services
    service_area: str

# ✅ Response Model
class ContentResponse(BaseModel):
    home_page: str
    about_us_page: str
    service_page: str
    individual_service_pages: Dict[str, str]  # Store multiple sub-services
    quality_score: int

@app.post("/generate-content/", response_model=ContentResponse)
def generate_content_endpoint(request: ContentRequest):
    content = generate_content(request.idea, request.company_name, request.services, request.service_area)

    return ContentResponse(
        home_page=content["home_page"].content,
        about_us_page=content["about_us_page"].content,
        service_page=content["service_page"].content,
        individual_service_pages={key: val.content for key, val in content["individual_service_pages"].items()},
        quality_score=content["quality_score"]
    )
