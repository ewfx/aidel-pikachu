import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class IncomeService {
  private apiUrl = 'http://localhost:5000/income/anomaly'; // Adjust URL if needed

  constructor(private http: HttpClient) {}

  getIncomeData(): Observable<any[]> {
    return this.http.get<{ Data: string; Explanation: string }>(this.apiUrl).pipe(
      map(response => JSON.parse(response.Data)) // Parse JSON string into an array
    );
  }
}
