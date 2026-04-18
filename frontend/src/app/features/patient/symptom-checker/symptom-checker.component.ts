import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { ApiService } from '../../../core/services/api.service';
import { SymptomCheckResult } from '../../../shared/models/models';

@Component({
  selector: 'app-symptom-checker',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatCardModule, MatButtonModule,
    MatIconModule, MatFormFieldModule, MatInputModule,
    MatProgressSpinnerModule, MatChipsModule, MatDividerModule],
  templateUrl: './symptom-checker.component.html',
  styleUrls: ['./symptom-checker.component.scss']
})
export class SymptomCheckerComponent {
  api = inject(ApiService);

  symptoms = '';
  loading = signal(false);
  result  = signal<SymptomCheckResult | null>(null);
  error   = signal('');

  quickSymptoms = [
    'fever', 'headache', 'chest pain', 'cough', 'stomach pain',
    'back pain', 'skin rash', 'anxiety', 'eye pain', 'joint pain'
  ];

  addQuick(s: string) {
    this.symptoms = this.symptoms ? `${this.symptoms}, ${s}` : s;
  }

  check() {
    if (!this.symptoms.trim()) return;
    this.loading.set(true);
    this.result.set(null);
    this.error.set('');

    this.api.checkSymptoms(this.symptoms).subscribe({
      next: (res) => { this.result.set(res); this.loading.set(false); },
      error: ()  => { this.error.set('Could not analyze symptoms. Please try again.'); this.loading.set(false); }
    });
  }

  reset() {
    this.symptoms = '';
    this.result.set(null);
    this.error.set('');
  }

  confidenceColor(c: number): string {
    if (c >= 0.75) return '#2e7d32';
    if (c >= 0.5)  return '#f57c00';
    return '#c62828';
  }

  confidenceLabel(c: number): string {
    if (c >= 0.75) return 'High match';
    if (c >= 0.5)  return 'Moderate match';
    return 'Possible match';
  }

  confidencePct(c: number): number {
    return Math.round(c * 100);
  }
}
