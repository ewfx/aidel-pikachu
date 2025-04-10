import os
import fitz  # PyMuPDF
import re
import requests
import json
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from performace_analysis import *
import google.generativeai as genai


from loan_table import *
# Hugging Face API details
def analysis(uploaded_file):
    load_dotenv()  # Load environment variables from .env file

    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    API_KEY = os.getenv("API_KEY")
    # print(f"Authorization: Bearer {API_KEY}")
    HEADERS = {"Authorization": f"Bearer {API_KEY}"}
    def classify_logprobs(avg_logprobs):
        """
        Classifies the avg_logprobs into confidence levels.
    
        :param avg_logprobs: The average log probability value (negative number).
        :return: Confidence level as a string.
        """
        if avg_logprobs >= -0.5:
            return "High Confidence"
        elif -1.5 <= avg_logprobs < -0.5:
            return "Medium Confidence"
        else:
            return "Low Confidence"
    def gemini_try(prompt):
        gemini_key=os.getenv("GEMINI_KEY")
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_data = response.candidates[0].content.parts[0].text
        avg_logprobs = response.candidates[0].avg_logprobs
        interpretation = classify_logprobs(avg_logprobs)

        return {"Text":text_data,"confidence":avg_logprobs, "interpretation": interpretation}
    # Load PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        # Convert all text into a single string
    full_text = "\n".join(page.get_text("text") for page in doc)

    # Define the target paragraph (Risk Factors Start)
    target_paragraph = r"An investment in the Company involves risk, including the\s+possibility that the value of the investment could fall\s+substantially and that dividends or other distributions on the\s+investment could be reduced or eliminated\."

    # Define the stopping keyword (Controls and Procedures Start)
    stop_section = r"The Company’s management evaluated the effectiveness"

    # Search for the start position
    match_start = re.search(target_paragraph, full_text, re.MULTILINE)
    match_stop = re.search(stop_section, full_text, re.MULTILINE)

    if match_start:
        start_pos = match_start.start()
        end_pos = match_stop.start() if match_stop else len(full_text)  # Stop at "Controls and Procedures" if found
        extracted_text = full_text[start_pos:end_pos]
        # print('start_pos:', start_pos)
        # print('end_pos:', end_pos)
        
        # print(f"\n🔹 Extracted Section (Risk Factors to Controls and Procedures):\n")
        # print(extracted_text[:1000])  # Print only first 1000 characters for preview
        # print("\n... (truncated) ...\n")
        
    else:
        print("\n⚠️ Paragraph not found in the document.\n")
        extracted_text = ""

    # Function to extract **only bold text** from the extracted section
    def extract_bold_text(doc, start_pos, end_pos):
        bold_text = []

        for page in doc:
            html_text = page.get_text("html")  # Extract HTML content
            soup = BeautifulSoup(html_text, "html.parser")

            # Get plain text of the page
            page_text = page.get_text("text")

            # Check if the extracted section is within this page
            page_start_pos = full_text.find(page_text)  # Find where this page starts in the full document
            page_end_pos = page_start_pos + len(page_text)

            # If this page contains part of the extracted section
            if page_end_pos >= start_pos and page_start_pos <= end_pos:
                for b_tag in soup.find_all("b"):  # Find bold text
                    bold_text_str = b_tag.text.strip()

                    # Ensure the bold text is within the extracted section range
                    bold_text_pos = page_text.find(bold_text_str)
                    actual_pos = page_start_pos + bold_text_pos  # Convert to global position

                    if start_pos <= actual_pos <= end_pos:
                        bold_text.append(bold_text_str)

        return " ".join(bold_text)  # Return as a single string

    # Extract bold text from the specific section
    bold_extracted_text = extract_bold_text(doc, start_pos, end_pos)

    # print("\n🔹 **Bold Text Extracted (Within Section Only):**\n")
    # print(bold_extracted_text if bold_extracted_text else "⚠️ No bold text found!")

    # Function to split text for AI analysis
    def split_text(text, chunk_size=4000, overlap=500):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        return text_splitter.split_text(text)


    def analyze_filing(static_prompt, dynamic_prompt):
        chunks = split_text(dynamic_prompt)
        print("Total chunks:", len(chunks))
        
        results = ""
        for i, chunk in enumerate(chunks):
            prompt = f"{static_prompt}\n\n{chunk}\n\nProvide a structured summary highlighting potential risk indicators."
            # Send the chunk to the Mistral API
            result = gemini_try(prompt)
            # print("result is :",result)

            if result:
                print(f"\n🔍 **Analysis Result (Section: Chunk {i+1}):**\n")
                text_data = [result.content.parts[0].text for result in result.candidates]
                print(json.dumps(text_data, indent=4))
                results += text_data[0]
        return results
    # Function to query Hugging Face AI
    # def query_huggingface(text):
    #     payload = {"inputs": text}
        
    #     try:
    #         response = requests.post(API_URL, headers=HEADERS, json=payload)
    #         response.raise_for_status()  # Raise exception for HTTP errors

    #             return response.json()
    #         except requests.exceptions.RequestException as e:
    #             print(f"API Error: {e}")
    #             return None

        # Analyze the extracted bold text instead of normal extracted text
    prompt_for_risk=""" You are a financial fraud analyst specializing in SEC filings.
            Analyze this section of a 10-K/10-Q filing for potential red flags, inconsistencies, or signs of fraudulent activity.
            
            **Focus on:**
            1. Unusual changes in revenue, expenses, or cash flow.
            2. Legal disputes, regulatory actions, or investigations.
            3. Discrepancies in financial statements.
            4. Risk factors that seem downplayed.
            5. Insider transactions or management changes."""
    prompt_for_performace="""Analyze the following financial data extracted from a company’s annual report. The figures follow this format:

    - First column = Current Year
    - Second column = Previous Year
    - Third column = Year before Previous Year

    Identify any **discrepancies, inconsistencies, or potential signs of financial fraud** by checking:
    1. **Revenue & Profit Trends**: Are there any sudden spikes or dips?
    2. **Expense Manipulation**: Any unusual reduction in expenses despite revenue growth?
    3. **Provisioning & Write-offs**: Any sharp increases/decreases in provisions that don’t match the risk profile?
    4. **Earnings Manipulation**: Any patterns suggesting earnings smoothing or aggressive accounting?
    5. **Debt & Cash Flow Anomalies**: Any inconsistencies in debt levels vs. reported profits?
    6. **Market & Stock Data Issues**: Any anomalies in EPS, book value, or stockholder equity?

    Here is the extracted text from the annual report:"""
    prompt_for_loan_table=prompt = """
    You are a financial risk analyst specializing in loan portfolio analysis. 
    Analyze the following loan portfolio data, where each value represents figures for the most recent year followed by the previous year.

    ### Key Risk Areas to Evaluate:
    1. **Portfolio Concentration Risk**  
    - Has the ratio of **commercial loans to consumer loans** changed significantly?  
    - Is there **overconcentration** in a particular loan category, such as **real estate** or **credit card lending**?  

    2. **Credit Quality & Risk Trends**  
    - Are there **sharp increases or declines** in specific loan categories?  
    - Could the growth in any segment suggest **aggressive lending** or **loosening credit standards**?  
    - Are there **potential defaults** indicated by sudden reductions in certain loan types?  

    3. **Liquidity & Market Exposure**  
    - Does the portfolio shift indicate **higher risk exposure** (e.g., increased real estate construction loans)?  
    - Could a decline in mortgage lending suggest **higher prepayments, write-offs, or loan sales**?  

    4. **Macroeconomic & Regulatory Considerations**  
    - Do changes in loan segments reflect **broader economic conditions** (e.g., inflation, interest rate hikes, recession risks)?  
    - Are there **compliance or stress test concerns** based on lending trends?"""
    risk_text = gemini_try(prompt_for_risk+bold_extracted_text)
    risk_score=gemini_try('Can you give me a Risk Score(Low risk,Medium Risk,High Risk) based on the extracted text?'+risk_text["Text"])
    performance_text=extract_second_occurrence_page(pdf_path)
    performance_gen_text = gemini_try(prompt_for_performace+performance_text)  
    performace_risk_score=gemini_try('Can you give me a Risk Score(Low risk,Medium Risk,High Risk) based on the extracted text?'+performance_gen_text["Text"])
    regex_pattern_loan_table = r"Table\s*\d+:\s*Total Loans Outstanding by Portfolio Segment and Class of\s*Financing Receivable"
    stop_phrase_loan_table = "We manage our credit risk by establishing what we believe"
    loan_table_text=extract_table_content(pdf_path, regex_pattern_loan_table, stop_phrase_loan_table)
    loan_table_gen_text = gemini_try(prompt_for_loan_table+loan_table_text)  # Analyze the extracted loan table
    loan_risk_score=gemini_try('Can you give me a Risk Score(Low risk,Medium Risk,High Risk) based on the extracted text?'+loan_table_gen_text["Text"])
    entity_analysis_text=gemini_try('Overall summary of possible risks that wells fargo can face based on the report,Where should we be careful.give it like a summary'+full_text)
    entity_risk_score=gemini_try('Can you give me a Risk Score(Low risk,Medium Risk,High Risk) based on the extracted text?'+entity_analysis_text["Text"])
    return {"Risk": risk_text, 
            "Performance": performance_gen_text, 
            "LoanTable": loan_table_gen_text,
            "RiskScore": risk_score,
            "PerformanceScore": performace_risk_score,
            "LoanTableScore": loan_risk_score,
            "EntityAnalysis": entity_analysis_text,
            "EntityRiskScore": entity_risk_score,
            }
            
