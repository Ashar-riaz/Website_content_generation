import streamlit as st
import requests

# FastAPI Endpoint (Update this if using ngrok or a deployed server)
API_URL = "https://977b-119-156-102-95.ngrok-free.app/generate-content/"

st.title("Website Content Generator")

company_name = st.text_input("Enter Company Name", "GreenTech Solar")
services = st.text_area("Enter Services (comma-separated)", "Solar Panel Installation, Maintenance, Consultation")
idea = st.text_area("Enter Business Idea", "Solar Energy Solutions")

if st.button("Generate Content"):
    # Convert user input into JSON format
    payload = {
        "idea": idea,
        "company_name": company_name,
        "services": services
    }

    with st.spinner("Generating content... Please wait ⏳"):
        response = requests.post(API_URL, json=payload)

    # Check for errors
    if response.status_code == 200:
        st.success("Content generated successfully!")
        content = response.json()

        # Display content as plain text instead of Markdown
        st.subheader("Home Page")
        st.text(content["home_page"])  # Show as plain text

        st.subheader("About Us Page")
        st.text(content["about_us_page"])

        st.subheader("Service Page")
        st.text(content["service_page"])

        st.subheader("Individual Service Page")
        st.text(content["individual_service_page"])
    else:
        st.error(f"Failed to generate content. Please check your API.\n\nError: {response.text}")

