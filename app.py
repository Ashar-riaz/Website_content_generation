import streamlit as st
import requests
from utils import generate_content
# FastAPI Endpoint (Update this if using ngrok or a deployed server)
# API_URL = "https://231e-119-156-102-95.ngrok-free.app/generate-content/"

st.title("Website Content Generator")

company_name = st.text_input("Enter Company Name", "GreenTech Solar")
services = st.text_area("Enter Services (comma-separated)", "Solar Panel Installation, Maintenance, Consultation")
idea = st.text_area("Enter Business Idea", "Solar Energy Solutions")

if st.button("Generate Content"):
    # Convert user input into JSON format
    # payload = {
    #     "idea": idea,
    #     "company_name": company_name,
    #     "services": services
    # }

    with st.spinner("Generating content... Please wait ⏳"):
        content = generate_content(idea, company_name, services)
    # Check for errors
    
    st.success("Content generated successfully!")
    # content = response.json()
    # Display content as plain text instead of Markdown
    st.subheader("Home Page")
    st.markdown(content["home_page"].content)  # Show as plain text
    st.subheader("About Us Page")
    st.markdown(content["about_us_page"].content)
    st.subheader("Service Page")
    st.markdown(content["service_page"].content)
    st.subheader("Individual Service Page")
    st.markdown(content["individual_service_page"].content)


