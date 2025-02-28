from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langgraph.graph import END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph
from typing import Dict, List
# ✅ Set Google Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyA6ks9hQCb29yaaEBs2XQXrPK86vrMhhG8"
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
    service_area_services: Dict[str, Dict[str, List[str]]]  # Each area has multiple sub-service pages


# ✅ Define Workflow
workflow = StateGraph(ContentState)

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
    return state

# ✅ Content Writing Task (Generates Home, About Us, and Service Pages)
def content_writing_task(state: ContentState) -> ContentState:
    research_data = state["research_data"]
    seo_data = state["seo_optimization"]
    services = "\n".join(f"- {service}" for service in state["services"])
    main_services = list(state["services"].keys())  # Extract main service names
    main_services_str = "\n".join(f"- {service}" for service in main_services)  # Format for readability

# Extract only subservices
    services_list = [
        subservice
        for main_service, subservices in state["services"].items()
        for subservice in subservices
    ]

# Convert to bullet points
    # services = "\n".join(f"- {sub}" for sub in services_list)
    service_area = "\n".join(f"- {area}" for area in state["service_area"])
    company_name=state["company_name"]
    service_area_services=state["service_area_services"]


    result = []
    for city, services in service_area_services.items():
        for value_list in services.values():
            for value in value_list:
                result.append((city, value))
    formatted_result = ""
    for city, services in service_area_services.items():
        subservices = "\n    ".join([value for value_list in services.values() for value in value_list])
        formatted_result += f"# **SERVICE AREA NAME `{city}`**\n    name of the subservices\n    {subservices}\n\n"

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
              - Emphasize what sets the company apart (e.g., 24/7 availability, warranties, financing options and add other which give plus).
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

              **Use the following research data for accuracy:**
              {research_data}

              **Apply these SEO best practices:**
              {seo_data}

              Ensure the content is persuasive, engaging, and easy to read. Keep paragraphs short and **use bullet points for clarity when needed**. Your writing should feel **professional yet approachable**, with a strong focus on **conversion and engagement**.
              please not provide a code and html tag.
              """,
"about_us_page": f"""You are an expert web content writer skilled in crafting **engaging, structured, and customer-focused About Us pages**.
                Write a professional and compelling **About Us** page for **{company_name}**, a trusted provider of **{services}**. The content must be well-structured, engaging, and clearly communicate the company’s mission, services, and coverage areas.

                ### **Key Requirements:**

                #### **1. Introduction (Who We Are & What We Do)**
                - Start with a strong, engaging introduction that:
                  - Establishes expertise and credibility.
                  - Mentions **years of experience, location, and key services**.
                  - Highlights the company’s commitment to **quality, customer satisfaction, and professional service**.
                  - Give in a detailed information about the company.

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

                #### **5. Call to Action (Encouraging Customer Engagement)**
                - End with a **clear and compelling CTA**, such as:
                - **"For expert services in {service_area}, contact us today!"**
                - **"Get in touch to schedule your consultation."**

                ### **Page Structure:**
                1. **About {company_name}** (Introduction)
                2. **Our Mission & Values** (Commitment to quality and customer satisfaction)
                3. **Our Services** (List services dynamically from `{services_list}`)
                4. **Areas We Cover** (List locations dynamically from `{service_area}`)
                5. **Contact Us** (Call to Action)

                Ensure the content is **concise, well-structured, and SEO-friendly**, using **bullet points** for readability and **natural keyword integration** for better search rankings.
                please not provide a code and html tag.
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
                - Each **main service** from `{main_services_str}` should be displayed as a heading add a (Page):
                  - **Format:** `## Main Service Name`
                - Each **subservice** from `{services}` should be listed under the correct **main service**:
                  - **Format:** `### Subservice Name`
                  - **Followed by a short description** explaining its benefits.
                - **Maintain the exact structure of main and subservices as provided.**

                #### **Example Format:**

                ## **Main service Page**
                At {company_name}, we provide expert solar panel installation services designed to maximize energy efficiency and savings. Our goal is to make solar energy accessible and affordable, ensuring that your home or business benefits from clean and sustainable power.

                ### **subservice1**
                Our professional team installs high-quality solar panels that are tailored to your property's needs. We assess your location, energy consumption, and budget to create an optimal solar solution that maximizes savings and efficiency.

                ### **subservice2**
                We provide comprehensive maintenance services to keep your solar system operating at peak performance. This includes panel inspections, cleaning, and system diagnostics to ensure longevity and efficiency.

                ### **subservice3**
                If your solar panels or inverters develop faults, our skilled technicians offer prompt repair services to restore functionality. Whether it's wiring issues, faulty components, or system inefficiencies, we quickly diagnose and fix the problem.

                ### **subservice4**
                Our solar consultation services include expert advice on the best solar solutions for your property. We conduct site evaluations, financial analysis, and system design planning to ensure that your investment yields the best results.

                and more if there are additional subservices...

                ---

                ## **Main service** Page
                Proper wiring ensures your solar power system functions safely and efficiently. At {company_name}, we provide expert electrical wiring services to guarantee seamless energy distribution from your solar panels to your home or business.

                ### **subservice1**
                We offer fixed wiring solutions that enhance the stability and reliability of your solar energy system. Our professional installations ensure compliance with safety standards and optimal electrical performance.

                ### **subservice2**
                If your current electrical wiring is outdated or inadequate for your solar energy needs, we provide new wiring solutions that optimize energy flow and improve overall system efficiency.

                and more if there are additional subservices...

                ---
                and more if there are additional service...

                #### **3. Service Process Overview**
                - Provide a **clear, step-by-step breakdown** of how the service is delivered.
                - Keep it **simple, engaging, and informative**.

                #### **4. Call to Action (CTA)**
                - End with a **strong, persuasive CTA**, such as:
                  - **"Contact us today for a free consultation!"**
                  - **"Book your service now and enjoy hassle-free solar solutions."**

                #### **5. SEO Optimization & Readability**
                - Ensure content is **SEO-optimized** for better search rankings.
                - Use **concise paragraphs, bullet points, and subheadings** for easy reading.

                #### **6. Adaptability**
                - **Do not mention specific locations unless required.**

                - **Use this research:** {research_data}
                - **Apply these SEO best practices:** {seo_data}

                The content must be **engaging, structured, and persuasive**, ensuring customers can easily navigate and understand your services.

                ---
                please not provide a code and html tag.
                """,
"individual_service_page": f"""
                Instruction: Generate high-quality, human-like content for each of the following services: `{services_list}`.

                Each service listed below must have its **own dedicated page** with content that is **specific to that subservice**. **Ensure that a response is generated for every subservice** without skipping any.

                **📌 Important Instructions:**
                - Generate **a full separate response for each subservice** in `{services_list}`.
                - Do **not** skip any subservice.
                - Do **not** mix content between subservices.
                - The content must be **unique for each subservice** and **not generic**.
                - Maintain a **consistent format** and ensure high-quality, structured writing.
                - The output must include **every subservice in the input list**.

                ---

                🔹 **For each subservice in `{services_list}`, use the following structure:**

                ---

                ### **[Subservice Name]**

                #### **Introduction**
                - Provide an engaging introduction that explains the importance of `[Subservice Name]`.
                - Mention why it is relevant for customers.

                #### **What is [Subservice Name]?**
                - Define `[Subservice Name]` in simple terms.
                - Explain how it works and why it is necessary.
                - Ensure the content is **exclusive to this subservice**.

                #### **Key Benefits of [Subservice Name]**
                - List the main benefits of this specific service.
                - Explain how customers will benefit from choosing this service.
                - Use **bullet points** for clarity.

                #### **Signs You Need [Subservice Name] (if applicable)**
                - Provide a list of signs that indicate when this service is needed.
                - Keep it **directly relevant** to this service.

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
                  please not provide a code and html tag.
                """,

"service_area_page": f"""
Show the subservices according to the chosen service area.

