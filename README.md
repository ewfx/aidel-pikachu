# 🚀 Project Name

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
1. AI-Powered Entity Risk Detection – Extracts entity names from user-uploaded transactions and runs deep searches across SEC, EDGAR, Wikipedia, and public news databases to assess risk.

 2. Generative AI Risk Scoring – Aggregates all financial intelligence and feeds it into Gemini AI to generate a comprehensive risk score for each entity.

Extra checks:
 3. Advanced Financial Report Analysis – Allows users to upload a company’s annual report for deeper insights, analyzing loan portfolios and financial health beyond database checks.

 4. Mathematical Anomaly Detection – Provides an alternative to AI-based scoring by letting users compare net income trends over previous years, uncovering potential financial manipulations.

 5. Wells Fargo-Specific Customization – As of now the Extra checks are developed to work for Wells Fargo related data

## 🎥 Demo 
📹 [Video Demo](#) - (https://github.com/ewfx/aidel-pikachu/blob/main/artifacts/demo/Demo (1).mp4)

## 💡 Inspiration
Regulatory compliance teams, auditors, and investors struggle to quickly analyze vast amounts of SEC filings and financial transactions. Identifying hidden risks, fraudulent activities, or irregular transactions manually takes days or weeks.

We were inspired to automate this process using GenAI to provide faster, more reliable financial insights and risk analysis.

## ⚙️ What It Does
Our Full-Stack SEC Filing & Financial Transaction Analysis Platform has three core features:

1️⃣ Net Income Analysis Dashboard

   Enter a quarter's net income for Wells Fargo
   
   View trends of quarterly net income trends in the dashboard
   
   View Risk or anomaly for the entered Net Income.

2️⃣ AI-Powered SEC Filing Anomaly Detection

Upload a 10-K, 10-Q, or other SEC filing.

AI scans for unusual risk factors.

Generates AI-driven explanations in simple terms.

3️⃣ Transaction Risk Analysis API 

Input transaction data as a text string (e.g., "Payment of $500,000 to XYZ Corp in Cayman Islands for consulting services").

AI performs:

Risk Scoring (Low, Medium, High) based on transaction patterns.

Entity Classification (e.g., "XYZ Corp" → Offshore Entity).

Anomaly Detection (e.g., Unusual high-value transactions, links to high-risk regions).

AI-Generated Explanation detailing potential compliance concerns.

## 🛠️ How We Built It
Front - End: Angular
Back - End: Flask - Python
GenAI - Gemini
DataSources - SEC EDGAR, NewsAPI, WikiData

## 🚧 Challenges We Faced
 - Analysing large reports of SEC Filing
 - Detecting anomaly for transaction data with accurate confidence score.

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/aidel-pikachu.git
   ```
2. Install dependencies  
   ```sh
   npm install  #front-end directory
   pip install -r requirements.txt #For back-end directory
   ```
3. Run the project  
   ```sh
   npm start  # for starting front-end
   py app.py # for starting back-end
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: Angular
- 🔹 Backend: Flask
- 🔹 Other: Gemini

## 👥 Team
- **Keerthana S** 
- **Manasa R**
- **Sangamesh Davey**
