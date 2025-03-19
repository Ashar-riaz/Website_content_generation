from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langgraph.graph import END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph
from typing import Dict, List
from docx import Document
# ✅ Set Google Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAExa1yC6Y0LtTbCTJKa64CT8f8I1roqR0"
# ✅ Initialize Google Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# ✅ Define Search Tool
search_tool = DuckDuckGoSearchRun(region="uk-en", safe="strict")
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
    data: str
    text:str
    meeting_point:str
    file_path:str

# ✅ Define Workflow
workflow = StateGraph(ContentState)
system_prompt= f"""
    You are an expert content writer specialising in creating professional, informative and customer-focused content for service-based businesses in the UK Your writing should be clear engaging and persuasive while maintaining a warm and trustworthy tone Use UK spelling grammar and a tone that resonates with a UK audience Avoid excessive punctuation only use it where necessary for clarity

When writing
1 Use a friendly but authoritative tone emphasising expertise and reliability
2 Keep sentences short and direct avoiding overly technical language unless necessary
3 Highlight key selling points clearly using bullet points or structured paragraphs to improve readability
4 Maintain a customer-focused perspective reassuring the reader and addressing potential concerns proactively
5 Ensure the content flows logically starting with broad information before diving into specifics
6 Use persuasive language to encourage action while avoiding aggressive sales tactics

Example Output
Trust Our Expert Heating Engineers in Exeter
Our Gas Safe registered engineers have over 40 years of experience in boiler installations servicing and repairs We specialise in fitting A rated energy efficient boilers from leading brands If you need a new boiler or a fast repair we’re here to help

🔹 Fast and Reliable Service – We aim for same day repairs and next day boiler installations
🔹 Free Smart Thermostat – Get a smart thermostat included with every new boiler installation
🔹 7 Day Availability – We work around your schedule offering flexible appointments

For expert heating and plumbing services in Exeter Exmouth Teignmouth and beyond contact us today

"""
# ✅ Research Task
def research_task(state: ContentState) -> ContentState:
    research_query  = f"{state['idea']}-{state['company_name']} - {state['services']}"
    research_data = search_tool.run(research_query )
    state.update({"research_data": research_data})
    return state

# ✅ SEO Optimization Task
def seo_optimization_task(state: ContentState) -> ContentState:
    prompt = f"Optimize the following research for SEO: {state['research_data']}"
    seo_optimization = llm.invoke(prompt)
    state.update({"seo_optimization": seo_optimization})
    print("seo_done",seo_optimization)
    return state

