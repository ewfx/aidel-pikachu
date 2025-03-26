import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecFlagsComponent } from './sec-flags.component';

describe('SecFlagsComponent', () => {
  let component: SecFlagsComponent;
  let fixture: ComponentFixture<SecFlagsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SecFlagsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SecFlagsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
