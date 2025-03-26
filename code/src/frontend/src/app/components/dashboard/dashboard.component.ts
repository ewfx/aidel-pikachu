import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { IncomeService } from 'src/app/services/income.service';
import { Chart, ChartOptions, ChartType, registerables } from 'chart.js';
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, AfterViewInit{
  @ViewChild('lineChart', { static: false }) lineChartRef!: ElementRef;
  chart!: Chart;
  
  incomeData: any[] = [];

  constructor(private incomeService: IncomeService, ) {
    
      Chart.register(...registerables); // ✅ Register all required components
    
  }

  ngOnInit(): void {
    this.incomeService.getIncomeData().subscribe(
      (      data: any[]) => {
        this.incomeData = data;
        console.log('Income Data:', this.incomeData); // Debugging
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
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Net Income',
            data: [10, 25, 30, 50, 40, 70, 90],
            borderColor: 'blue',
            backgroundColor: 'rgba(63, 81, 181, 0.2)',
            fill: true,
            tension: 0.4
          },
          {
            label: 'Revenue Growth',
            data: [15, 30, 40, 60, 45, 80, 100],
            borderColor: 'green',
            backgroundColor: 'rgba(76, 175, 80, 0.2)',
            fill: true,
            tension: 0.4
          }
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
}
