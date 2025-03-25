import requests
import pandas as pd

# Wells Fargo CIK Number
CIK = "0000072971"

# SEC EDGAR API URL for company filings
SEC_API_URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"

# User-Agent required by SEC (replace with your email)
HEADERS = {"User-Agent": "your-email@example.com"}

def fetch_wells_fargo_10q_accession_numbers():
    response = requests.get(SEC_API_URL, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        
        # Extract filings
        filings = data.get("filings", {}).get("recent", {})
        form_types = filings.get("form", [])
        accession_numbers = filings.get("accessionNumber", [])
        filing_dates = filings.get("filingDate", [])
        
        # Filter only 10-Q filings
        records = [
            {"Accession Number": acc_num, "Filing Date": date}
            for form, acc_num, date in zip(form_types, accession_numbers, filing_dates)
            if form == "10-K"
        ]
        
        # Convert to DataFrame for better visualization
        df = pd.DataFrame(records)
        return df
    
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return None

# Fetch and display the Accession Numbers
df_10q = fetch_wells_fargo_10q_accession_numbers()
print(df_10q)
