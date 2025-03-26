
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv
import ast
from newsapi import NewsApiClient

load_dotenv()  # Load environment variables from .env file
def gemini_try(prompt):
        gemini_key=os.getenv("GEMINI_KEY")
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_data = response.candidates[0].content.parts[0].text
        avg_logprobs = response.candidates[0].avg_logprobs
        interpretation = classify_logprobs(avg_logprobs)
        return {"Text":text_data,"confidence":avg_logprobs, "interpretation": interpretation}
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
def get_names(input):
    def gemini_try(prompt):
        gemini_key=os.getenv("GEMINI_KEY")
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_data = response.candidates[0].content.parts[0].text
        avg_logprobs = response.candidates[0].avg_logprobs
        interpretation = classify_logprobs(avg_logprobs)
        return {"Text":text_data,"confidence":avg_logprobs, "interpretation": interpretation}

    entity_names=gemini_try('''Can you give me the names of the entities mentioned in the report,just give me the name of entiies in list(Give it to my in the formart of "['entityname1','entityname2','entityname3','etc']") and nothing else?'''+input)
    return entity_names["Text"]
    

def search_wiki(entity):

    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": entity
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("search"):
        entity_id = data["search"][0]["id"]
        entity_url = f"https://www.wikidata.org/wiki/{entity_id}"
        return f"Entity: {data['search'][0]['label']}, Description: {data['search'][0]['description']}, URL: {entity_url}"
    else:
        return "No results found."

    

# names=get_names('''Transaction ID: TXN123456789
# Date: 2025-03-26
# Sender: John Doe (Account No: 1234567890, Wells Fargo)
# Receiver: ABC Corp (Account No: 0987654321, JPMorgan Chase)
# Amount: $5,000.00
# Currency: USD
# Transaction Type: Wire Transfer
# Purpose: Payment for consulting services
# Status: Completed
# Reference Number: WF2025032''')
# print(names)
# list_data = ast.literal_eval(names)

# print(type(list_data))
API_KEY = os.getenv("SEC_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def check_entity_in_sec(name):
    """
    Checks if a given entity (company) is listed in the SEC EDGAR database.
    """
    url = f"https://api.sec-api.io/mapping/name/{name}?token={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for HTTP issues
        data = response.json()

        if data:
            entity = data[0]  # Assuming first result is the best match
            print("\n✅ Entity Found in SEC EDGAR Database:\n")
            print(f"Name: {entity['name']}")
            print(f"Ticker: {entity.get('ticker', 'N/A')}")
            print(f"CIK: {entity.get('cik', 'N/A')}")
            print(f"Exchange: {entity.get('exchange', 'N/A')}")
            print(f"Sector: {entity.get('sector', 'N/A')}")
            print(f"Industry: {entity.get('industry', 'N/A')}")
            print(f"Location: {entity.get('location', 'N/A')}")
            print(f"Delisted: {entity.get('isDelisted', False)}")

            return entity  # Return entity details as a dictionary

        else:
            print("\n❌ Entity Not Found in SEC EDGAR Database.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {e}")
        return None
def checknews(entity):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    top_headlines = newsapi.get_everything(q=entity,
                                           sort_by='relevancy',
                                            page=2,
                                        
                                          
                                          language='en',
                                         )
    # print(top_headlines)
    return top_headlines
# for name in list_data:
#     print(search_wiki(name))
#     print(check_entity_in_sec(name))
#     print(checknews(name))
# result_list = {
#     name: {
#         "WikiData": search_wiki(name),
#         "SEC Data": check_entity_in_sec(name),
#         "News": checknews(name)
#     }
#     for name in list_data
# }


def final_analysis(input1):
    names=get_names(input1)
    list_data = ast.literal_eval(names)

    result_list = {
        name: {
            "WikiData": search_wiki(name),
            "SEC Data": check_entity_in_sec(name),
            "News": checknews(name)
        }
        for name in list_data
    }

    result = []

    for name, data in result_list.items():
        prompt = f"""
    Analyze the entity: {name}

    1. **Anomaly Detection**  
       - Identify if this entity shows signs of fraudulent or high-risk activity based on the provided information.  
       - Cross-check against known risk patterns.  

    2. **Entity Classification**  
       - Classify the entity into one of the following categories:  
         [Corporation, Non-Profit, Shell Company, Government Agency, Financial Institution, Individual, Other].  

    3. **Risk Scoring**  
       - Assign a risk score between 0 (Low Risk) and 100 (High Risk) based on the data.  
       - Justify the assigned score.  

    4. **Supporting Evidence**  
       - WikiData Information: {data.get("WikiData", "Not Available")}  
       - SEC Filings: {data.get("SEC Data", "Not Available")}  
       - Recent News Mentions: {data.get("News", "Not Available")}  

    Please provide a structured analysis based on the above criteria.
    """

        response = gemini_try(prompt)
        print(f"Analysis for {name}:\n{response}\n")

        result.append({"Name": name, "Text": response['Text'], "Confidence": response['confidence'], "Interpretation": response['interpretation']})
    
    return {"transanction_result": result}
    
# final_analysis('''Transaction ID: TXN123456789
# Date: 2025-03-26
# Sender: John Doe (Account No: 1234567890, Wells Fargo)
# Receiver: ABC Corp (Account No: 0987654321, JPMorgan Chase)
# Amount: $5,000.00
# Currency: USD
# Transaction Type: Wire Transfer
# Purpose: Payment for consulting services
# Status: Completed
# Reference Number: WF2025032''')