# ✅ Content Writing Task (Generates Home, About Us, and Service Pages)
def content_writing_task(state: ContentState) -> ContentState:
    research_data = state["research_data"]
    seo_data = state["seo_optimization"]
    services = "\n".join(f"- {service}" for service in state["services"])
    main_services = list(state["services"].keys())  # Extract main service names
    main_services_str = "\n".join(f"- {service}" for service in main_services)  # Format for readability
    services_list = [
        subservice
        for main_service, subservices in state["services"].items()
        for subservice in subservices
    ]

    service_area = "\n".join(f"- {area}" for area in state["service_area"])
    company_name=state["company_name"]
    prompts = {
            "home_page": f"""You are an expert web content writer specializing in **SEO-optimized, high-converting website copy**. Your task is to write a compelling **Home Page** for a company named **{company_name}**, which provides **{services}**. Your writing should be persuasive, well-structured, and engaging while maintaining a clear, informative tone.

              ### **Key Requirements:**

              #### **1. Engaging Headline & Subheadline:**
              - Create a powerful, attention-grabbing **headline** that highlights the company’s expertise and core offering.
              - Follow with a **subheadline** that builds trust and credibility while reinforcing key benefits.

              #### **2. Strong Introduction (First 2-3 Sentences Must Hook the Reader):**
              - Clearly introduce the company, its specialization, and the core services.
              - Ensure the tone is professional yet friendly to build trust and engagement.

              #### **3. Service Sections (Well-Structured & Persuasive):**
              - **Break down key services** (**{services_list}**) into well-defined sections.
              - Explain the benefits of each service using a persuasive yet informative style.
              - Highlight **unique selling points** (e.g., fast installation, expert engineers, same-day service).
              - If applicable, mention warranties, certifications, and brand affiliations.
              - Service show in a paragraph. The heading should be the service name and then the paragraph should be the service description.

              #### **4. Trust & Experience (Builds Authority):**
              - Showcase the company’s years of experience, qualifications, and certifications.
              - Mention **Gas Safe registration**, City and Guilds qualifications, or any other relevant credentials.

              #### **5. Customer Benefits & Competitive Advantages:**
              - Clearly **differentiate** this company from competitors.
              - Emphasize **why customers should choose this business** (e.g., fast service, 7-day availability, great warranties).
              - Mention any **freebies or added-value services** (e.g., “Free Smart Thermostat with Every Boiler Installation”).

              #### **6. **Why Choose Us?** (Unique Selling Points)
              - Emphasize what sets the company apart (e.g., 24/7 availability, warranties, financing options, and add other which give plus points).
              - Reinforce a **customer-first approach**, focusing on transparency, trust, and superior service.

              #### **7. Call to Action (Drives Conversions):**
              - End with a **strong, action-oriented CTA**, such as:
                - “Get a Free Quote Today – Call Now!”
                - “Book Your Boiler Installation in Just 24 Hours!”
              - Encourage urgency and easy next steps.

              #### **8. SEO Optimization (Ensures Visibility):**
              - Naturally integrate **high-ranking keywords** without keyword stuffing.
              - Ensure content is structured for **readability and engagement**.
              - Generate a **compelling meta description** (160 characters max) that improves search engine click-through rates.

              #### **9. Local Relevance (If Applicable):**
              - Ensure the content is adaptable to any location unless specified.
              - If a location is provided, highlight **local expertise** and availability.

              #### **10. Insights from Client Meeting (Ensures Accuracy & Alignment):**
              - Incorporate key takeaways from the client meeting.
              - Use the following extracted insights to align the website content with client expectations:
                {state["meeting_point"]}

              **Use the following research data for accuracy:**
              {research_data}

              **Apply these SEO best practices:**
              {seo_data}

              Ensure the content is UK based, use UK keywords, persuasive, engaging, and easy to read. Keep paragraphs short and **use bullet points for clarity when needed**. Your writing should feel **professional yet approachable**, with a strong focus on **conversion and engagement**.
              Please do not provide code or HTML tags and avoid using colons in the middle of sentences.
              """,
 "about_us_page": f"""You are an expert web content writer skilled in crafting **engaging, structured, and customer-focused About Us pages**.  
                Write a professional and compelling **About Us** page for **{company_name}**, a trusted provider of **{services}**. The content must be well-structured, engaging, and clearly communicate the company’s mission, services, and coverage areas.  

                ### **Key Requirements:**  

                #### **1. Introduction (Who We Are & What We Do)**  
                - Start with a strong, engaging introduction that:  
                  - Establishes expertise and credibility.  
                  - Mentions **years of experience, location, and key services**.  
                  - Highlights the company’s commitment to **quality, customer satisfaction, and professional service**.  
                  - Provide **detailed company information** to build trust and authority.  

                #### **2. Our Mission & Values**  
                - Describe the company’s **core values and commitment**:  
                  - Integrity, professionalism, and high-quality service.  
                  - Dedication to customer-first service and long-term client relationships.  

                #### **3. Service Overview (With Subservices in Bullet Points)**  
                - Display only **the services exactly as provided in `{services_list}`**, without modifying or adding extra services.  
                - Ensure subservices **stay in their original format** without splitting words.  
                - Example structure:  

                {services_list}  

                #### **4. Areas We Serve (Exact Format & Integrity Preserved)**  
                - Display only **the locations exactly as provided in `{service_area}`**.  
                - Ensure locations with **multiple words remain intact** (e.g., "Newton Abbot" will not split).  
                - Display in a **clean bullet-point list**.  

                {service_area}  

                #### **5. Insights from Client Meeting (Ensures Accuracy & Alignment)**  
                - Use the following extracted insights from the client meeting to align the content with their expectations:  
                  {state["meeting_point"]}  

                #### **6. SEO Optimization (Improves Search Visibility)**  
                - Naturally integrate **SEO best practices** to improve online visibility.  
                - Use **high-ranking keywords** while ensuring natural readability.  
                - Maintain a **clear and structured format** to enhance search rankings.  
                - Include a **compelling meta description** (max 160 characters) for better click-through rates.  

                #### **7. Research-Based Accuracy**  
                - Ensure the content is aligned with industry standards and trends.  
                - Use the following research data to enhance credibility:  
                  {research_data}  

                #### **8. Call to Action (Encouraging Customer Engagement)**  
                - End with a **clear and compelling CTA**, such as:  
                  - **"For expert services in {service_area}, contact us today!"**  
                  - **"Get in touch to schedule your consultation."**  

                ### **Page Structure:**  
                1. **About {company_name}** (Introduction)  
                2. **Our Mission & Values** (Commitment to quality and customer satisfaction)  
                3. **Our Services** (List services dynamically from `{services_list}`)  
                4. **Areas We Cover** (List locations dynamically from `{service_area}`)  
                5. **Client Insights** (Incorporate `{state["meeting_point"]}` for alignment)  
                6. **SEO & Research** (Ensure factual accuracy and search visibility)  
                7. **Contact Us** (Call to Action)  

                Ensure the content is **concise, well-structured, and SEO-friendly**, using **bullet points** for readability and **natural keyword integration** for better search rankings.  
                Please do not provide code or HTML tags.  
                """,


    "service_page": f"""You are a professional web content strategist and expert copywriter.
              Create a **well-structured, engaging, and customer-focused service page** for {company_name}.
              Ensure that **each main service has its own heading**, with **detailed descriptions of all corresponding subservices** underneath in a structured format.

              ---

              ### **Key Requirements:**

              #### **1. Headline & Introduction**
              - Start with a **strong, engaging headline** introducing the main service category.
              - Provide a **concise yet compelling introduction**, highlighting why this service is important and how it benefits customers.

              #### **2. Service Breakdown (Main Services & Corresponding Subservices)**
              - Each **main service** from `{main_services_str}` should be displayed as a heading, followed by a structured description.
                - **Format:** `## Main Service Name`
              - Each **subservice** from `{services}` should be described thoroughly underneath its corresponding main service:
                - **Format:** `### Subservice Name`
                - **Include a full, well-structured description** that explains the service, its purpose, benefits, and any unique value it offers to customers.

              #### **Example Format:**

              ## Solar Panel Installation**
              At {company_name}, we provide expert solar panel installation services designed to maximize energy efficiency and savings. Our goal is to make solar energy accessible and affordable, ensuring that your home or business benefits from clean and sustainable power.

              ### **High-Quality Solar Panels Installed**
              We offer premium-grade solar panels tailored to your property's energy needs. Our experts assess your location, energy consumption, and budget to create an optimal solar solution that maximizes savings and efficiency.

              ### **Professional System Maintenance**
              Regular maintenance is essential for ensuring the longevity and performance of your solar energy system. Our team conducts thorough inspections, panel cleaning, and system diagnostics to maintain efficiency and extend the life of your investment.

              ### **Fast and Reliable Repairs**
              If your solar panels or inverters develop faults, our skilled technicians provide prompt repair services to restore functionality. We quickly diagnose issues such as wiring problems, faulty components, and system inefficiencies, ensuring your system operates at peak performance.

              ### **Expert Solar Consultation**
              Not sure which solar solution is best for your property? Our consultation services include detailed site evaluations, financial feasibility studies, and customized system design recommendations to help you make the best investment decision.

              ---

              ## Electrical Wiring**
              Proper wiring ensures your solar power system functions safely and efficiently. At {company_name}, we provide expert electrical wiring services to guarantee seamless energy distribution from your solar panels to your home or business.

              ### **Fixed Wiring Solutions**
              Our professional team offers high-quality fixed wiring solutions designed for maximum stability and efficiency. We ensure compliance with industry safety standards and optimal electrical performance for your solar system.

              ### **New Wiring Installations**
              If your current electrical setup is outdated or inadequate for your solar energy needs, we provide new wiring installations that improve energy flow and ensure seamless connectivity between components.

              ---

              #### **3. Service Process Overview**
              - Provide a **clear, step-by-step breakdown** of how the service is delivered.
              - Keep it **simple, engaging, and informative**.

              #### **4. Insights from Client Meeting (Ensures Accuracy & Alignment)**
              - Incorporate key takeaways from the client meeting to align service descriptions with customer expectations:
                {state["meeting_point"]}

              #### **5. Call to Action (CTA)**
              - End with a **strong, persuasive CTA**, such as:
                - **"Contact us today for a free consultation!"**
                - **"Book your service now and enjoy hassle-free solar solutions."**

              #### **6. SEO Optimization & Readability**
              - Ensure content is **SEO-optimized** for better search rankings.
              - Use **concise paragraphs, bullet points, and subheadings** for easy reading.

              #### **7. Adaptability**
              - **Do not mention specific locations unless required.**
              - **Use this research:** {research_data}
              - **Apply these SEO best practices:** {seo_data}

              The content must be **engaging, structured, and persuasive**, ensuring customers can easily navigate and understand your services.

              ---
              Please do not provide code or HTML tags.
              """,


    "individual_service_page": f"""
                Each service listed below must have its **own dedicated page** with content that is **specific to that subservice**. **Ensure that a response is generated for every subservice** without skipping any.

            **📌 Important Instructions:**
            - Generate **a full separate response for each subservice** in `{services_list}`.
            - Do **not** skip any subservice.
            - Do **not** mix content between subservices.
            - The content must be **unique for each subservice** and **not generic**.
            - Maintain a **consistent format** and ensure high-quality, structured writing.
            - The output must include **every subservice in the input list**.
            - **Use SEO best practices** and relevant keywords for better search rankings.

            ---  

            🔹 **For each subservice in `{services_list}`, use the following structure:**  

            ---  

            ### **[Subservice Name]**  

            #### **Trusted [Subservice Name] Experts**  
            - Provide a compelling introduction emphasizing expertise and trustworthiness.  
            - Mention the experience and commitment to customer satisfaction.  

            #### **What is [Subservice Name]?**  
            - Define `[Subservice Name]` clearly and concisely.  
            - Explain how it works and why it is beneficial.  
            - Ensure the explanation is **exclusive to this subservice**.  

            #### **Why Choose Our [Subservice Name] Services?**  
            - List reasons why customers should trust your services.  
            - Highlight experience, qualifications, and customer-centric approach.  
            - Use **bullet points** for clarity.  

            #### **Key Benefits of [Subservice Name]**  
            - List the main benefits of this specific service.  
            - Explain how customers will benefit from choosing this service.  
            - Use **bullet points** for clarity.  

            #### **Signs You Need [Subservice Name] (if applicable)**  
            - Provide a list of signs that indicate when this service is needed.  
            - Keep it **directly relevant** to this service.  

            #### **How Our [Subservice Name] Process Works**  
            - Describe the process step by step in an easy-to-understand manner.  
            - Ensure clarity and professionalism.  

            #### **Insights from Client Meeting (Ensures Accuracy & Alignment)**  
            - Incorporate key takeaways from the client meeting to align content with expectations:  
              {state["meeting_point"]}  

            #### **SEO Optimization & Research-Based Accuracy**  
            - Integrate **high-ranking keywords** naturally for SEO optimization.  
            - Ensure content is structured for **readability and engagement**.  
            - Use the following research data to enhance credibility:  
              {research_data}  
            - Apply these **SEO best practices** for better visibility:  
              {seo_data}  

            #### **Call to Action**  
            - End with a strong **Call to Action (CTA)**, encouraging visitors to **book, contact, or request a quote**.  
            - Include a **phone number, email, or link** for immediate action.  

            ---  

            **📌 Final Reminder:**  
            ✅ **Generate content for every subservice** listed in `{services_list}`.  
            ✅ Do **not** generate only one or a few subservices; all must be included.  
            ✅ Keep responses **structured, engaging, and informative**.  
            ✅ Maintain a **professional yet persuasive** tone.  
            ✅ Ensure **SEO-friendly** and **human-like writing**.  
            ✅ Do **not** include any code or HTML tags.  
            """,


"service_area_page": f"""
                    Generate a detailed and engaging service area page for {service_area}.

                    For each service in {services_list}, follow this structured format:

                    ---
                    {service_area}

                    ### [Unique, keyword-rich heading including the service name and {service_area}]
                    - Write a compelling introduction about this service, explaining its importance and benefits for customers in {service_area}. 
                    - Highlight key features and how it addresses specific needs.  

                    - Provide additional details, such as:
                      - The expertise of the team.
                      - Service quality and any guarantees.
                      - Unique aspects of this service in {service_area} (e.g., compliance with local regulations, availability, or exclusive offers).  

                    - Ensure the content is **informative, specific, and valuable to the reader**.  
                    - Maintain a **natural variation in wording** while keeping the format consistent across all services.  
                    - Each service description should be in paragraph form, with the **service name as the heading** followed by the description.  
                    - Ensure all services are displayed in full.  

                    ### **Insights from Client Meeting (Ensures Accuracy & Alignment)**  
                    - Incorporate key takeaways from the client meeting to align the content with expectations:  
                      {state["meeting_point"]}  

                    ### **SEO Optimization & Research-Based Accuracy**  
                    - Naturally integrate **high-ranking keywords** for SEO optimization.  
                    - Ensure content is structured for **readability and engagement**.  
                    - Use the following research data to enhance credibility:  
                      {research_data}  
                    - Apply these **SEO best practices** for better search rankings:  
                      {seo_data}  

                    **Final Requirements:**  
                    ✅ Ensure content is **location-specific** to {service_area}.  
                    ✅ Keep the tone **professional, engaging, and informative**.  
                    ✅ Do **not** use generic descriptions—each service must be unique.  
                    ✅ Maintain **SEO-friendly** and **human-like writing**.  
                    ✅ Do **not** include any code or HTML tags.  
                    """,

}
    pages = {key: llm.invoke([{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]) for key, prompt in prompts.items()}
    state.update(pages)
    print("content_done")
    return state

def refine_content(state: ContentState) -> ContentState:
    company_name=state["company_name"]

    prompts = {
        "home_page": f"""You are an expert UK-based web content writer. Your task is to refine the following **Home Page Content** to match the structure, style, and detail level of top-tier UK service websites. The content should be well-organized, highly detailed, and formatted professionally.
        ---

        ### **Few-Shot Examples of Desired Structure (UK-Specific, Highly Detailed)**

        #### **Example 1 - Exeter’s Heating Experts**
        🏡 **Your Trusted Local Heating Specialists**
        | Providing Gas Boiler Installations & Central Heating Solutions Across Exeter & South Devon

        🔹 **Professional Boiler Installations – A-rated Efficiency & Reliability**
        At **South Coast Plumbing and Heating**, we specialise in fitting modern **A-rated combi, traditional, and system boilers** from **Viessmann, Worcester Bosch, and Vaillant**—brands known for their exceptional reliability and energy efficiency. Our **Gas Safe registered engineers** ensure that your new boiler is installed safely, efficiently, and in compliance with **UK heating regulations**.

        ⭐ **Why Choose Us for Your Boiler Installation?**
        ✔ **Next-Day Boiler Fitting:** If your boiler breaks down unexpectedly, we can fit a **replacement boiler within 24 hours**.
        ✔ **Free Smart Thermostat:** Every boiler installation includes a **smart thermostat**, helping you **reduce energy bills** by up to 30%.
        ✔ **Extended Manufacturer’s Warranties:** We offer warranties of **up to 10 years** for select models, ensuring peace of mind.

        🔹 **Experienced & Certified Heating Engineers**
        Our team is **Gas Safe Registered** and **certified through City & Guilds**, with a **combined experience of over 40 years**. We’ve worked on **every type of heating system**, meaning we can handle anything from complex installations to emergency repairs.

        📞 **Reliable Customer Service** – We always **answer your calls** and **respond promptly** to your inquiries, so you’re never left waiting when you need help.

        🔹 **Air-Source Heat Pump Installations – Future-Proof Your Home**
        Looking for a sustainable heating solution? We install **energy-efficient air-source heat pumps** that help **reduce carbon footprint** and **lower heating costs**. These systems **extract heat from the air** to provide **year-round warmth**, even in cold UK weather.

        🔹 **Annual Boiler Servicing – Keep Your Heating System Running Smoothly**
        Regular servicing extends the **lifespan of your boiler** and prevents costly breakdowns. Our **comprehensive servicing includes**:
        ✅ Checking for **gas leaks and corrosion**
        ✅ Testing **efficiency and emissions**
        ✅ Inspecting **safety controls and components**
        ✅ Cleaning & optimizing **internal parts**

        🗓 **Book your annual servicing today** to keep your heating system in peak condition!

        ---

        #### **Example 2 - Cheltenham Heating Solutions**
        🔥 **Your Local Heating & Boiler Experts in Cheltenham, Gloucester, and Worcestershire**

        ✅ **New Gas Boilers - High Efficiency & Cost Savings**
        We supply and install the **latest A-rated boilers** from **Worcester Bosch, Vaillant, and Ideal**. Our boilers come with **up to 10 years’ warranty** and are **professionally installed by our Gas Safe engineers**.

        ⭐ **Exclusive Benefits When You Choose Us:**
        ✔ **FREE Annual Boiler Servicing** – We service your boiler **free of charge** for the **entire length of your warranty**!
        ✔ **Flexible Finance Options** – Spread the cost of your new boiler with **0% interest-free finance**.
        ✔ **Expert Guidance & No Hard Sell** – We provide **honest advice** and won’t pressure you into unnecessary purchases.

        📞 **Emergency Boiler Repairs - Fast Response**
        Boiler failure? No heating or hot water? Our **emergency call-out service** ensures a **same-day response** to restore warmth to your home quickly.

        🔹 **Comprehensive Central Heating Services**
        From full **central heating system installations** to **power flushing** and **radiator repairs**, we offer a **complete range of services** to keep your home warm and energy-efficient.

        🛠 **What We Offer:**
        ✅ **Gas Boiler Replacements & Repairs**
        ✅ **Landlord Gas Safety Certificates (CP12)**
        ✅ **Radiator & Thermostat Installations**
        ✅ **Power Flushing for Heating Systems**
        ✅ **Emergency Plumbing Services**

        📍 **Areas We Cover:** Cheltenham, Gloucester, Tewkesbury, Worcester, Stroud, and surrounding areas.

        ---

        ### **NOW, Refine the Following Home Page Content to Match These High-Detail Examples:**

        {state["home_page"].content}

        ---

        ### **📌 Instructions for Refinement (UK-Specific, Highly Detailed & Professional):**
        ✅ **Enhance Detail & Professionalism:** The content should be **well-structured, informative, and engaging**.
        ✅ **Use UK Spelling & Terminology:** Ensure terms like **Gas Safe, A-rated boilers, VAT, CP12 certificates, Smart Thermostats, 10-Year Warranties** are included.
        ✅ **Use UK city only :** If the city need then use only UK city not a other**.
        ✅ **Improve Readability:** Format with **clear headings, bullet points, and short paragraphs** for better user experience.
        ✅ **Make it SEO-Friendly (Without Being Robotic):** Use relevant keywords naturally, ensuring it reads as **authentic, high-quality website content**.
        ✅ **Focus on Benefits & Trustworthiness:** Clearly outline **why customers should choose this company**, including guarantees, fast response times, expert knowledge, and certifications.
        ✅ **Ensure Content is UK Market-Specific:** Adapt services, pricing models, and customer expectations to fit UK consumer standards.
        ✅  Do NOT modify punctuation or add extra symbols. Maintain the original punctuation exactly as provided.
        ✅  Do NOT add colon in the center of the sentence.

        Return the improved home page content in a **fully structured, highly detailed, and polished format** suitable for a professional UK service business website.
         Not give any code and html tags.""",

       "about_us_page": f""" You are an expert UK-based content writer specializing in home services. Your task is to refine the following **About Us Page Content** for a heating and plumbing company to match the structure, style, and detail level of top-tier UK service websites. The content should be well-organized, informative, and highly professional.
        ---
        ### **Few-Shot Examples of Desired Structure (UK-Specific, Highly Detailed)**

        #### **Example 1 - South Coast Plumbing and Heating**
        🏡 **Experienced Heating & Plumbing Specialists in Exeter, Devon**

        **South Coast Plumbing and Heating** is a trusted team of **Gas Safe-registered engineers and certified plumbers** with over **20 years of industry experience**. We proudly serve **both domestic and commercial clients** across **Exeter, Devon, and the surrounding areas**, offering comprehensive heating and plumbing services.

        🔹 **Our Expertise Includes:**
        ✔ **New Gas & Oil Boiler Installations** – We specialise in the installation of modern **A-rated gas and oil boilers**, ensuring energy-efficient heating solutions for homes and businesses.
        ✔ **Boiler Repairs & Servicing** – Our **Gas Safe registered engineers** carry out professional repairs and servicing, extending the lifespan of your boiler and preventing costly breakdowns.
        ✔ **Air-Source Heat Pumps** – We install **renewable heating systems**, such as **air-source heat pumps**, to provide a **sustainable alternative** to traditional heating.
        ✔ **Central Heating Systems & Power Flushing** – Our team also handles full central heating installations and **system power flushing**, ensuring that your home stays warm and your heating system operates at peak performance.

        🔹 **Why Choose Us?**
        ✔ **Over 20 Years of Experience** – We’ve built our reputation by delivering **reliable, affordable, and high-quality services**.
        ✔ **24/7 Emergency Plumbing** – We’re available around the clock for emergency plumbing needs.
        ✔ **Fully Qualified & Gas Safe Registered** – All our engineers are **fully certified**, offering peace of mind that your home is in expert hands.
        ✔ **Areas We Cover:** Exeter, Exmouth, Newton Abbot, Taunton, Honiton, and surrounding areas.

        🔹 **Our Commitment:**
        At **South Coast Plumbing and Heating**, we focus on delivering a **personalised, customer-centric service**. We believe in honesty, integrity, and **exceptional workmanship**. Whether it’s a routine boiler service or an urgent repair, we treat every project with the same level of care and professionalism.

        ---

        #### **Example 2 - Superior Heat Solutions**
        🔥 **Your Local Heating Experts in Central Scotland**

        At **Superior Heat Solutions**, we take pride in our team’s **14+ years of experience** in the heating and plumbing industry. We provide **high-quality, energy-efficient solutions** to meet your unique needs—whether it’s a new boiler, **central heating repairs**, or a **full bathroom installation**.

        🔹 **Our Core Services Include:**
        ✔ **New Boiler Installations** – We offer **A-rated gas boilers** from leading brands such as **Vaillant, Worcester Bosch, and Ideal**, backed by up to **10-year warranties**.
        ✔ **Air Source Heat Pumps** – Our engineers are skilled in installing **eco-friendly heat pumps**, which help reduce carbon emissions and lower heating costs.
        ✔ **Power Flushing** – We provide professional **power flushing services** to remove sludge and debris from your heating system, improving efficiency and performance.
        ✔ **General Plumbing Services** – From fixing leaks to **installing new radiators**, our team is equipped to handle all your plumbing needs.

        🔹 **Our Promise to You:**
        ✔ **Guaranteed Quality Work** – We stand behind our work, ensuring that every project is completed to the **highest standard**.
        ✔ **Affordable Pricing & Transparent Quotes** – We promise to beat any written quote for **boiler installations**, ensuring you get the best value for money.
        ✔ **Constant Communication** – We keep you updated at every stage of the project, offering clear guidance and transparent advice.

        🔹 **Areas We Serve:**
        We proudly serve **Cheltenham**, **Gloucester**, **Tewkesbury**, **Stroud**, and the surrounding areas in **Central Scotland**.

        ---

        ### **NOW, Refine the Following About Us Content to Match These High-Detail Examples:**

        {state["about_us_page"].content}

        ---

        ### **📌 Instructions for Refinement (UK-Specific, Highly Detailed & Professional):**
        ✅ **Enhance Detail & Professionalism:** The content should be **well-structured**, **clear**, and **engaging**.
        ✅ **Use UK Spelling & Terminology:** Ensure terms like **Gas Safe**, **A-rated boilers**, **VAT**, and **renewable energy** are included.
        ✅ **Improve Readability:** Use **clear headings**, **bullet points**, and **short paragraphs** for ease of reading.
        ✅ **Focus on Benefits & Trustworthiness:** Make sure to clearly outline **why customers should choose this company**, highlighting **experience, customer service, and certifications**.
        ✅ **Make it SEO-Friendly:** Integrate **relevant UK-based keywords** naturally into the content to improve SEO ranking without sacrificing readability.
        ✅ **Include Location Details & Coverage Areas:** Clearly specify the regions served, emphasizing the **local expertise** of the business.

        Return the improved **About Us Page** content in a **fully structured, highly detailed, and polished format** suitable for a professional UK service business website.
         Not give any code and html tags.""",




        "service_page": f""" You are an expert in creating **SEO-optimized, highly detailed, and engaging** service pages for business websites.
Your task is to **refine the service page content** to make it more structured, comprehensive, and conversion-friendly.

### **Instructions for Refinement:**
- **Expand Each Section** – Provide **in-depth descriptions** of the services, including their **benefits and processes**.
- **Use Clear Headings & Subheadings** – Structure the content properly for **better readability and SEO**.
- **Highlight Key Features with Bullet Points** – Make the information **easy to scan and engaging**.
- **Incorporate Persuasive & Actionable Language** – Encourage visitors to **take action** (e.g., **"Get a Free Quote Today!"**).
- **Ensure Natural Keyword Integration** – Optimize for **search engines** while keeping it human-friendly.
- **Mention the Location Where Relevant** – If the services are location-specific, naturally include city names.

---

### **Examples of Well-Structured Service Pages:**

#### **🔹 Emergency Plumbing Services in Lancashire**
At **Jaws Gas Services**, we specialize in **fast-response emergency plumbing** across Lancashire, covering areas like **Blackburn, Bolton, Burnley, Preston, and Blackpool**. Our team is available **24/7** to handle urgent plumbing problems.

### **Why Choose Our Emergency Plumbing Service?**
✅ **Rapid Response:** We arrive quickly to prevent further damage.
✅ **Expert Repairs:** Skilled plumbers with years of experience.
✅ **Transparent Pricing:** No hidden charges—just fair, upfront costs.
✅ **Local & Trusted:** A dedicated Lancashire-based team you can rely on.

### **Common Emergency Plumbing Issues We Fix:**
- **Burst Pipes & Leaks** – We quickly repair and replace damaged pipes.
- **No Hot Water** – We diagnose and fix heating system failures.
- **Blocked Drains & Toilets** – Swift solutions to prevent overflow and backups.

🚀 **Don't wait—call Jaws Gas Services for emergency plumbing now!**

---

#### **🔹 Professional Boiler Installation in Scotland**
At **Superior Heat Solutions**, we provide **top-quality boiler installation** services throughout Scotland. Whether you're replacing an old unit or installing a brand-new system, we have the expertise to **fit high-efficiency A-rated boilers** from top manufacturers.

### **Why Choose Us for Your Boiler Installation?**
🔥 **Expert Installation:** We fit combi, system, and conventional boilers.
🔥 **Affordable Pricing:** Competitive rates with flexible finance options.
🔥 **Energy Efficiency:** Save on heating bills with our A-rated systems.
🔥 **Hassle-Free Process:** From selection to installation, we handle everything.

🚀 **Upgrade your heating today—book a free consultation!**

---

### **🔹 Power Flushing Service in Exeter**
Does your heating system take too long to warm up? Our **power flushing service** removes sludge, rust, and debris to restore your **radiators’ efficiency**.

### **Benefits of Power Flushing:**
💧 **Improved Heat Distribution:** Say goodbye to cold spots in your home.
💧 **Lower Energy Bills:** A cleaner system runs more efficiently.
💧 **Prevents Boiler Damage:** Extends the life of your heating system.

**Starting from just £300**—get in touch today to book your power flush!

---

### **Now, refine the following service page content into a highly detailed, structured, and persuasive version like the examples above:**

{state["service_page"].content}

**Make sure to:**
- Expand the details of each section.
- Use structured headings and subheadings.
- Improve the **clarity, engagement, and persuasiveness** of the content.
- Include **strong call-to-action statements**.
- Ensure **SEO optimization** with natural keyword integration.
- Not Mention any location.
- All the data shown in a pargraph.

Provide the refined content in a **well-formatted and professional** manner.
Not give any code and html tags.

         """,

"individual_service_page": f"""
Your **task** is to **rewrite and refine** the given service page content while ensuring that it follows the diverse structures, tones, and formatting of the provided examples.

### **Instructions**
- Carefully **analyze the example service pages**—each subservice follows a unique structure.
- **Do not copy or mix example content into the final output.** The provided examples are for structure reference only.
- **Do not use bullet points** or repetitive templates. Instead, ensure the content is presented in well-structured paragraphs.
- Keep the writing **clear, professional, and SEO-friendly**, optimizing for readability and engagement.
- Structure the content with **logical transitions** between sections while maintaining a natural, narrative flow.
Is there name use of company name used this name {company_name}.
Not add any specific area in the content and not add colon in the center of the sentence.

---

### **Example Formats of Well-Structured Service Pages**
The following examples are for structure reference only. **Do not mix their content into the final response.**

#### **Example 1:
Oil Boilers Page**
- Trusted Oil Boiler Installation Experts

  At South Coast Plumbing and Heating, we specialise in installing high-quality oil boilers. With years of expertise, we are committed to providing exceptional service to our valued customers across Devon.

- What Are Oil Boilers?

  Oil boilers are reliable and efficient heating solutions for properties not connected to the gas grid. They burn heating oil to provide heat and hot water, making them ideal for rural homes and businesses. Modern oil boilers are designed to be energy-efficient, helping to reduce fuel costs and environmental impact.
  The lifespan of an oil boiler typically ranges between 15 to 20 years, depending on regular maintenance and servicing. By investing in a high-quality boiler and ensuring it is properly maintained, you can enjoy consistent heating and hot water for many years to come.

- Ask Us About Fitting your New Oil Boiler

  We understand that every property is unique, so we offer tailored solutions to meet your heating needs. Whether you’re replacing an old boiler or installing a new one, you can trust us to get the job done efficiently and to the highest standard.
  Ready to upgrade your heating system? Get in touch with South Coast Plumbing and Heating for a free quote. Let us help you stay warm and comfortable all year round!


---

#### **Boiler Servicing Funnel Text**
- Online Booking For Boiler Services

  An annual boiler service is essential to keep your boiler running smoothly all year. Regular maintenance is also usually required to maintain warranties and help prevent system breakdowns. Book us, your local boiler and heating team, for your annual boiler service in Exeter, Exmouth, Newton Abbot, Honiton, and Cullompton.

- Service Your Boiler Annually

  An annual maintenance check for your boiler is essential. A knowledgeable gas engineer can regularly service your central heating and avoid potential risks like carbon monoxide poisoning, gas leaks, explosions, and fires.
  Corrosion and boiler faults can be spotted early before they cause a boiler breakdown. Prevention is better than cure, and regular boiler maintenance can help stop costly breakdowns and repairs in the future. Our engineers will point out any weaknesses so you can plan and budget for a repair before it becomes an issue.

- Keep Your Boiler Warranty Valid

  To keep your boiler warranty valid, annual servicing must be completed by a qualified engineer. Our team is qualified and approved to service gas and oil boilers - you can trust us for all your heating solutions. Don’t lose out - keep your manufacturer’s warranty up to date by calling us for a service every 12 months.

---
#### **Boiler Repairs Funnel Text**

- No Heating Or Hot Water?
  Our skilled gas engineers are equipped with the expertise and tools to diagnose and fix boiler, heating and hot water problems. With our prompt and reliable service, you can trust us to get your system up and running in no time. Broken down boilers are fixed properly, and often in a single visit when you use our local heating services.

- Broken Down Boilers Fixed

  A broken boiler can be a major inconvenience in your daily life, but at South Coast Plumbing and Heating in Exeter, we’re here to help. Our team of skilled gas engineers is equipped to handle any boiler repair, big or small.
  We understand the importance of fast boiler repair services, so we work quickly to diagnose and correct the problems. With our fast and efficient services, you'll have your boiler up and running in no time.

- Boiler Stopped Working? We Can Help!

  Our team has years of experience repairing central heating and boilers, and we have seen most of the problems that occur.
  -       Boiler leaks
  -       No heating
  -       Cold radiators
  -       No hot water
  -       Low gas pressure
  -       Broken controls
  -       Timer not working
  -       Non-firing boiler
  -       Boiler fault codes

  These are all common faults that we repair immediately, but if you have other issues with your boiler, don’t hesitate to call us. We repair boilers in Exeter, Exmouth, Newton Abbot, Cullompton and Honiton.
---
#### **Example 2:
New Boiler Page**
- A New Boiler At A Great Price

  Oil boilers are designed to be robust and durable. Often, they can last for up to 15 years, or even longer if they are well maintained. However, there will come a point in every oil boiler’s life when it stops functioning as it should and therefore needs to be replaced.
  If your gas boiler is more than 12 years old or no longer works reliably, it’s probably time to consider replacing it with a new model. Our dedicated team of fully certified experts are on hand to assist you. We can install a new, energy-efficient, cost-effective boiler for your home for a fixed-rate.
  We are happy to help with your boiler installation throughout the entire process, from choosing a new boiler to fitting everything you need. Our simple three-step consultation process ensures that we can answer your queries and provide a fixed-rate quote conveniently.
- Oil To Gas Conversion

  Get rid of your oil boiler and convert to gas central heating - we are available to complete the conversion in the Belfast area. There are many advantages to converting from oil to gas, one of main advantages is having instant hot water when changing to a gas-combi boiler system. Here are a few other advantages:
    - No need for an oil tank; we will remove it
    - Your inefficient oil boiler will be replaced by an energy-efficient gas model
    - Stored water is no longer required, so we remove the hot water cylinder
    - Your cold water storage tank is also no longer needed; you gain valuable space
    - Have complete control over your heating system with optional smart controls
    - Monthly energy bills will be lower
    - Oil leaks and oil theft are no longer a risk

- What to Expect From an Oil to Gas Conversion

  With over 17 years’ experience in oil to gas conversions, our engineers have a wealth of experience to meet any challenges that might arise when completing the conversion.
  Most oil to gas conversions take around two days (we don’t like to rush).This is adequate time to ensure that the job is completed to the highest possible standard. Our experience and attention to detail is why Reid Energy Solutions has earned a first-rate reputation.
---
#### **Boiler Servicing Page**
- Maintain your Boiler With Annual Servicing

  Our annual boiler service will help keep your boiler working efficiently all year round. Your boiler is in good hands when you book us to maintain your hot water and heating system. Our team of engineers service boilers in Belfast and the surrounding areas. Make sure your heating is safe, efficient and reliable by choosing us to service your boiler.

- Why Servicing Your Boiler is Essential

  Booking an annual service for your boiler keeps your home and loved ones safe. Potential risks like carbon monoxide poisoning, oil or gas leaks and fires can be avoided when a knowledgeable heating engineer regularly checks your central heating. We all rely on our heating systems to keep supplying warmth and hot water every day, so a maintenance check every 12 months is essential.
  Reduce the chance of needing an emergency callout in the winter. With a boiler service every 12 months, corrosion and potential faults can be spotted early before they cause a boiler breakdown. Our engineers will point out any weaknesses so you can plan and budget for a repair before they become an issue.

- Keep Your Boiler Warranty Valid

  New boilers come with a manufacturer’s warranty, but to keep it valid, annual servicing must be completed by a qualified engineer. The team at Reid Energy is qualified and approved for oil and gas boiler servicing - you can trust us for all your heating solutions. At the end of the service appointment, our engineers provide documentation as proof should you need it for your warranty.
  Don’t let things lapse by putting off the maintenance check; you can book your boiler service online! The price is fixed with no hidden surprises, and we will arrive as scheduled to maintain your boiler properly while providing peace of mind. We service boilers in Belfast, Comber, Killinchy, Newtownards and Lisburn.
---
#### **Boiler Repairs Page**
- Brokendown Boiler Repairs

  Is your heating not working? Our expert boiler repair service is here to quickly and effectively resolve any issues with your heating or hot water system. We offer boiler repairs in the Belfast, Comber, Killinchy, Newtownards and Lisburn areas.
  Our skilled oil and gas engineers are equipped with the knowledge and tools to diagnose and fix heating and hot water problems. With our prompt and reliable service, you can trust us to get your boiler up and running in no time.

- No Hot Water? We Can Help!

  The team at Reid Energy Solutions has years of experience repairing heating and boilers and has seen most of the problems that occur.
  -       Boiler leaks
  -       Cold radiators
  -       No water
  -       Low gas pressure
  -       Broken controls
  -       The timer not working
  -       Non-firing boiler

  These are all common faults that we repair straight away, but if you have other issues with your boiler, don’t hesitate to call us.

- Boilers Fixed Quickly
  We are confident we can get your boiler working properly again in no time. Our team is happy to fix boilers and has repaired combi, system and regular boilers with a variety of issues. We start by checking your boiler and heating carefully before identifying the fault. Once we have pinpointed the problem, we can let you know the cost of repairs and get to work quickly.
  Boilers sometimes develop faults that mean they aren’t working properly. Modern boilers often display a fault code, but if you’re not sure what to do next, we can rectify the issues and leave you with a boiler that runs properly again.

---

### **Now Rewrite and Refine the Following Service Page Content to Match the Structure Above**
- **Ensure each subservice has an appropriate heading**
- **Write in paragraphs, not bullet points**
- **Each subservice should follow a distinct structure, avoiding generic formatting**

#### **Content to Refine**
{state["individual_service_page"].content}

---

### **Pattern Checking and Content Validation**
**After rewriting the content, verify that**

1. **Each subservice has a distinct heading** clearly indicating the topic
2. **It follows a paragraph format** with smooth transitions between sections
3. **The structure varies appropriately** based on the closest relevant example
4. **There are no bullet points, lists, or repetitive templates**—everything is in natural, professional paragraphs
5. **The content remains engaging, SEO-optimized, and aligned with business website standards**
6. ** The content shown on a paragraph only shown those content which has two to three word so this content shown in a bullet point**

If the structure does not match the provided examples, **revise and refine it accordingly** to ensure **each subservice has its own unique format** while maintaining high-quality, professional writing.
 Not give any code and html tags.
""",

"service_area_page": f"""
Your task is to refine the content of the service area page for {state["service_area_page"].content}.
Use the provided example to ensure **consistency in structure, clarity, and professional tone** while making each service area unique.

**⚠️ IMPORTANT:**
👉 **DO NOT include any introduction, explanation, or summary before the refined content.**
👉 Start directly with the refined service area pages.
👉 **Each service area must have unique headings** while maintaining the same subservices.
👉 **Headings must NOT contain any punctuation (e.g., no commas, periods, or exclamation marks).**

### **Few-Shot Example:**
#### **Example: Service Areas with the Same Subservices but Unique Headings**

✅ **Exeter**
- **Heating Solutions for Exeter Homes**
  Whether you need a **new boiler, central heating installation, power flushing service, or boiler repair**, our **Gas Safe engineers** ensure your home stays warm and comfortable. **South Coast Plumbing and Heating** provides a **full range of heating services** in Exeter, covering **Natural Gas and oil boilers**.

- **Energy Efficient Boiler Installation Exeter**
  Looking for an **energy-efficient boiler upgrade** in Exeter? We **supply and install A-rated gas and oil boilers** from leading manufacturers. Our skilled heating engineers help you choose the **best replacement boiler** for your home. **Get an online quote** today for a high-performance boiler that reduces energy costs.

- **Reliable Boiler Servicing Exeter Homes**
  Routine maintenance is key to keeping your boiler in **top condition**. Our team provides **annual servicing** across Exeter, ensuring safety, efficiency, and early detection of any issues. **Regular servicing** extends your boiler’s lifespan and helps maintain your warranty.

---

✅ **Exmouth**
- **Trusted Heating Experts Exmouth**
  If you’re in Exmouth and need a **new boiler, central heating installation, power flushing, or boiler repair**, our **Gas Safe engineers** are ready to assist. **South Coast Plumbing and Heating** serves Exmouth, offering **expert heating solutions** for both **Natural Gas and oil boilers**.

- **High Performance Boiler Installation Exmouth**
  Planning to **upgrade to an A-rated boiler** in Exmouth? We install **high-efficiency boilers** from trusted manufacturers. Our specialists guide you in selecting the **perfect boiler** for your home, ensuring **maximum energy savings**. **Request an online quote** today.

- **Annual Boiler Checkups Exmouth**
  Keep your boiler running **safely and efficiently** with our **annual servicing** in Exmouth. Our team conducts a **detailed inspection** to prevent costly repairs and extend your boiler’s lifespan. Book your **boiler service in Exmouth** today.

### **Guidelines for Refinement:**
🔹 **Follow the Format:** Each service area should have structured sections like the example, including a location-based heading, service highlights, and a clear description.
🔹 **Unique Headings for Each Service Area:** Ensure **headings are different** for each location while keeping subservices the same. **Avoid using the same title structure across all locations.**
🔹 **No Punctuation in Headings:** Headings **must not contain any punctuation** (e.g., no commas, periods, or exclamation marks).
🔹 **Consistency with Readability:** Maintain **bullet points, concise descriptions, and proper formatting** for clarity.
🔹 **Location-Specific Details:** Make sure each section sounds **tailored to the specific area** while keeping **the core service offerings consistent**.

🚀 **Final Output Format:**
✅ No unnecessary introduction or explanation
✅ Starts directly with the **first service area**
✅ Uses **unique headings without punctuation**
✅ Ensures **professional, structured, and readable content**
 Not give any code and html tags.
"""

    }
    pages = {
        key: llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]).content.strip()
        for key, prompt in prompts.items()
    }
    state.update(pages)
    print("refine_done")
    return state

