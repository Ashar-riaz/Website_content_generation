import streamlit as st
import json
from main import generate_content, update_page  # Import the functions

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

# Initialize session state for content storage
if "content" not in st.session_state:
    st.session_state["content"] = {}

if "history" not in st.session_state:
    st.session_state["history"] = {}


# Generate Content
if st.button("Generate Content"):
    payload = {
        "idea": idea,
        "company_name": company_name,
        "services": services,
        "service_area": service_areas_list,
        "service_area_services": service_area_services
    }

    try:
        data = generate_content(payload)
        st.success("Content Generated Successfully!")

        # Store generated content in session state
        st.session_state["content"] = data
        st.session_state["history"] = {key: [value] for key, value in data.items()}  # Store first version

    except Exception as e:
        st.error(f"Error: {e}")

# User Query for Updating Content
st.subheader("Update Content")
user_query = st.text_area("Enter modification request", "")

# Dropdown for selecting the page to update
available_pages = {
    "Home Page": "home_page",
    "About Us Page": "about_us_page",
    "Service Page": "service_page",
    "Individual Service Pages": "individual_service_page",
    "Service Area Page": "service_area_page",
}

selected_page = st.selectbox("Select the page to update", list(available_pages.keys()))

# Update Content Button
if st.button("Update Content"):
    if not user_query.strip():
        st.warning("Please enter a modification request.")
    elif "content" not in st.session_state or not st.session_state["content"]:
        st.warning("Generate content first before updating.")
    else:
        try:
            # Get the current content for the selected page
            page_key = available_pages[selected_page]
            current_content = st.session_state["content"].get(page_key, "")

            # Call update_page function
            updated_page_content = update_page({"page_content": current_content}, user_query)

            # Store the new version in session state
            if page_key in st.session_state["history"]:
                st.session_state["history"][page_key].append(updated_page_content["page_content"])
            else:
                st.session_state["history"][page_key] = [updated_page_content["page_content"]]

            # Update displayed content
            st.session_state["content"][page_key] = updated_page_content["page_content"]

            st.success(f"{selected_page} Updated Successfully!")

        except Exception as e:
            st.error(f"Error: {e}")

# Display all pages with history
st.subheader("Website Content")

for page, key in available_pages.items():
    if key in st.session_state["content"]:
        st.subheader(f"🔹 {page}")

        # Show latest content
        st.write(st.session_state["content"][key])

        # Show previous versions in an expander
        if key in st.session_state["history"] and len(st.session_state["history"][key]) > 1:
            with st.expander("📜 Previous Versions"):
                for i, old_version in enumerate(reversed(st.session_state["history"][key][:-1])):
                    st.markdown(f"**Version {len(st.session_state['history'][key]) - i - 1}**")
                    st.write(old_version)
                    st.markdown("---")
