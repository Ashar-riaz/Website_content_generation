from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro",google_api_key=GEMINI_API_KEY)
search_tool = DuckDuckGoSearchRun(region="uk-en", safe="strict")

class ContentState(Dict):
    idea: str
    company_name: str
    services: str
    research_data: str
    seo_optimization: str
    home_page: str
    about_us_page: str
    service_page: str
    individual_service_page: str
    quality_score: int

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
    services = ", ".join(state["services"])
    prompts = {
    "home_page": f"""You are a professional web content writer. Write an engaging **Home Page** for a company specializing in {services}.
    - Start with a compelling headline that highlights the company’s expertise and services.
    - Introduce the business and its main offerings concisely.
    - Provide a trustworthy and friendly tone, emphasizing expert service and customer satisfaction.
    - Highlight key services such as {services} and any unique benefits (e.g., free annual servicing, warranties, financing options).
    - Include a section about why customers should choose this company, emphasizing reliability, transparency, and professional service.
    - Ensure the content is universally applicable, avoiding any references to specific cities, states, or countries.
    - Use persuasive, SEO-friendly language that encourages customers to take action.
    - Use this research: {research_data}
    - Apply these SEO best practices: {seo_data}
    """,

    "about_us_page": f"""You are an expert storyteller and professional content writer. Write a compelling **About Us Page** for a company specializing in {services}.
    - Start with a warm and engaging introduction, emphasizing the company's commitment to customer satisfaction and high-quality service.
    - Clearly outline the company’s **mission, values, and expertise**, focusing on professionalism, reliability, and trust.
    - Highlight the company’s **experience, certifications, and industry credibility** (e.g., working with trusted brands, offering long-term warranties).
    - If applicable, mention flexible payment or financing options to make services more accessible to customers.
    - Explain the company’s **work process step by step**, ensuring transparency and ease of understanding for potential customers.
    - Use a **reassuring and customer-focused tone**, emphasizing quality workmanship, safety, and customer satisfaction.
    - Avoid specific location names to keep the content universally applicable.
    - Ensure the content is **SEO-optimized**, informative, and encourages potential customers to trust and engage with the business.
    - Use this research: {research_data}
    - Apply these SEO best practices: {seo_data}
    """,

    "service_page":f"""You are a professional content strategist. Create a **dedicated service page** for {services}.

    - **Introduction:** Clearly introduce the service and its importance for customers.
    - **What We Offer:** Explain what is included in this service, covering key features and benefits.
    - **Why Choose Us:** Highlight expertise, quality assurance, warranties, or unique advantages of choosing this company.
    - **Process:** Outline the step-by-step process of how this service is provided (e.g., consultation, installation, maintenance).
    - **Customer Benefits:** Detail how customers will benefit from this service (e.g., cost savings, efficiency, reliability).
    - **Call to Action (CTA):** Encourage customers to request a quote, book an appointment, or contact for more details.
    - Ensure the content is **clear, persuasive, SEO-optimized, and engaging**.
    - Do not mention specific locations so the content remains adaptable.
    - Use this research: {research_data}
    - Apply these SEO best practices: {seo_data}
    """,
   "individual_service_page": f"""You are a professional web content writer. Write a **dedicated service page** for the service: {services}. The content should be structured with a clear heading for each service and the related content underneath it. Ensure that the page is **informative, practical, and engaging** while maintaining a professional tone.
    ### **Service: {services}**
    there is the list of service  {services} so show one by one.
    #### **Introduction**
    Provide a brief, clear introduction to the service, explaining its purpose and value for the customer.

    #### **Service Details**
    Describe what is included in this service, highlighting its key features and benefits.

    #### **Process**
    Outline the step-by-step process of how this service is delivered, including any important details customers should know.

    #### **Customer Benefits**
    Explain how the customer will benefit from this service, whether through cost savings, enhanced efficiency, or improved reliability.

    #### **Why Choose Us?**
    Provide practical reasons why customers should trust this company for this service, focusing on expertise, quality, and customer satisfaction.

    #### **Call to Action (CTA)**
    Encourage customers to take action, such as requesting a quote, scheduling an appointment, or getting in touch for more details.

    - Ensure the content is **clear, persuasive, SEO-optimized, and engaging**.
    - Do not mention specific locations so the content remains adaptable for any service area.
    - Keep the content **concise, natural, and SEO-friendly**—avoid overly promotional language.
    - Use this research: {research_data}
    - Apply these SEO best practices: {seo_data}
    """

}
    pages = {key: llm.invoke(prompt) for key, prompt in prompts.items()}
    state.update(pages)
    return state