For each service in {formatted_result}, follow this structure, ensuring the tone is professional, engaging, and informative.

---
{city}

### {value} in {city}
- Write a compelling introduction about this subservice, highlighting why it is important and beneficial for customers in {city}. Explain its key features and how it solves a problem.

- Provide additional details, such as the expertise of the team, the quality of service, or any guarantees. Ensure the content is specific, informative, and valuable to the customer.

- If applicable, mention any unique aspects of this service in {city}, such as compliance with local regulations, availability, or special offers.

- Ensure each subservice follows the same format while maintaining natural variations in wording.
- shown in a paragraph. The heading should be the service name and then the paragraph should be the service description.
- [Provide details about the second subservice, explaining its benefits and relevance to customers in {city}.]
---
- Show all the results.
please not provide a code and html tag.
"""

}
    pages = {key: llm.invoke(prompt).content for key, prompt in prompts.items()}
    state.update(pages)
    print("content_done")

    return state


def refine_content(state: ContentState) -> ContentState:
    prompts = {
        "refine_home_page_content": f"""You are an expert UK-based web content writer. Your task is to refine the following **Home Page Content** to match the structure, style, and detail level of top-tier UK service websites. The content should be well-organized, highly detailed, and formatted professionally.
        ---

        ### **Few-Shot Examples of Desired Structure (UK-Specific, Highly Detailed)**

        #### **Example 1 - Exeter’s Heating Experts**
        🏡 **Your Trusted Local Heating Specialists** | Providing Gas Boiler Installations & Central Heating Solutions Across Exeter & South Devon

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

        {state["home_page"]}

        ---

        ### **📌 Instructions for Refinement (UK-Specific, Highly Detailed & Professional):**
        ✅ **Enhance Detail & Professionalism:** The content should be **well-structured, informative, and engaging**.
        ✅ **Use UK Spelling & Terminology:** Ensure terms like **Gas Safe, A-rated boilers, VAT, CP12 certificates, Smart Thermostats, 10-Year Warranties** are included.
        ✅ **Use UK city only :** If the city need then use only UK city not a other**.
        ✅ **Improve Readability:** Format with **clear headings, bullet points, and short paragraphs** for better user experience.
        ✅ **Make it SEO-Friendly (Without Being Robotic):** Use relevant keywords naturally, ensuring it reads as **authentic, high-quality website content**.
        ✅ **Focus on Benefits & Trustworthiness:** Clearly outline **why customers should choose this company**, including guarantees, fast response times, expert knowledge, and certifications.
        ✅ **Ensure Content is UK Market-Specific:** Adapt services, pricing models, and customer expectations to fit UK consumer standards.

        Return the improved home page content in a **fully structured, highly detailed, and polished format** suitable for a professional UK service business website.""",

        "refine_about_us_page_content": f""" You are an expert UK-based content writer specializing in home services. Your task is to refine the following **About Us Page Content** for a heating and plumbing company to match the structure, style, and detail level of top-tier UK service websites. The content should be well-organized, informative, and highly professional.
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

        {state["about_us_page"]}

        ---

        ### **📌 Instructions for Refinement (UK-Specific, Highly Detailed & Professional):**
        ✅ **Enhance Detail & Professionalism:** The content should be **well-structured**, **clear**, and **engaging**.
        ✅ **Use UK Spelling & Terminology:** Ensure terms like **Gas Safe**, **A-rated boilers**, **VAT**, and **renewable energy** are included.
        ✅ **Improve Readability:** Use **clear headings**, **bullet points**, and **short paragraphs** for ease of reading.
        ✅ **Focus on Benefits & Trustworthiness:** Make sure to clearly outline **why customers should choose this company**, highlighting **experience, customer service, and certifications**.
        ✅ **Make it SEO-Friendly:** Integrate **relevant UK-based keywords** naturally into the content to improve SEO ranking without sacrificing readability.
        ✅ **Include Location Details & Coverage Areas:** Clearly specify the regions served, emphasizing the **local expertise** of the business.

        Return the improved **About Us Page** content in a **fully structured, highly detailed, and polished format** suitable for a professional UK service business website.""",


        "refine_service_page": f""" You are an expert in creating **SEO-optimized, highly detailed, and engaging** service pages for business websites.
         Your task is to **refine the service page content** to make it more structured, comprehensive, and conversion-friendly.
         ### **Instructions for Refinement:**
         - **Expand Each Section** – Provide **in-depth descriptions** of the services, including their **benefits and processes**.
         - **Use Clear Headings & Subheadings** – Structure the content properly for **better readability and SEO**.
         - **Highlight Key Features with Bullet Points** – Make the information **easy to scan and engaging**.
         - **Incorporate Persuasive & Actionable Language** – Encourage visitors to **take action** (e.g., **"Get a Free Quote Today!"**).
         - **Ensure Natural Keyword Integration** – Optimize for **search engines** while keeping it human-friendly.
         - **Mention the Location Where Relevant** – If the services are location-specific, naturally include city names.
         ---

         ### **Example of a Structured & Detailed Service Page:**
         ```
         ## **Our Expert Plumbing & Heating Services in London**
         At **South Coast Plumbing & Heating**, we offer a full range of **reliable and high-quality heating and plumbing services** in London. Our experienced, **Gas Safe registered engineers** ensure your home stays warm, safe, and energy-efficient all year round.

         ### **🔹 New Boiler Installation**
         Looking for a new boiler? We supply and install **high-efficiency A-rated boilers** from top brands like **Worcester Bosch, Vaillant, and Ideal**. Our experts recommend the **best energy-efficient solution** based on your home’s heating needs.

         ✅ Free Consultation & Personalized Advice
         ✅ Professional Installation with a 10-Year Warranty
         ✅ Energy-Saving Solutions to Lower Your Bills

         ### **🔹 Fast & Reliable Boiler Repairs**
         Experiencing boiler issues? We provide **same-day emergency repairs** for all major brands. Common issues we fix:

         - **No heating or hot water**
         - **Leaks, pressure drops, and error codes**
         - **Strange noises or pilot light failures**

         🚀 **Call now for urgent repairs!**
         ### **🔹 Annual Boiler Servicing**
         Keep your boiler in **top condition** with our **comprehensive servicing**:

         - **Safety checks** to prevent carbon monoxide risks
         - **Cleaning & tuning** for maximum efficiency
         - **Early fault detection** to avoid costly repairs

         🔥 **Book your service today to avoid winter breakdowns!**
         ---
         ```

         ---

         ### **Now, refine the following service page content into a highly detailed, structured, and persuasive version like the example above:**

         {state["service_page"]}

         **Make sure to:**
         - Expand the details of each section.
         - Use structured headings and subheadings.
         - Improve the **clarity, engagement, and persuasiveness** of the content.
         - Include **strong call-to-action statements**.
         - Ensure **SEO optimization** with natural keyword integration.

         Provide the refined content in a **well-formatted and professional** manner.
         """,

        "refine_individual_service_page" : f""" You are an expert at generating professional, structured, and SEO-optimized service pages for a business website.

         Please **rewrite and refine** the following individual service page content using the exact format of the examples provided below.
         Your response **must strictly follow the same structure, tone, and clarity** as the examples.
         **Instructions:**
         - Maintain the **exact headings, formatting, and structure** used in the examples.
         - Ensure **clarity and professionalism** in the content.
         - Use **engaging and SEO-friendly language**.
         - Structure the content with **clear headings, subheadings, and sections**.
         - Adapt the text while keeping it **relevant to the service and location**.

         **Example Format of a Well-Structured Service Page:**
         ```
         SERVICE AREAS PAGES
         Exeter

         Heating Services for Exeter

         Whether you need a new boiler, central heating installation, power flushing service, or boiler repair, our Gas Safe engineers are here to ensure your home stays warm and comfortable. South Coast Plumbing and Heating covers Exeter and provides a complete range of services for Natural Gas and oil boilers.

         New Boilers Installed in Exeter
         Are you looking to upgrade to a new, energy-efficient boiler in Exeter? We supply and install A-rated gas and oil boilers from leading manufacturers. Our experienced gas heating engineers can help you choose the right replacement boiler for your home. Get an online quote from us for a new boiler that delivers optimum efficiency and reduces your energy bills.

         We Service Gas and Oil Boilers in Exeter
         Regular maintenance is key to ensuring your boiler works safely and efficiently all year round. Our team offers annual boiler servicing for homes across Exeter. During the boiler service, we perform a full inspection, identifying any potential issues before they become costly repairs. Keeping your boiler in top condition can also help to extend its lifespan and maintain your warranty.

         Boilers Fixed Professionally in Exeter
         If your boiler breaks down, you don’t want to be left without heating or hot water for long. We offer fast and reliable boiler repairs throughout Exeter. Our team of Gas Safe engineers is fully equipped to diagnose and fix common boiler issues, such as leaks, no hot water, and non-firing systems. If you’re experiencing boiler problems, contact us for a quick, professional repair service.

         Air Source Heat Pumps
         Ask our team to give you a quote for a new air source heat pump in Exeter. Renewable energy products are the next generation in heating technology, so ask us about installing it in your home. We are your local renewable energy experts, available to install the best heat pump system to suit your home in Exeter.

         All Plumbing for Exeter
         When you need a reliable plumber in Exeter, our team is here to help. We handle all types of plumbing projects, including general plumbing and emergency plumbing. You can count on us for prompt and professional service every time. For new kitchen or bathroom plumbing and 24-hour plumbers, our Exeter plumbers have you covered.

         Commercial Boilers & Plumbing Exeter
         If you need a commercial plumber or heating engineer for your Exeter business, then South Coast Plumbing and Heating is the best team to contact. We install and maintain commercial boilers and hot water systems in Exeter. We also cover commercial plumbing projects.
         ```

        **Now, rewrite the following service page content to match the format above, strictly follow:**

        ```
        {state["individual_service_page"]}
        ```

        **Your response must follow the example structure exactly.**
    """,
        "service_area_page": f""" Yor task is assigned a refine content of the page {state["service_area_page"]}. I peovide the some example check them and then refine the content.