def evaluate_content_quality(state: ContentState) -> ContentState:
    """Evaluates content quality, ensuring fair scoring that reflects real improvements."""
    previous_score = state.get("quality_score", None)  # Get previous score if available
  # Get previous score if available

    prompt = f"""
    ### **Strict Content Quality Evaluation (NO Guesswork Allowed)**
    You are a **highly strict but fair content evaluator**. Your job is to **accurately measure quality improvements** and ensure a logical score adjustment.

    ---

    ### **🚨 VERY IMPORTANT – STRICT RULES 🚨**
    - **You MUST compare the content to its previous version.** If no prior version is available, evaluate as usual.
    - **If improvements have been made, the score should increase.** If the score stays the same or drops, you must justify why.
    - **DO NOT suggest changes unrelated to the provided content.** No hallucinations about missing videos, testimonials, or interactive elements.
    - **All feedback must be content-based, fact-driven, and specific.**
    - **You MUST provide at least 5 unique, real improvement areas**—no generic feedback.
    ---
    ### **Evaluation Criteria (Be Critical, But Only on Real Issues)**
    1. **Readability & Flow** – Does the content read smoothly and professionally?
    2. **Logical Structure & Clarity** – Is the content well-structured with clear headings and transitions?
    3. **Depth & Relevance** – Does it provide unique insights and valuable details?
    4. **SEO Optimization** – Are keywords well-integrated and formatting SEO-friendly?
    5. **Accuracy & Credibility** – Are all claims factually correct, with no vague statements?
    6. **Persuasiveness & CTA Strength** – Are the calls to action compelling?
    7. **Spelling & Language Precision** – Any typos or awkward phrasing?

    ---

    ### **Scoring System (Adjust Fairly Based on Changes)**
    - **0-3: Unacceptable** – Major issues. Needs total rewrite.
    - **4-6: Below Average** – Needs significant work before being usable.
    - **7: Average** – Acceptable, but **lacks refinement**.
    - **8: Above Average** – Good, but **not quite premium quality**.
    - **9: Almost There** – High quality, **minor refinements needed**.
    - **10: Perfect** – **Extremely rare.** Must be **flawless and highly persuasive**.

    ---

    ### **Content to Evaluate:**
    ```
    {state["home_page"]}
    {state["about_us_page"]}
    {state["service_page"]}
    {state["individual_service_page"]}
    {state["service_area_page"]}
    ```

    ---

    ### **Final Output Format (STRICTLY FOLLOW THIS)**
    **Quality Score: X/10**
    **Reason for Score (MUST justify if score drops or stays the same):**
    - **[Short but detailed explanation]**
    **Key Areas to Improve (MUST list 5+ real, unique issues):**
    - **[Issue 1]**
    - **[Issue 2]**
    - **[Issue 3]**
    - **[Issue 4]**
    - **[Issue 5]**

    **If the score does NOT increase, explicitly state why.**
    """

    response = llm.invoke(prompt)
    output = response.content

    # Extract the score from the response
    try:
        score_line = [line for line in output.split("\n") if "Quality Score" in line][0]
        score = int(score_line.split(":")[-1].strip().split("/")[0])
    except (IndexError, ValueError):
        score = 0  # Default to 0 if parsing fails

    # Extract feedback
    improvement_lines = []
    capture = False
    for line in output.split("\n"):
        if "Key Areas to Improve" in line:
            capture = True
            continue
        if capture and line.strip():
            improvement_lines.append(line.strip())

    improvements = "\n".join(improvement_lines) if improvement_lines else "No major weaknesses found."

    # **Fix Score Inconsistency: Force Justification**
    if previous_score is not None and score < previous_score:
        print("\n🚨 **Warning:** The score decreased! Checking for justification... 🚨")
        if "explicitly state why" not in output:
            print("⚠️ No valid reason for lowering the score. Reverting to previous score.")
            score = previous_score  # Prevent unfair decreases

    # Print Feedback
    print(f"\n=== Quality Evaluation ===")
    print(f"Content Quality Score: {score}/10")
    print(f"Key Areas to Improve:\n{improvements}\n")

    # Update State
    state["quality_score"] = score
    state["feedback"] = improvements

    return state
