import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-doctor-patients',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule,
    MatProgressSpinnerModule, MatTooltipModule, MatFormFieldModule, MatInputModule],
  templateUrl: './doctor-patients.component.html',
  styleUrls: ['./doctor-patients.component.scss']
})
export class DoctorPatientsComponent implements OnInit {
  api = inject(ApiService);
  patients = signal<any[]>([]);
  loading  = signal(true);
  search   = '';

  ngOnInit() {
    this.api.getDoctorPatients().subscribe({
      next: d => { this.patients.set(d); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  filtered() {
    const q = this.search.toLowerCase();
    return this.patients().filter(p => !q || p.name.toLowerCase().includes(q) || p.email.toLowerCase().includes(q));
  }
}
