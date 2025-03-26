import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { IncomeService } from 'src/app/services/income.service';
import { Chart, ChartOptions, ChartType, registerables } from 'chart.js';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  // imports: [CommonModule]
})


export class DashboardComponent implements OnInit, AfterViewInit{
  @ViewChild('lineChart', { static: false }) lineChartRef!: ElementRef;
  chart!: Chart;
  newIncome: number = 0;
  anomalyResult: any;
  
  incomeData: any[] = []; 
  

  constructor(private incomeService: IncomeService, private http: HttpClient ) {
    
      Chart.register(...registerables); // ✅ Register all required components
    
  }

  ngOnInit(): void {
    this.incomeService.getIncomeData().subscribe(
      (      data: any[]) => {
        this.incomeData = data;
        console.log('Income Data:', this.incomeData); // Debugging
        if (this.chart) {
          this.updateChart();
        }
      },
      (      error: any) => console.error('Error fetching data:', error)
    );  
  }  

  ngAfterViewInit() {
    if (this.lineChartRef) {
      this.createLineChart();
    } else {
      console.error("Canvas element not found");
    }
  }

  createLineChart() {
    const ctx = this.lineChartRef.nativeElement.getContext('2d');
    if (!ctx) {
      console.error("Unable to get 2D context for canvas");
      return;
    }

    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Net Income',
            data: [],
            borderColor: 'blue',
            backgroundColor: 'rgba(63, 81, 181, 0.2)',
            fill: true,
            tension: 0.4
          },          
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  updateChart() {
    // Extract labels (e.g., quarter names) and data from API response
    this.chart.data.labels = this.incomeData.map(item => item.Quarter);
    this.chart.data.datasets[0].data = this.incomeData.map(item => item.NetIncome);

    this.chart.update(); // Refresh chart with new data
  }

  submitIncome() {
    if (this.newIncome === null) return;

    const payload = { new_income: this.newIncome };

    this.http.post('http://localhost:5000/income/new/anomaly', payload).subscribe(
      (response) => {
        this.anomalyResult = response;  // Store response in variable
        console.log(this.anomalyResult);
      },
      (error) => {
        console.error('Error:', error);
      }
    );
  }
}