def table_answers():
    # Load PDF
    pdf_path = "2021-annual-report.pdf"  # Change this to the actual path
    doc = fitz.open(pdf_path)

        # Convert all text into a single string
    full_text = "\n".join(page.get_text("text") for page in doc)
    def classify_logprobs(avg_logprobs):
        """
        Classifies the avg_logprobs into confidence levels.
    
        :param avg_logprobs: The average log probability value (negative number).
        :return: Confidence level as a string.
        """
        if avg_logprobs >= -0.5:
            return "High Confidence"
        elif -1.5 <= avg_logprobs < -0.5:
            return "Medium Confidence"
        else:
            return "Low Confidence"
        
    def gemini_try(prompt):
        gemini_key=os.getenv("GEMINI_KEY")
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_data = response.candidates[0].content.parts[0].text
        avg_logprobs = response.candidates[0].avg_logprobs
        interpretation = classify_logprobs(avg_logprobs)

        return {"Text":text_data,"confidence":avg_logprobs, "interpretation": interpretation}

    table_checklist=gemini_try('''Anwer the following questions in single YES/NO ,dont answer anything else,there are 10 questions,I want 10 YES/NO..  1.Loan Portfolio Risk: Has there been a significant shift in the commercial-to-consumer loan ratio or concentration in high-risk sectors (e.g., real estate, auto loans)?

2️⃣ Regulatory & Compliance Issues: Are there any ongoing or newly disclosed investigations, lawsuits, or regulatory penalties that could impact operations?

3️⃣ Credit Loss Provisions: Has the allowance for loan losses increased disproportionately compared to loan growth, signaling potential credit quality issues?

4️⃣ Net Interest Margin (NIM) Trends: Is NIM shrinking, indicating declining profitability due to lower lending rates or higher funding costs?

5️⃣ Efficiency Ratio & Expense Management: Is non-interest expense growing faster than revenue, suggesting operational inefficiencies or excessive legal costs?

6️⃣ Deposit & Liquidity Trends: Are total deposits declining, or is there increased reliance on short-term funding, signaling potential liquidity stress?

7️⃣ Risk Management & Internal Controls: Are there disclosures of weaknesses in internal controls or governance failures that could lead to future compliance breaches?

8️⃣ Executive & Board Stability: Have there been major executive departures, board changes, or unusual insider stock sales that could indicate internal turmoil?

9️⃣ Capital Adequacy & CET1 Ratio: Is Wells Fargo’s Common Equity Tier 1 (CET1) ratio declining, indicating weakening capital reserves to absorb financial shocks?

🔟 Reputation & Customer Trust: Is there evidence of reputational damage affecting customer confidence, such as declining consumer deposits or adverse media coverage?'''+full_text)
    print(table_checklist["Text"])
    return {
        "Table_Answers":table_checklist["Text"]
    }
# analysis()