def feedback_improvement(state: ContentState) -> ContentState:
    feedback = state["feedback"]
    previous_score = state["quality_score"]

    # Previous versions of all pages
    previous_home_page = state["home_page"]
    previous_about_us = state["about_us_page"]
    previous_service_page = state["service_page"]
    previous_individual_service_page = state["individual_service_page"]
    previous_service_area_page = state["service_area_page"]

    # Adjusted prompts for refining content
    prompts = {
        "refine_home_page_content": f"""
You are a **senior UK-based content strategist and conversion copywriter**. Your task is to **significantly enhance the quality of the given content** by addressing every issue mentioned in the feedback. Your goal is to **maximize the quality score (Currently: {previous_score})**.

### **🚀 Critical Directives (Must Follow)**
✅ **Aggressively fix ALL Issues Highlighted in Feedback (No Exceptions)**
✅ **Enhance Structure, Readability, and Persuasiveness with Concrete Improvements**
✅ **Ensure High SEO Optimization & Conversion-Driven Writing**
✅ **Use More Engaging, Clear, and Action-Oriented Language**
✅ **Ensure the new version is drastically better than the previous one**

### **❌ Common Mistakes to Avoid**
🚫 **DO NOT return content that is too similar to the original**  
🚫 **DO NOT simply rephrase—fully transform weak sections**  
🚫 **DO NOT ignore any issues in feedback**  
🚫 **DO NOT include explanations, commentary, HTML tags, or code**

---

### **🔍 Issues in the Previous Version (MUST BE FIXED):**
{feedback}

### **📜 Previous Version (Revise & Improve):**
{previous_home_page}

🔹 **Your rewrite must show a noticeable, measurable improvement over the previous version. If it does not, the quality score will remain the same. Not give any code and html tags.**
""",

"refine_about_us_content": f"""
You are a **senior UK-based content strategist and conversion copywriter**. Your mission is to **aggressively refine and enhance** the About Us content to make it **more engaging, trustworthy, and conversion-driven**.

### **🚀 Mandatory Improvements**
✅ **Fully Address Every Issue Highlighted in the Feedback**  
✅ **Strengthen Brand Storytelling & Emotional Appeal**  
✅ **Improve Readability, Flow, and Clarity**  
✅ **Ensure SEO Optimization & Persuasive Copywriting**  
✅ **Significantly Increase the Quality Score (Currently: {previous_score})**

### **❌ Avoid These Mistakes**
🚫 **Do NOT return content that is too similar to the original**  
🚫 **Do NOT just rephrase—fully transform weak sections**  
🚫 **Do NOT ignore any feedback points**  
🚫 **Do NOT include explanations, commentary, HTML tags, or code**  

---

### **🔍 Issues in the Previous Version (MUST BE FIXED):**
{feedback}

### **📜 Previous Version (Rewrite & Improve):**
{previous_about_us}

🔹 **Your rewrite must demonstrate a measurable improvement. If it does not, the quality score will remain the same. Not give any code and html tags.**
""",


        "refine_service_page_content": f"""
You are a **senior UK-based content strategist and SEO specialist**. Your mission is to **completely refine and optimize** the Service Page content to make it **highly engaging, persuasive, and conversion-focused**.

### **🚀 Critical Directives (Must Follow)**
✅ **Fix ALL Issues Highlighted in the Feedback Below (No Exceptions)**  
✅ **Make Service Descriptions More Engaging & Benefit-Driven**  
✅ **Improve Readability, Clarity, and SEO Optimization**  
✅ **Strengthen CTAs & User Engagement**  
✅ **Increase the Quality Score (Currently: {previous_score})**  

### **❌ Common Mistakes to Avoid**
🚫 **DO NOT return a slightly modified version—Make Drastic Improvements**  
🚫 **DO NOT just rephrase—fully transform weak sections**  
🚫 **DO NOT ignore any feedback points**  
🚫 **DO NOT include explanations, commentary, HTML tags, or code**  

---

### **🔍 Issues in the Previous Version (MUST BE FIXED):**
{feedback}

### **📜 Previous Service Page Content (Rewrite & Improve):**
{previous_service_page}

🔹 **Your rewrite must demonstrate a measurable improvement. If it does not, the quality score will remain the same. Not give any code and html tags.**
""",

       "refine_individual_service_page_content": f"""
You are a **senior UK-based content strategist and SEO specialist**. Your task is to **significantly enhance the quality of the individual service page content** by making it **clear, persuasive, and highly optimized for conversions**.

### **🚀 Key Objectives**
✅ **Address Every Issue Highlighted in the Feedback Below**  
✅ **Improve Service Descriptions for Maximum Clarity & Persuasion**  
✅ **Enhance Readability, Engagement, and SEO Performance**  
✅ **Strengthen Call-to-Actions (CTAs) to Drive More Conversions**  
✅ **Ensure a Noticeable Quality Score Increase (Currently: {previous_score})**  

### **❌ Strict Guidelines**
🚫 **DO NOT submit a version that is too similar to the original**  
🚫 **DO NOT just rephrase—fully transform weak sections**  
🚫 **DO NOT ignore any feedback points**  
🚫 **DO NOT include explanations, commentary, HTML tags, or code**  

---

### **🔍 Issues in the Previous Version (MUST BE FIXED):**
{feedback}

### **📜 Previous Individual Service Page Content (Rewrite & Improve):**
{previous_individual_service_page}

🔹 **Your rewrite must demonstrate a measurable improvement. If it does not, the quality score will remain the same. Not give any code and html tags.**
""",


       "refine_service_area_page_content": f"""
You are a **senior UK-based content strategist and SEO specialist**. Your job is to **significantly enhance the quality of the service area page content**, ensuring it is **engaging, location-optimized, and highly persuasive**.

### **🚀 Must-Have Improvements**
✅ **Fix ALL Issues Highlighted in the Feedback Below**  
✅ **Enhance Structure, Readability, and Persuasiveness**  
✅ **Improve Location-Specific Optimization for SEO**  
✅ **Strengthen CTAs & User Engagement**  
✅ **Ensure a Noticeable Quality Score Increase (Currently: {previous_score})**  

### **❌ Strict Rules**
🚫 **DO NOT submit a version that is too similar to the original**  
🚫 **DO NOT just rephrase—fully transform weak sections**  
🚫 **DO NOT ignore any feedback points**  
🚫 **DO NOT include explanations, commentary, HTML tags, or code**  

---

### **🔍 Issues in the Previous Version (MUST BE FIXED):**
{feedback}

### **📜 Previous Service Area Page Content (Rewrite & Improve):**
{previous_service_area_page}

🔹 **Your rewrite must demonstrate a measurable improvement. If it does not, the quality score will remain the same. Not give any code and html tags.**
""",

    }

    # Invoke LLM for refinement on all pages
    refined_pages = {
    key: llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]).content.strip()
    for key, prompt in prompts.items()
    }
    # Update state with refined content
    state.update({
        "home_page": refined_pages["refine_home_page_content"],
        "about_us_page": refined_pages["refine_about_us_content"],
        "service_page": refined_pages["refine_service_page_content"],
        "individual_service_page": refined_pages["refine_individual_service_page_content"],
        "service_area_page": refined_pages["refine_service_area_page_content"],
    })

    return state