Few-Shot Examples
Here are well-structured examples of service area pages to guide the refinement process:

Example 1: Blackburn Area Page
"Blackburn’s Boiler & Plumbing Experts. We are a plumbing and heating specialist covering Blackburn in Lancashire and the surrounding areas. Our team is available for new boiler installations, repairs, and servicing for all types of heating systems in Blackburn. We also handle a wide range of plumbing services, including emergency plumbing. If you're interested in renewable heating solutions, ask us about installing an air-source heat pump for your home in the Blackburn area."

(Continue following the structured sections, ensuring professional, high-quality, and location-specific content.)

Example 2: Bolton Area Page
"Bolton’s Boiler & Plumbing Experts. Jaws Gas Services is your trusted plumbing and heating specialist serving Bolton and the surrounding areas. Our skilled team provides new boiler installations, repairs, and servicing for all types of heating systems in Bolton. We also offer a comprehensive range of plumbing services, including 24/7 emergency plumbing support. If you're exploring renewable heating options, ask us about installing an air-source heat pump in your Bolton home."

(Continue following the structured sections, refining language, and ensuring clarity and engagement.)

Important Notes:
✅ Each service area must have its own dedicated page with content related only to that location.
✅ Maintain structure, clarity, and a professional yet engaging tone.
✅ Use headings and bullet points for improved readability.
✅ Ensure consistency across all service area pages.
        """

    }
    pages = {key: llm.invoke(prompt) for key, prompt in prompts.items()}
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
    7. **Grammar, Spelling & Language Precision** – Any typos or awkward phrasing?

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
        You are a **senior UK-based content strategist and conversion copywriter**. Your mission is to **completely refine and enhance** the given Home Page Content so that it **achieves a significantly higher quality score**.

        ### **🚀 Your Objectives:**
        ✅ **Fix ALL Issues Highlighted in the Feedback Below**
        ✅ **Upgrade Readability, Persuasiveness, and Professionalism**
        ✅ **Increase the Quality Score (Currently: {previous_score})**
        ✅ **Enhance Structure & Engagement**
        ✅ **Strengthen CTAs & Conversion Elements**

        ### **🔍 Issues in the Previous Version (MUST BE FIXED):**
        {feedback}

        ### **📜 Previous Home Page Content (Rewrite & Improve):**
        {previous_home_page}

        **🚀 Your rewrite must be a clear, measurable improvement over the previous version.**
        Instruction: Do NOT include any explanations, commentary, any code, HTML tags, or introductions.
        """,

        "refine_about_us_content": f"""
        You are a **senior UK-based content strategist and brand storyteller**. Your mission is to **completely refine and enhance** the About Us page so it **authentically represents the company's values and credibility**.

        ### **🚀 Your Objectives:**
        ✅ **Fix ALL Issues Highlighted in the Feedback Below**
        ✅ **Enhance Brand Storytelling & Authenticity**
        ✅ **Ensure a Compelling and Trustworthy Narrative**
        ✅ **Improve Readability, Flow, and Engagement**
        ✅ **Increase the Quality Score (Currently: {previous_score})**

        ### **🔍 Issues in the Previous Version (MUST BE FIXED):**
        {feedback}

        ### **📜 Previous About Us Page Content (Rewrite & Improve):**
        {previous_about_us}

        **🚀 Your rewrite must be a clear, measurable improvement over the previous version.**
        Instruction: Do NOT include any explanations, commentary, any code, HTML tags, or introductions.
        """,

        "refine_service_page_content": f"""
        You are a **senior UK-based content strategist and SEO specialist**. Your mission is to **completely refine and enhance** the Service Page Content to make it **highly engaging, clear, and optimized for conversions**.

        ### **🚀 Your Objectives:**
        ✅ **Fix ALL Issues Highlighted in the Feedback Below**
        ✅ **Improve Service Descriptions & Benefits**
        ✅ **Enhance Readability, Clarity, and SEO Optimization**
        ✅ **Increase the Quality Score (Currently: {previous_score})**
        ✅ **Strengthen CTAs & User Engagement**

        ### **🔍 Issues in the Previous Version (MUST BE FIXED):**
        {feedback}

        ### **📜 Previous Service Page Content (Rewrite & Improve):**
        {previous_service_page}

        **🚀 Your rewrite must be a clear, measurable improvement over the previous version.**
        Instruction: Do NOT include any explanations, commentary, any code, HTML tags, or introductions.
        """,

        "refine_individual_service_page_content": f"""
        You are a **senior UK-based service page specialist and conversion copywriter**. Your mission is to **refine and enhance** this Individual Service Page so that it **clearly communicates value and drives conversions**.

        ### **🚀 Your Objectives:**
        ✅ **Fix ALL Issues Highlighted in the Feedback Below**
        ✅ **Clarify Service Benefits and Unique Selling Points**
        ✅ **Enhance Readability, Trustworthiness, and Persuasion**
        ✅ **Increase the Quality Score (Currently: {previous_score})**
        ✅ **Optimize for SEO and Engagement**

        ### **🔍 Issues in the Previous Version (MUST BE FIXED):**
        {feedback}

        ### **📜 Previous Individual Service Page Content (Rewrite & Improve):**
        {previous_individual_service_page}

        **🚀 Your rewrite must be a clear, measurable improvement over the previous version.**
        Instruction: Do NOT include any explanations, commentary, any code, HTML tags, or introductions.
        """,

        "refine_service_area_page_content": f"""
        You are a **senior UK-based content strategist and local SEO specialist**. Your mission is to **completely refine and enhance** the Service Area Page Content so that it **attracts and converts local customers effectively**.

        ### **🚀 Your Objectives:**
        ✅ **Fix ALL Issues Highlighted in the Feedback Below**
        ✅ **Make Location-Specific Content More Engaging**
        ✅ **Ensure Clear and Persuasive Messaging**
        ✅ **Improve SEO Optimization for Local Search**
        ✅ **Increase the Quality Score (Currently: {previous_score})**

        ### **🔍 Issues in the Previous Version (MUST BE FIXED):**
        {feedback}

        ### **📜 Previous Service Area Page Content (Rewrite & Improve):**
        {previous_service_area_page}

        **🚀 Your rewrite must be a clear, measurable improvement over the previous version.**
        Instruction: Do NOT include any explanations, commentary, any code, HTML tags, or introductions.
        """
    }
    # Invoke LLM for refinement on all pages
    refined_pages = {key: llm.invoke(prompt).content.strip() for key, prompt in prompts.items()}

    # Update state with refined content
    state.update({
        "home_page": refined_pages["refine_home_page_content"],
        "about_us_page": refined_pages["refine_about_us_content"],
        "service_page": refined_pages["refine_service_page_content"],
        "individual_service_page": refined_pages["refine_individual_service_page_content"],
        "service_area_page": refined_pages["refine_service_area_page_content"],
    })

    return state
def create_content_workflow():
    
    workflow =  StateGraph(ContentState)

    # ✅ Define Nodes
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
        lambda state: "feedback_improvement" if state["quality_score"] <= 2 else END,
        {
            "feedback_improvement": "feedback_improvement",
            END: END
        }
    )

    # ✅ Add Loopback from feedback_improvement to refine_content
    workflow.add_edge("feedback_improvement", "evaluate_content_quality")
    compile = workflow.compile() 
    # ✅ Compile the Graph
    return compile