def refine_content(state: ContentState) -> ContentState:
    services = ", ".join(state["services"])
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

        {state["about_us_page"].content}

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

         {state["service_page"].content}

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
          ### **Service: {services}**
          there is the list of service  {services} so show one by one.
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
        {state["individual_service_page"].content}
        ```

        **Your response must follow the example structure exactly.**
    """
    }
    pages = {key: llm.invoke(prompt) for key, prompt in prompts.items()}
    state.update(pages)
    return state

def evaluate_content_quality(state: ContentState) -> ContentState:
    """Evaluates the quality of the given content and assigns a score from 0 to 10.
    If the score is 7 or below, it suggests regeneration.
    """
    prompt = f"""
    ### **Role & Responsibility**
    You are an **extremely strict content quality evaluator**, ensuring that the provided website content is **highly professional, conversion-focused, human-like, and SEO-optimized**.
    Your job is to **identify even the smallest weaknesses** and ensure that only **exceptional** content is accepted.

    ### **Evaluation Criteria (Be Extremely Critical)**
    1. **Readability & Flow** – Is the content **crystal clear** and **engaging**, or does it contain **clunky phrasing, awkward transitions, or unnecessary complexity**?
    2. **Coherence & Structure** – Does the content **flow logically** with **no redundancy or repetition**? Are sections **properly structured** with **clear headers**?
    3. **Depth & Relevance** – Is the content **deeply informative** and **highly relevant** to plumbing, heating, and boiler services, or is it **generic and lacking real value**?
    4. **SEO Optimization** – Does the content **seamlessly integrate important keywords** while avoiding **keyword stuffing**? Are **headings, subheadings, and formatting** properly optimized?
    5. **Factual Accuracy** – Is the content **technically sound and correct**? Are there **any vague, misleading, or inaccurate claims**?
    6. **Human-like & Persuasive Tone** – Does the content read **smoothly and naturally**, or does it sound **robotic, generic, or AI-generated**?
    7. **Grammar & Language** – Are there **any grammar mistakes, typos, awkward sentence structures, or inconsistencies**?
    8. **Persuasiveness & Conversion Ability** – Does the content **convince customers to take action (e.g., request a quote, book a service)**? Are CTAs **strong and compelling**?

    ---

    ### **Scoring System (Be VERY Harsh – Only Near-Perfect Content Gets High Scores)**
    - **0-3: Unacceptable** – Poorly written, unclear, lacks professionalism. Needs a total rewrite.
    - **4-6: Below Average** – Some acceptable elements, but **not good enough** for high-quality business content. Needs serious improvement.
    - **7: Average** – Acceptable but still **far from perfect**. Requires multiple refinements.
    - **8: Above Average** – Decent, but **lacks the level of refinement needed for top-tier content**. Needs adjustments.
    - **9: Almost There** – High quality, **but still room for final polishing**.
    - **10: Perfect** – **Extremely rare.** Only award a **10** if the content is **flawless, highly persuasive, and perfectly structured**.

    ---

    ### **Content to Evaluate:**

    ```
    {state["home_page"].content}
    {state["about_us_page"].content}
    {state["service_page"].content}
    {state["individual_service_page"].content}
    ```

    **Strictly return ONLY this format:**
    - **Quality Score: X/10**
    - **Reason for Score: [Concise Explanation]**
    - **Key Areas to Improve (if applicable)**
    """

    response = llm.invoke(prompt)
    output = response.content

    # Extract the score from the response
    try:
        score_line = [line for line in output.split("\n") if "Quality Score" in line][0]
        score = int(score_line.split(":")[-1].strip().split("/")[0])
    except (IndexError, ValueError):
        score = 0  # Default to 0 if parsing fails

    # **Fix: Return updated state instead of just the score**
    state["quality_score"] = score
    return state  # **Ensure we return the updated dictionary**

# ✅ Define Workflow Steps
workflow.add_node("research_step", research_task)
workflow.add_node("seo_step", seo_optimization_task)
workflow.add_node("writing_step", content_writing_task)
workflow.add_node("refine_content", refine_content)
workflow.add_node("evaluate_content_quality", evaluate_content_quality)
workflow.add_edge("refine_content", "evaluate_content_quality")
# ✅ Define Transitions
workflow.set_entry_point("research_step")
workflow.add_edge("research_step", "seo_step")
workflow.add_edge("seo_step", "writing_step")
workflow.add_edge("writing_step", "refine_content")
workflow.add_conditional_edges(
"evaluate_content_quality",
lambda state: "refine_content" if state["quality_score"] <= 7 else END,
{
    "refine_content": "refine_content",
    END: END
}
)
content_graph = workflow.compile()

def generate_content(idea: str, company_name: str, services: str) -> Dict:
    state = content_graph.invoke({
        "idea": idea,
        "company_name": company_name,
        "services": services,
        "quality_score": 0
    })
    return state