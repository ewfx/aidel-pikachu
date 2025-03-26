import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'SEC File Analysis';
  showNavbar = true; // Initially, navbar is visible

  toggleNavbar() {
    this.showNavbar = !this.showNavbar;
  }
}
