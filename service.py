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
            "home_page": f"""You are an expert web content writer specializing in **on page SEO-optimized, high-converting website copy**. Your task is to write a compelling **Home Page** for a company named **{company_name}**, which provides **{services}**. Your writing should be persuasive, well-structured, and engaging while maintaining a clear, informative and marketing tone.

              ### **Key Requirements:**

              #### **1. Engaging Headline & Subheadline:**
              - Create a powerful, attention-grabbing **headline** that highlights the company’s expertise and core offering.
              - Follow with a **subheadline** that builds trust and credibility while reinforcing key benefits.

              #### **2. Strong Introduction (First 2-3 Sentences Must Hook the Reader):**
              - Clearly introduce the company, its specialization, and the core services.
              - Ensure the tone is professional yet friendly to build trust and engagement.

              #### **3. Service Sections (Well-Structured & Persuasive):**
              - **Break down key services** (**{services_list}**) into well-defined sections.
              - Make the perfect heading which clarify the service and addition some words to make serviceattractive.
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

              #### **6. **Why Choose Us?**
              - Emphasize what sets the company apart (e.g., 24/7 availability, warranties, financing options, and add other which give plus points).
              - Reinforce a **customer-first approach**, focusing on transparency, trust, and superior service.

              #### **7. Call to Action (Drives Conversions):**
              - End with a **strong, action-oriented CTA**, such as:
                - “Get a Free Quote Today – Call Now!”
                - “Book Your Boiler Installation in Just 24 Hours!”
              - Encourage urgency and easy next steps.

              #### **8. On page SEO Optimization (Ensures Visibility):**
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
            "about_us_page": f"""You are an expert web content writer skilled in crafting **clear, engaging, and customer-focused About Us pages**.  

### **Task:**  
Write a **concise, natural-sounding About Us page** for **{company_name}**, a trusted provider of **{services}**. The content must:  
✅ **Be engaging and professional** while maintaining a friendly, approachable tone.  
✅ **Strictly follow the provided structure and formatting.**  
✅ **Not add extra sections** (e.g., "Why Choose Us").  
✅ **List services and areas covered in bullet points ONLY—no additional descriptions.**  

---

### **Content & Structure Requirements:**  

#### **1. Introduction (Who We Are & What We Do)**  
- Begin with a **concise, engaging introduction** that:  
  - Highlights **experience, expertise, and service reliability**.  
  - Mentions **years in business, qualifications, and key services**.  
  - Reinforces commitment to **quality, integrity, and customer satisfaction**.  
  - Uses a **conversational yet professional tone** for readability.  

#### **2. Company Commitment & Approach**  
- Briefly explain the company’s **dedication to high standards**:  
  - Reliable, affordable, and professional service.  
  - Customer-first approach with a focus on long-term relationships.  
  - Tailored solutions to meet individual client needs.  

#### **3. Our Services (Bullet Points Only – No Extra Details)**  
- List **ONLY** the services exactly as provided in `{services_list}`:  
  - **No modifications, explanations, or additional details.**  
  - **Example format:**  

  {services_list}  

#### **4. Areas We Cover (Bullet Points Only – No Extra Details)**  
- Display **ONLY** the locations exactly as provided in `{service_area}`:  
  - Maintain formatting and **do not split multi-word locations**.  
  - **Example format:**  

  {service_area}  

#### **5. Call to Action (Encouraging Customer Engagement)**  
- Conclude with a **concise, compelling CTA**, such as:  
  - **"For expert {services}, contact {company_name} today!"**  
  - **"Need emergency plumbing? We're here when you need us most—get in touch now."**  

---

### **Final Output Must:**  
✔️ **Follow this structure exactly** (no extra sections).  
✔️ **Match a natural, conversational yet professional tone** (see example style).  
✔️ **List services & areas strictly in bullet points—no descriptions.**  
✔️ **Keep content concise, clear, and customer-friendly.**  

