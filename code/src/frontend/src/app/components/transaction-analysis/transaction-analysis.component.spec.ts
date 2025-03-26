import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransactionAnalysisComponent } from './transaction-analysis.component';

describe('TransactionAnalysisComponent', () => {
  let component: TransactionAnalysisComponent;
  let fixture: ComponentFixture<TransactionAnalysisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TransactionAnalysisComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TransactionAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
