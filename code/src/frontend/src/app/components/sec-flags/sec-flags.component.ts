import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-sec-flags',
  templateUrl: './sec-flags.component.html',
  styleUrls: ['./sec-flags.component.css']
})
export class SecFlagsComponent implements OnInit {

  displayedColumns: string[] = ['question', 'answer'];
  flagData: { question: string, answer: string }[] = [];
  questions: string[] = [
    "Loan Portfolio Risk: Has there been a significant shift in the commercial-to-consumer loan ratio or concentration in high-risk sectors (e.g., real estate, auto loans)?",
    "Regulatory & Compliance Issues: Are there any ongoing or newly disclosed investigations, lawsuits, or regulatory penalties that could impact operations?",
    "Credit Loss Provisions: Has the allowance for loan losses increased disproportionately compared to loan growth, signaling potential credit quality issues?",
    "Net Interest Margin (NIM) Trends: Is NIM shrinking, indicating declining profitability due to lower lending rates or higher funding costs?",
    "Efficiency Ratio & Expense Management: Is non-interest expense growing faster than revenue, suggesting operational inefficiencies or excessive legal costs?",
    "Deposit & Liquidity Trends: Are total deposits declining, or is there increased reliance on short-term funding, signaling potential liquidity stress?",
    "Risk Management & Internal Controls: Are there disclosures of weaknesses in internal controls or governance failures that could lead to future compliance breaches?",
    "Executive & Board Stability: Have there been major executive departures, board changes, or unusual insider stock sales that could indicate internal turmoil?",
    "Capital Adequacy & CET1 Ratio: Is Wells Fargo’s Common Equity Tier 1 (CET1) ratio declining, indicating weakening capital reserves to absorb financial shocks?",
    "Reputation & Customer Trust: Is there evidence of reputational damage affecting customer confidence, such as declining consumer deposits or adverse media coverage?"
  ];  
  
  answers: { question: string, answer: string }[] = [];
  loading: boolean = true;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchAnswers();
  }

  fetchAnswers() {
    this.http.get<{ Table_Answers: string }>('http://localhost:5000/table/answers').subscribe(response => {
      if (response && response.Table_Answers) {
        const answerLines = response.Table_Answers.split('\n').filter(line => line.trim() !== '');
        const answers = answerLines.map(line => line.split('. ')[1]?.trim() || 'Unknown');
        console.log(answers);
        this.flagData = this.questions.map((question, index) => ({
          question,
          answer: answers[index] || 'Unknown'
        }));
        this.loading=false;
      }
    });
  }
}
