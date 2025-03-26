import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-transaction-analysis',
  templateUrl: './transaction-analysis.component.html',
  styleUrls: ['./transaction-analysis.component.css']
})
export class TransactionAnalysisComponent {
  transactionForm = new FormGroup({
    transactionData: new FormControl('')
  });

  isLoading = false;
  loadingMessage = 'Starting analysis...';
  statusUpdates = [
    'Analyzing data...',
    'Fetching financial records...',
    'Running AI risk models...',
    'Cross-checking SEC filings...',
    'Generating insights...',
    'Finalizing results...'
  ];

  responseData: any = null; // Ensure it's an array of objects
  // Store formatted response
  loading: boolean = false;

  constructor(private http: HttpClient, private sanitizer: DomSanitizer) {}


  startLoading() {
    this.isLoading = true;
    let index = 0;
  
    const interval = setInterval(() => {
      this.loadingMessage = this.statusUpdates[index];
      index = (index + 1) % this.statusUpdates.length;
    }, 10000); // Change message every 2 seconds
  
    return interval; // Return the interval ID to stop it later
  }

  submitTransaction() {
    this.loading = true;
    const inputData = this.transactionForm.value.transactionData;
    const interval = this.startLoading(); // Start loader  

    this.http.post('http://localhost:5000/transaction/data', { input: inputData }).subscribe({
      next: (response: any) => {
        console.log(response);
        if (response) {
          console.log(response);
          this.responseData = response.transanction_result; // No need to pre-format here
          console.log(this.responseData);
        } else {
          this.responseData = [];
        }
        this.isLoading = false;
        clearInterval(interval);
      },
      error: (error) => {
        console.error('Error:', error);
        this.responseData = [];
        this.isLoading = false;
        clearInterval(interval);
      }
    });
  }
  
  formatResponse(text: string): SafeHtml {
    if (!text) return '';
  
    let formattedText = text
      .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // **bold** → <b>
      .replace(/\n/g, '<br>'); // \n → <br>
  
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }
}  