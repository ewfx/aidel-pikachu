import requests
import pandas as pd
import numpy as np
import time
import json
from IPython.display import display, HTML
from sec_api import QueryApi



SEC_KEY = "0160dfd90fb23cf8c3f199db988c402261c53c25e7f7fc303c5b0ccc7c3ef725"
WELLS_FARGO_CIK = "CIK0000072971"
API_END_POINT = "https://api.sec-api.io/xbrl-to-json"
FILLING_URL = "https://www.sec.gov/Archives/edgar/data/72971/000183988225017028/0001839882-25-017028-index.html"


xbrl_converter_api_endpoint = "https://api.sec-api.io/xbrl-to-json"

# get your API key at https://sec-api.io
query_api = QueryApi(api_key=SEC_KEY)

# fetch all 10-Q and 10-K filings for Wells Fargo
query = {
    "query": {
        "query_string": {
            "query": "(formType:\"10-Q\" OR formType:\"10-K\") AND ticker:WFC"
        }
    },
    "from": "0",
    "size": "20",
    "sort": [{ "filedAt": { "order": "desc" } }]
}

query_result = query_api.get_filings(query)

accession_numbers = []

# extract accession numbers of each filing
for filing in query_result['filings']:
    accession_numbers.append(filing['accessionNo'])
    

"""
accession_numbers: 
['0000072971-25-000066',
 '0000072971-24-000064',
 '0000072971-23-000071'.
 '0000072971-24-000243',
 '0000072971-24-000185',
 '0000072971-24-000129',
 '0000072971-23-000170',
 '0000072971-23-000138',
 '0000072971-23-000102',
 '0000072971-22-000205',
]
"""


# get XBRL-JSON for a given accession number
def get_xbrl_json(accession_no, retry = 0):
    request_url = xbrl_converter_api_endpoint + "?accession-no=" + accession_no + "&token=" + SEC_KEY

    # linear backoff in case API fails with "too many requests" error
    try:
      response_tmp = requests.get(request_url)
      xbrl_json = json.loads(response_tmp.text)
    except:
      if retry > 5:
        raise Exception('API error')
      
      # wait 500 milliseconds on error and retry
      time.sleep(0.5) 
      return get_xbrl_json(accession_no, retry + 1)

    return xbrl_json

def get_income_statement(xbrl_json):
    income_statement_store = {}

    if "StatementsOfIncome" not in xbrl_json:
        return pd.DataFrame()  
    
    # iterate over each US GAAP item in the income statement
    for usGaapItem in xbrl_json['StatementsOfIncome']:
        values = []
        indicies = []

        for fact in xbrl_json['StatementsOfIncome'][usGaapItem]:
            # only consider items without segment. not required for our analysis.
            if 'segment' not in fact:
                index = fact['period']['startDate'] + '-' + fact['period']['endDate']
                # ensure no index duplicates are created
                if index not in indicies:
                    values.append(fact['value'])
                    indicies.append(index)                    

        income_statement_store[usGaapItem] = pd.Series(values, index=indicies) 

    income_statement = pd.DataFrame(income_statement_store)
    # switch columns and rows so that US GAAP items are rows and each column header represents a date range
    return income_statement.T 

def merge_income_statements(statement_a, statement_b):
    if statement_a.empty or statement_b.empty:
        print("One of the DataFrames is empty. Skipping merge.")
        return statement_a if not statement_a.empty else statement_b

    # Reset index to ensure merge happens on the same column
    statement_a = statement_a.reset_index()
    statement_b = statement_b.reset_index()

    # Merge on the index column
    merged_statement = statement_a.merge(statement_b, how="outer", on="index", suffixes=('_left', ''))

    # Set index back to original
    merged_statement.set_index("index", inplace=True)

    return merged_statement


def clean_income_statement(statement):
    for column in statement:

        # column has more than 5 NaN values
        is_nan_column = statement[column].isna().sum() > 5

        if column.endswith('_left') or column == 'key_0' or is_nan_column:
            statement = statement.drop(column, axis=1)
    
    # rearrange columns so that first column represents first quarter
    # e.g. 2018, 2019, 2020 - and not 2020, 2019, 2018
    sorted_columns = sorted(statement.columns.values)
    
    return statement[sorted_columns]


previous_income_statement_set = False
income_statement_final = None

for accession_no in accession_numbers[0:9]:
    print(accession_no)
    
    # get XBRL-JSON of 10-Q or 10-K filing by accession number
    xbrl_json_data = get_xbrl_json(accession_no)
    
    # convert XBRL-JSON to a pandas dataframe
    income_statement_uncleaned = get_income_statement(xbrl_json_data)

    # clean the income statement
    income_statement_cleaned = clean_income_statement(income_statement_uncleaned)
    
    # print income statement on each iteration to monitor progress
    display(HTML(income_statement_cleaned.to_html()))
    
    # merge new income statement with previously generated income statement
    if previous_income_statement_set:
        income_statement_final = clean_income_statement(merge_income_statements(income_statement_final, income_statement_cleaned))
    else:
        income_statement_final = income_statement_cleaned
        previous_income_statement_set = True

