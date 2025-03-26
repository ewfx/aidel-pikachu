import { Component, OnInit } from '@angular/core';
import { HttpEventType, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FileUploadService } from 'src/app/services/file-upload.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  
})
export class FileUploadComponent implements OnInit {
  currentFile?: File;
  progress = 0;
  message = '';

  fileName = 'Select File';
  fileInfos?: Observable<any>;
  generatedAnalysis: any = null;

  constructor(private uploadService: FileUploadService) { }

  ngOnInit(): void {
    this.fileInfos = this.uploadService.getFiles();
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

  upload(): void {
    this.progress = 0;
    this.message = "";
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
          }
        },
        (err: any) => {
          console.error("Upload error:", err);
          this.progress = 0;
          this.message = err.error?.message || "Could not upload the file!";
          this.currentFile = undefined;
        }
      );
    }
  }
  
}