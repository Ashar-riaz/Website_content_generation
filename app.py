import streamlit as st
from utils import generate_content

st.title("Website Content Generator")

company_name = st.text_input("Enter Company Name", "GreenTech Solar")
idea = st.text_area("Enter Business Idea", "Solar Energy Solutions")
service_area_input = st.text_area("Enter Service Areas (comma-separated)", "Exmouth, Newton Abbot, Teignmouth, Taunton")

# Convert service_area input into a list
service_areas = [city.strip() for city in service_area_input.split(",") if city.strip()]

# 🔹 Services with Sub-services Input
st.subheader("Enter Services & Sub-services")

services = {}
num_services = st.number_input("Number of Services", min_value=1, value=1, step=1)
for i in range(num_services):
    service_name = st.text_input(f"Service {i+1} Name", f"Service {i+1}")

    num_sub_services = st.number_input(f"Number of Sub-services for {service_name}", min_value=1, value=1, step=1)
    sub_services = [st.text_input(f"Sub-service {j+1} for {service_name}", f"Sub-service {j+1}") for j in range(num_sub_services)]

    services[service_name] = sub_services

# 🔹 Service Area-wise Sub-service Selection
st.subheader("Assign Sub-services to Each City")
service_area_services = {}

for city in service_areas:
    st.subheader(f"Sub-services for {city}")

    city_services = {}
    
    for service, sub_services in services.items():
        selected_sub_services = st.multiselect(
            f"Select sub-services for {service} in {city}",
            sub_services,  # Show sub-services in dropdown
            key=f"{city}_{service}"
        )
        if selected_sub_services:
            city_services[service] = selected_sub_services  # Store only selected sub-services

    service_area_services[city] = city_services  # Store city-wise service mapping

if st.button("Generate Content"):
    with st.spinner("Generating content... Please wait ⏳"):
        content = generate_content(idea, company_name, services, service_area_services)

    st.success("Content generated successfully!")

    # Display content
    st.subheader("Home Page")
    st.markdown(content["home_page"].content)
    
    st.subheader("About Us Page")
    st.markdown(content["about_us_page"].content)
    
    st.subheader("Service Page")
    st.markdown(content["service_page"].content)

    st.subheader("Individual Service Pages")
    for sub_service, text in content["individual_service_pages"].items():
        st.markdown(f"### {sub_service}")
        st.markdown(text)