❗ **DO NOT provide code or HTML tags.**  

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
        "home_page": f"""You are an expert UK-based web content editor. Your task is to **refine and enhance** the following **Home Page Content** to match the structure, style, and detail level of top-tier UK service websites. Ensure the content is **well-organised, highly detailed, and professionally formatted.**

---
### **Few-Shot Examples of Ideal UK-Specific Structure & Style**

#### **Example 1**
### Exeter’s Heating Experts
#### Local Gas Boiler Installations & Heating Services

**New and Replacement Boilers Fitted**
At South Coast Plumbing and Heating, we specialise in fitting new combi, traditional and system boilers. Trust us to install the latest **A-rated boilers** from Viessmann—a brand known for **reliability and durability**. Need an **emergency, same-day boiler installation**? We’ve got you covered. Plus, choose us for your replacement boiler, and we’ll install a **smart thermostat free of charge!**

**Experienced Boiler Engineers**
All our engineers are **Gas Safe Registered** and **City & Guilds qualified**, bringing over **40 years of combined industry experience**. We promptly answer every customer query—no long waits, just **reliable service**.

**Air-Source Heat Pump Installers**
Switch to a more **energy-efficient heating solution** with an **Air Source Heat Pump (ASHP)**. These systems offer **sustainable, year-round comfort** while reducing energy costs. Interested in **renewable heating**? Ask us about fitting an **air-source heat pump** in your Exeter home.

**Book Your Annual Boiler Servicing**
Our boiler servicing ensures **safety and efficiency** by checking for leaks, corrosion, and early signs of wear. We recommend an **annual service** to prevent breakdowns and keep your heating system running **smoothly all year round**.

**Why Choose Us for Your Exeter Heating Needs?**

✅ **Next-Day Boiler Installation**
Need a boiler replacement fast? We can install a new boiler **within 24 hours** across Exeter, Exmouth, Teignmouth, and Taunton.

✅ **Local Devon-Based Plumbers**
We’re a **local Exeter business**, meaning we’re always nearby when you need us.

✅ **Highly Experienced Gas Engineers**
With **40+ years of expertise**, we ensure top-tier heating solutions. All engineers are **Gas Safe Registered**.

✅ **Available 7 Days a Week**
We’re open when you need us—weekdays or weekends.

✅ **Free Smart Thermostat**
Upgrade your heating efficiency—get a **free smart thermostat** when we install your new boiler.

✅ **Great Warranties**
Our **affordable A-rated boilers** come with warranties of **up to 10 years** for select models.

---
#### **Example 2**
### Exeter Boiler Experts
#### Local Gas Boiler Installations & Heating Services

**New and Replacement Boilers Fitted**
At South Coast Plumbing and Heating, we specialise in installing **combi, traditional, and system boilers**. We fit **A-rated Viessmann boilers**, known for their **durability and reliability**. Need an **urgent boiler replacement**? We offer **same-day installations**. Plus, every new boiler installation includes a **free smart thermostat** for added energy savings.

**Experienced Boiler Engineers**
Our **Gas Safe Registered** engineers have **over 40 years of combined industry experience**. We provide a **fast, responsive service**—no unanswered calls or long waits.

**Book Your Annual Boiler Servicing**
Regular boiler servicing prevents **breakdowns and efficiency loss**. We perform **comprehensive checks** to ensure **your heating system remains in top condition** year-round.

**Air-Source Heat Pump Installers**
Considering **renewable heating**? **Air Source Heat Pumps** offer an **energy-efficient alternative** to gas boilers. Our **expert installers** can help you switch to a **sustainable home heating solution**.

**Why Choose Us?**

✅ **Fast Boiler Installations** – Next-day service available.
✅ **Local Experts** – Exeter-based plumbers & engineers.
✅ **40+ Years of Experience** – Trusted industry professionals.
✅ **Weekend & Emergency Availability** – We work when you need us.
✅ **Free Smart Thermostat** – Added value with every new boiler.
✅ **Up to 10-Year Warranties** – Quality boilers with long-term protection.

---
### **📌 Refinement Instructions (UK-Specific & Highly Detailed)**

✅ **Enhance Detail & Professionalism** – Ensure the content is **highly structured, informative, and engaging**.
✅ **Use UK Spelling & Terminology** – Maintain UK-specific language, including terms like **Gas Safe, A-rated boilers, VAT, CP12 certificates, Smart Thermostats, and 10-Year Warranties**.
✅ **UK City Names Only** – Do not use non-UK cities in location references.
✅ **Improve Readability** – Use **clear headings, bullet points, and short paragraphs** to enhance user experience.
✅ **SEO-Optimised But Natural** – Incorporate **relevant keywords organically**, ensuring the content reads naturally while supporting search visibility.
✅ **Highlight Benefits & Trustworthiness** – Clearly communicate **why customers should choose this company**, emphasising **guarantees, response times, expert knowledge, and certifications**.
✅ **UK Market-Specific Content** – Adapt pricing models, service expectations, and industry standards to align with UK consumer preferences.
✅ **Maintain Original Punctuation** – **Do NOT** alter punctuation or symbols. Preserve the original structure exactly.
✅ **Avoid Unnecessary Colons** – Do not insert colons mid-sentence where unnecessary.

---
### **NOW, Refine the Following Home Page Content Using These Standards:**

{state["home_page"].content}

---
**Deliver the final content in a fully structured, detailed, and polished format, ensuring it aligns with top-tier UK service websites.**
Refine the content according to the examples.
""",
"about_us_page": f""" You are an expert UK-based web content editor. Your task is to refine the following **About Us Page Content** to match the structure, style, and detail level of top-tier UK service websites. Ensure the content is **well-organised, highly detailed, and professionally formatted.**.
        ---
        ### **Few-Shot Examples of Desired Structure (UK-Specific, Highly Detailed)**

        #### **Example 1 
         About Us Page
           South Coast Plumbing and Heating is a trusted team of experienced plumbers and Gas Safe-registered engineers based in Exeter, Devon. With over 20 years of industry expertise, we proudly serve both domestic and commercial clients, offering new oil and gas boiler installations, boiler repairs, boiler servicing and system power flushing across Devon. When it comes to renewable energy heating, we install the latest air-source heat pumps for homes in our local area. 
           We are committed to delivering high-quality plumbing and heating solutions with a focus on honesty, integrity and exceptional workmanship. Our goal is to build lasting relationships with our clients by providing reliable, affordable and professional services tailored to their needs.
           At South Coast Plumbing and Heating, we take pride in our work, ensuring every project is completed to the highest standard. Our personalised approach sets us apart, allowing us to offer bespoke solutions that meet every customer’s unique requirements.
           For 24/7 emergency plumbing services in Exeter, we’re here when you need us most. Contact us today to learn more about our efficient and cost-effective boiler installations.

           **Our services include:** 
             - New gas boilers
             - New oil boilers
             - Boiler repairs
             - Boiler servicing
             - New central heating installations
             - Power flushing
             - Unvented cylinders
             - Air source heat pumps
             - Commercial heating solutions
             - Emergency plumbing
             - General plumbing services
             - Commercial plumbing services
           **Areas we cover:**
             - Exmouth
             - Newton Abbot
             - Teignmouth
             - Taunton
             - Cullompton
             - Honiton
             And the surrounding areas

        ---

        #### **Example 2 **
          About Us Page
             Humber Homes Heating was established in early 2022 by directors Jason and Dan, who collectively bring over 25 years of industry experience. As a growing company, our mission is to become the number one heating provider in Lincolnshire. We pride ourselves on delivering exceptional service tailored to the unique needs of our clients.
             Our commitment to quality means that we offer competitive pricing while ensuring that every job meets our high standards. Whether it’s a routine maintenance check, a new boiler installation, or emergency repairs, we are dedicated to providing reliable solutions that keep your home comfortable year-round.
             We believe in building lasting relationships with our customers, based on trust and transparency. Your satisfaction is our priority, and we are here to guide you through every step of your heating project.
             Contact us today to discuss how we can bring your heating vision to life. We look forward to hearing from you.

                 . Lincoln
                 . Hull
                 . Scunthorpe
                 . Cleethorpes
                 . Grimsby
                 . Doncaster
                 . And the surrounding areas
        #### **Example 3**
        About Us
          At Jaws Gas Services Ltd, we provide the complete range of commercial, industrial and domestic gas, heating and plumbing services across Lancashire. The company was established in 2021, and includes a team of highly experienced and qualified gas engineers.
          Covering Lancashire and the North West, we handle jobs large and small with professionalism and efficiency. Visit our Yell profile for more details.

          Our services are comprehensive and include:

            . New boiler installation
            . Gas boiler servicing
            . Gas boiler repair
            . Oil boiler installations and maintenance
            . Central heating installation
            . Heating fault finding
            . General plumbing
            . Emergency plumbing
            . Power flushing service
            . Unvented cylinder installation
            . Commercial gas engineer services
            . Commercial heating and hot water
            . Catering and commercial kitchen installations

        ---



        ### **📌 Instructions for Refinement (UK-Specific, Highly Detailed & Professional):**
        ✅ **Enhance Detail & Professionalism:** The content should be **well-structured**, **clear**, and **engaging**.
        ✅ **Use UK Spelling & Terminology:** Ensure terms like **Gas Safe**, **A-rated boilers**, **VAT**, and **renewable energy** are included.
        ✅ **Improve Readability:** Use **clear headings**, **bullet points**, and **short paragraphs** for ease of reading.
        ✅ **Focus on Benefits & Trustworthiness:** Make sure to clearly outline **why customers should choose this company**, highlighting **experience, customer service, and certifications**.
        ✅ **Make it SEO-Friendly:** Integrate **relevant UK-based keywords** naturally into the content to improve SEO ranking without sacrificing readability.
        ✅ **Include Location Details & Coverage Areas:** Clearly specify the regions served, emphasizing the **local expertise** of the business.
       
        ---
        
        ### **NOW, Refine the Following About Us Content to Match These High-Detail Examples:**

        {state["about_us_page"].content}

        ---
        
        Return the improved **About Us Page** content in a **fully structured, highly detailed, and polished format** suitable for a professional UK service business website.""",

       "service_page": f"""You are an expert UK-based web content editor. Your task is to **refine the service page content** to make it more structured, detailed, and conversion-friendly.  

### **Instructions for Refinement:**  
- **Expand Each Section** – Provide **in-depth descriptions** of services, including their **benefits and processes**.  
- **Use Clear Headings & Subheadings** – Structure the content properly for **better readability and SEO**.  
- **Make the Content Flow Naturally in Paragraphs** – Ensure a **smooth, engaging, and persuasive tone** (NO bullet points).  
- **Incorporate Persuasive & Actionable Language** – Encourage visitors to **take action** (e.g., **"Get a Free Quote Today!"**).  
- **Ensure Natural Keyword Integration** – Optimize for **search engines** while keeping it human-friendly.  
- **DO NOT Mention Any Specific Locations.**  

---

### **Few-Shot Examples of Ideal UK-Specific Structure & Style**  

#### **Example 1 – Heating Services**  
**Heating Services**  
At South Coast Plumbing and Heating Ltd, we provide a comprehensive range of heating solutions tailored to meet the needs of homeowners and businesses. From new boiler installations to servicing and repairs, our expert team is committed to delivering reliable, high-quality workmanship. We take pride in offering honest, impartial advice and ensuring every project meets the highest standards.  

**New Gas Boilers Installed**  
Whether you need a combi boiler, a system boiler, or a traditional gas boiler, our skilled engineers provide seamless installation. If you’re replacing an outdated unit or relocating your boiler, we work closely with you to find the best solution that suits your home and budget.  

**Power Flushing Services**  
If your heating system is not working efficiently, a power flush can remove sludge and debris, restoring heat distribution and lowering energy costs. Our team uses advanced techniques to ensure your radiators and pipework are clean and performing at their best.  

---

#### **Example 2 – Plumbing Services**  
**Expert Plumbing Solutions**  
Our experienced team offers a full range of plumbing services, ensuring every job is completed to the highest standard. Whether you need a quick repair, a full system installation, or emergency assistance, we provide efficient and cost-effective solutions.  

**General Plumbing & Repairs**  
From fixing leaks to installing new pipework, our plumbers handle all general plumbing tasks with precision and care. Whether it’s a simple tap replacement or a full bathroom installation, we guarantee high-quality service at competitive prices.  

---

#### **Example 3 – Electrical Services**  
**Reliable Electrical Services for Homes & Businesses**  
Our expert electricians provide high-quality electrical services, ensuring safety, efficiency, and compliance with UK regulations. Whether you need a new wiring installation, an electrical inspection, or fault-finding services, we offer professional solutions tailored to your needs.  

**Lighting & Electrical Installations**  
Upgrade your home with modern lighting solutions designed for energy efficiency and style. Our team installs LED lighting, security systems, and custom electrical fittings, delivering high-performance results for residential and commercial properties.  

---

### **Now, refine the following service page content into a highly detailed, structured, and persuasive version like the examples above:**  

{state["service_page"].content}  

### **Make sure to:**  
✔ **Expand the details of each section** while maintaining a natural flow.  
✔ **Format everything in paragraphs ONLY** – **No bullet points**.  
✔ **Improve clarity, engagement, and persuasiveness**.  
✔ **Include strong call-to-action statements**.  
✔ **Ensure On-Page SEO optimization** with natural keyword integration.  
✔ **DO NOT mention specific locations** anywhere in the content.  
✔ **Maintain a professional and high-quality writing style.**  

❗ **DO NOT provide code or HTML tags.**  

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
    - **DO NOT suggest changes unrelated to the provided content.** No hallucinations, testimonials, or interactive elements.
    - **All feedback must be content-based, fact-driven, and specific.**
    - **You MUST provide at least 5 unique, real improvement areas**—no generic feedback.
    ---
    ### **Evaluation Criteria (Be Critical, But Only on Real Issues)**
    1. **Readability & Flow** – Does the content read smoothly and professionally?
    2. **Logical Structure & Clarity** – Is the content well-structured with clear headings and transitions?
    3. **Depth & Relevance** – Does it provide unique insights and valuable details?
    4. **On Page SEO Optimization** – Are keywords well-integrated and formatting SEO-friendly?
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