def upload_file(state: ContentState) -> ContentState:
  file_path= state["file_path"]
  print(file_path)
# Load the document
  doc = Document(file_path)

  # Read and print the content
  text = "\n".join([para.text for para in doc.paragraphs])
  print("upload done")
  return {"text": text}

def meeting_insights(state: ContentState) -> ContentState:
  data=state["text"]
  prompt = f"""
### Role:
You are an expert **Website Content Analyst** specializing in extracting relevant information from meeting transcripts. Your job is to analyze the provided transcript, identify key discussions about website content, and present only the most useful insights.

### Task:
Process the transcript and extract essential details **directly contributing to website content creation**, while ignoring unrelated discussions, small talk, and general meeting logistics.

### Responsibilities:
1. **Understand Website Goals** – Identify the client's main objectives and purpose for the website.
2. **Define Site Structure** – Extract discussed pages, sections, and overall navigation flow.
3. **Summarize Content Strategy** – Capture insights about content types (text, images, blogs, videos, FAQs).
4. **Extract Branding & Design Preferences** – Note colors, typography, branding elements, and overall visual style.
5. **Identify Functional & Interactive Elements** – List features like forms, integrations, buttons, and CTAs.
6. **Analyze Target Audience & Messaging** – Understand the audience and tone/style of communication.

### Guidelines:
- Strictly **filter out** unrelated discussions, filler words, or non-essential details.
- Focus on **clear, actionable insights** for content development.
- Present the extracted information in a structured, professional format.

### Input Transcript:
{data}

### Optimized Output:
Provide a structured summary with only the **necessary insights** that contribute to website content creation.
"""

  response = llm.invoke(prompt)
  meeting_point = response.content
  print("insights done",meeting_point)
  return {"meeting_point": meeting_point}