net_income = income_statement_final.loc["NetIncomeLoss"]
print(net_income)


# First, reset index so that we have a DataFrame with "Period" and "NetIncome"
net_income_df = net_income.reset_index()
net_income_df.columns = ["Period", "NetIncome"]

net_income_df["Year"] = net_income_df["Period"].str[:4]
net_income_df["StartMonth"] = net_income_df["Period"].str[5:7].astype(int)
net_income_df["EndMonth"] = net_income_df["Period"].str[16:18].astype(int)
net_income_df = net_income_df.sort_values(["Year", "StartMonth"])
print(net_income_df)

# Dictionary to store properly split quarters
quarterly_data = {}

# First Pass: Process Q1, Q2, and Q3 first
for _, row in net_income_df.iterrows():
    year = row["Year"]
    net_income = int(row["NetIncome"])
    start_month = row["StartMonth"]
    end_month = row["EndMonth"]

    if start_month == 1 and end_month == 3:  # Q1
        quarterly_data[f"{year}-Q1"] = net_income

    elif start_month == 1 and end_month == 6:  # H1 (First Half)
        quarterly_data[f"{year}-Q2"] = int(net_income) - int(quarterly_data.get(f"{year}-Q1", 0))

    elif start_month == 1 and end_month == 9:  # 9 Months Data
        quarterly_data[f"{year}-Q3"] = int(net_income) - int(
           int( quarterly_data.get(f"{year}-Q1", 0)) + int(quarterly_data.get(f"{year}-Q2", 0))
        )

    elif start_month == 4 and end_month == 6:  # Q2
        quarterly_data[f"{year}-Q2"] = net_income

    elif start_month == 7 and end_month == 9:  # Q3
        quarterly_data[f"{year}-Q3"] = net_income

# Second Pass: Process Q4 after ensuring Q1, Q2, and Q3 exist
for _, row in net_income_df.iterrows():
    year = row["Year"]
    if(int(year) == 2021):
        continue
    net_income = row["NetIncome"]
    start_month = row["StartMonth"]
    end_month = row["EndMonth"]

    if start_month == 1 and end_month == 12:  # Full Year Data
        q1 = quarterly_data.get(f"{year}-Q1", 0)
        q2 = quarterly_data.get(f"{year}-Q2", 0)
        q3 = quarterly_data.get(f"{year}-Q3", 0)
        quarterly_data[f"{year}-Q4"] = str(int(net_income) - (int(q1) + int(q2) + int(q3)))

# Convert dictionary to DataFrame
quarterly_df = pd.DataFrame(list(quarterly_data.items()), columns=["Quarter", "NetIncome"]).sort_values("Quarter")

# Display properly formatted quarterly data
print(quarterly_df)


final_quarterly_income = quarterly_df
final_quarterly_income["NetIncome"] = pd.to_numeric(final_quarterly_income["NetIncome"], errors='coerce')

mean_income = final_quarterly_income["NetIncome"].mean()
std_income = final_quarterly_income["NetIncome"].std()

# Compute Z-score for each quarter
final_quarterly_income["Z-Score"] = (final_quarterly_income["NetIncome"] - mean_income) / std_income

# Define anomaly threshold (Z-score > 3 or < -3)
final_quarterly_income["Anomaly"] = final_quarterly_income["Z-Score"].abs() > 3

# Display results
print(final_quarterly_income)

# Show only anomalous values
anomalies = final_quarterly_income[final_quarterly_income["Anomaly"]]
print("\nAnomalous Quarters Detected:")
print(anomalies)

# Compute Risk Score: Normalize Z-score to a 0-100 scale
final_quarterly_income["RiskScore"] = final_quarterly_income["Z-Score"].abs() * 20  # Adjust scaling factor

# Cap the risk score at 100
final_quarterly_income["RiskScore"] = final_quarterly_income["RiskScore"].clip(0, 100)

# Categorize Risk Levels
def categorize_risk(score):
    if score >= 80:
        return "High Risk"
    elif score >= 50:
        return "Medium Risk"
    else:
        return "Low Risk"

final_quarterly_income["RiskLevel"] = final_quarterly_income["RiskScore"].apply(categorize_risk)

# Display updated dataframe
print(final_quarterly_income)

# Generate Explanation using Mistral-7B
anomalies = final_quarterly_income[final_quarterly_income["Anomaly"]]

if anomalies.empty:
    explanation = "No significant anomalies were detected in the quarterly income data. The financial data appears stable."
else:
    explanation = "Anomalies detected in the following quarters:\n"
    
    for index, row in anomalies.iterrows():
        explanation += f"- {row['Quarter']}: Net Income = {row['NetIncome']}, Z-Score = {row['Z-Score']:.2f}, Risk Score = {row['RiskScore']:.1f} ({row['RiskLevel']})\n"

    explanation += "\nA higher risk score suggests significant deviation from normal income trends, indicating potential financial inconsistencies or external influences."

print("\nGenerated Explanation:\n")
print(explanation)

def fetch_income_anomaly():
    return { "Data": final_quarterly_income, "Explanation": explanation}
