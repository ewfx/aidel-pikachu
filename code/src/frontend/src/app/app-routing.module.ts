import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { SecFlagsComponent } from './components/sec-flags/sec-flags.component';
import { TransactionAnalysisComponent } from './components/transaction-analysis/transaction-analysis.component';

const routes: Routes = [
  { path: 'dashboard', component: DashboardComponent },
  { path: 'transaction', component: TransactionAnalysisComponent },
  { path: 'sec-flags', component: SecFlagsComponent },
  { path: 'upload', component: FileUploadComponent },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' } // Default route
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
