import streamlit as st
import json
from main import generate_content  # Import the function directly

st.title("Website Content Generator")

# User Inputs
idea = st.text_input("Enter Business Idea", "Solar Energy Solutions")
company_name = st.text_input("Enter Company Name", "GreenTech Solar")

st.subheader("Services")
services = {}
num_services = st.number_input("How many main services?", min_value=1, max_value=10, value=1)

for i in range(num_services):
    service_name = st.text_input(f"Service {i+1} Name", key=f"service_{i}")
    sub_services = st.text_area(f"Sub-services for {service_name} (comma-separated)", key=f"sub_service_{i}")
    if service_name:
        services[service_name] = [s.strip() for s in sub_services.split(",") if s.strip()]

st.subheader("Service Areas")
service_areas = st.text_area("Enter service areas (comma-separated)", "London, Manchester, Birmingham")
service_areas_list = [area.strip() for area in service_areas.split(",") if area.strip()]

st.subheader("Service Area Services")
service_area_services = {}
for area in service_areas_list:
    service_area_services[area] = {}
    for service in services.keys():
        sub_services_area = st.text_area(f"{area} - Sub-services for {service} (comma-separated)", key=f"{area}_{service}")
        service_area_services[area][service] = [s.strip() for s in sub_services_area.split(",") if s.strip()]

# Submit button
if st.button("Generate Content"):
    # Prepare the request payload
    payload = {
        "idea": idea,
        "company_name": company_name,
        "services": services,
        "service_area": service_areas_list,
        "service_area_services": service_area_services
    }

    # Call the function directly instead of making an API request
    try:
        data = generate_content(payload)
        st.success("Content Generated Successfully!")

        st.subheader("Home Page")
        st.write(data.get("home_page", "Not available"))
        
        st.subheader("About Us Page")
        st.write(data.get("about_us_page", "Not available"))
        
        st.subheader("Service Page")
        st.write(data.get("service_page", "Not available"))

        st.subheader("🔹 Individual Service Pages")
        individual_service_page = data.get("individual_service_page", "")
        if individual_service_page:
            st.markdown(individual_service_page)

        st.subheader("🌍 Service Area Page")
        service_area_page = data.get("service_area_page", "")
        if service_area_page:
            st.markdown(service_area_page)

    except Exception as e:
        st.error(f"Error: {e}")
