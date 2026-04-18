import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatDialogModule } from '@angular/material/dialog';
import { ApiService } from '../../../core/services/api.service';
import { LabTestType, LabBooking } from '../../../shared/models/models';

@Component({
  selector: 'app-lab-tests',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule, MatChipsModule,
    MatFormFieldModule, MatSelectModule, MatInputModule,
    MatProgressSpinnerModule, MatTabsModule, MatDividerModule, MatDialogModule],
  templateUrl: './lab-tests.component.html',
  styleUrls: ['./lab-tests.component.scss']
})
export class LabTestsComponent implements OnInit {
  api = inject(ApiService);
  fb = inject(FormBuilder);
  testTypes = signal<LabTestType[]>([]);
  bookings = signal<LabBooking[]>([]);
  loading = signal(true);
  booking = signal(false);
  showForm = signal(false);

  form = this.fb.group({
    test_type_id: ['', Validators.required],
    notes: ['']
  });

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    Promise.all([
      new Promise<void>(res => this.api.getLabTestTypes().subscribe(d => { this.testTypes.set(d); res(); })),
      new Promise<void>(res => this.api.getLabBookings().subscribe(d => { this.bookings.set(d); res(); }))
    ]).then(() => this.loading.set(false));
  }

  book() {
    if (this.form.invalid) return;
    this.booking.set(true);
    this.api.bookLabTest(this.form.value).subscribe({
      next: () => { this.booking.set(false); this.showForm.set(false); this.form.reset(); this.load(); },
      error: () => this.booking.set(false)
    });
  }

  cancel(id: string) {
    if (!confirm('Cancel this lab test booking?')) return;
    this.api.cancelLabBooking(id).subscribe(() => this.load());
  }

  statusColor(s: string) {
    const m: any = { pending: 'warn', sample_collected: 'accent', processing: 'primary', report_ready: 'primary', cancelled: '' };
    return m[s] || 'primary';
  }

  getType(id: string) {
    return this.testTypes().find(t => t.id === id);
  }
}
