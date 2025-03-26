import { Component, OnInit } from '@angular/core';
import { HttpEventType, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FileUploadService } from 'src/app/services/file-upload.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  
})
export class FileUploadComponent implements OnInit {
  currentFile?: File;
  progress = 0;
  message = '';
  responseAvailable = false;
  // responseText: string = '';
  fileName = 'Select File';
  fileInfos?: Observable<any>;
  generatedAnalysis: any = null;
  loanData: any = null;
  performanceData: any = null;
  riskData: any = null;
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
  intervalId: any;
  isRiskExpanded = false; // Controls expansion of the Risk card
  isPerformanceExpanded = false;
  isLoanTableExpanded = false;
  isEntityRiskExpanded = false;  

  constructor(private uploadService: FileUploadService, private sanitizer: DomSanitizer) { }

  ngOnInit(): void {
    this.fileInfos = this.uploadService.getFiles();
  }

  getFormattedEntityAnalysisText(): SafeHtml {
    if (!this.generatedAnalysis?.EntityAnalysis?.Text) return '';    
    // Convert **bold** to <b> HTML
    let formattedText = this.generatedAnalysis.EntityAnalysis.Text
        .replace(/\*\*(.*?)\*\*/g, '<div><b>$1</b></div>') // Bold text in a new line
        .replace(/\n/g, '<br>'); // Preserve new lines  
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }

  getFormattedRiskText(): SafeHtml {
    if (!this.generatedAnalysis?.Risk?.Text) return '';    
    // Convert **bold** to <b> HTML
    const formattedText = this.generatedAnalysis.Risk.Text
          .replace(/\*\*(.*?)\*\*/g, '<div><b>$1</b></div>') // Bold text in a new line
          .replace(/\n/g, '<br>'); // Preserve new lines    
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }

  getFormattedPerfomanceText(): SafeHtml {
    if (!this.generatedAnalysis?.Performance?.Text) return '';    
    // Convert **bold** to <b> HTML
    const formattedText = this.generatedAnalysis.Performance.Text
        .replace(/\*\*(.*?)\*\*/g, '<div><b>$1</b></div>') // Bold text in a new line
        .replace(/\n/g, '<br>'); // Preserve new lines     
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }

  getFormattedLoanTableText(): SafeHtml {
    if (!this.generatedAnalysis?.LoanTable?.Text) return '';    
    // Convert **bold** to <b> HTML
    const formattedText = this.generatedAnalysis.LoanTable.Text
        .replace(/\*\*(.*?)\*\*/g, '<div><b>$1</b></div>') // Bold text in a new line
        .replace(/\n/g, '<br>'); // Preserve new lines    
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }

  selectFile(event: any): void {
    if (event.target.files && event.target.files[0]) {
      const file: File = event.target.files[0];
      this.currentFile = file;
      this.fileName = this.currentFile.name;
    } else {
      this.fileName = 'Select File';
    }
  }

  toggleRiskCard() {
    this.isRiskExpanded = !this.isRiskExpanded;
  }

  toggleEntityRiskCard() {
    this.isEntityRiskExpanded = !this.isEntityRiskExpanded;
  }

  togglePerformanceCard() {
    this.isPerformanceExpanded = !this.isPerformanceExpanded;
  }  
  toggleLoanTableCard() {
    this.isLoanTableExpanded = !this.isLoanTableExpanded;
  }

  startLoading() {
    this.isLoading = true;
    let index = 0;
  
    const interval = setInterval(() => {
      this.loadingMessage = this.statusUpdates[index];
      index = (index + 1) % this.statusUpdates.length;
    }, 10000); // Change message every 2 seconds
  
    return interval; // Return the interval ID to stop it later
  }

  upload(): void {
    this.progress = 0;
    this.message = "";

    this.isLoading = true;
    this.loadingMessage = 'Starting analysis...';

    const interval = this.startLoading(); // Start loader    

    this.generatedAnalysis = null; // Ensure old data is cleared
  
    if (this.currentFile) {
      this.uploadService.upload(this.currentFile).subscribe(
        (event: any) => {
          if (event.type === HttpEventType.UploadProgress) {
            this.progress = Math.round(100 * event.loaded / event.total);
          } else if (event instanceof HttpResponse) {
            // Handle successful upload response
            const responseBody = event.body;  
            // Extract generated_text safely
            // this.generatedAnalysis = responseBody?.generated_text?.[0]?.generated_text || "No analysis generated.";
            this.message = "File uploaded successfully!";
            this.fileInfos = this.uploadService.getFiles();
            this.generatedAnalysis = responseBody;            
            this.isLoading = false;
            this.responseAvailable = true;
            clearInterval(interval);
          }
          
        },
        (err: any) => {
          console.error("Upload error:", err);
          this.progress = 0;
          this.message = err.error?.message || "Could not upload the file!";
          this.currentFile = undefined;
          this.isLoading = false;
          clearInterval(interval);
        }
      );
    }
  }
  
}