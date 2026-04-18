import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';
import { LabTestType, LabBooking } from '../../../shared/models/models';

@Component({
  selector: 'app-admin-lab-tests',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatTableModule, MatChipsModule, MatProgressSpinnerModule,
    MatTabsModule, MatTooltipModule],
  templateUrl: './admin-lab-tests.component.html',
  styleUrls: ['./admin-lab-tests.component.scss']
})
export class AdminLabTestsComponent implements OnInit {
  api = inject(ApiService);
  fb = inject(FormBuilder);
  types = signal<LabTestType[]>([]);
  bookings = signal<LabBooking[]>([]);
  loading = signal(true);
  saving = signal(false);
  editingId = signal<string | null>(null);
  showForm = signal(false);
  typeCols = ['name', 'category', 'price', 'turnaround', 'actions'];
  bookingCols = ['patient', 'test', 'status', 'payment', 'date', 'actions'];
  statusOptions = ['pending', 'sample_collected', 'processing', 'report_ready', 'cancelled'];
  categories = ['Hematology', 'Biochemistry', 'Microbiology', 'Radiology', 'Pathology', 'Immunology', 'Genetics'];

  form = this.fb.group({
    name: ['', Validators.required],
    description: [''],
    price: [0, [Validators.required, Validators.min(0)]],
    turnaround_hours: [24, [Validators.required, Validators.min(1)]],
    category: ['', Validators.required]
  });

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    Promise.all([
      new Promise<void>(r => this.api.getLabTestTypes().subscribe(d => { this.types.set(d); r(); })),
      new Promise<void>(r => this.api.getLabBookings().subscribe(d => { this.bookings.set(d); r(); }))
    ]).then(() => this.loading.set(false));
  }

  openAdd() { this.form.reset({ price: 0, turnaround_hours: 24 }); this.editingId.set(null); this.showForm.set(true); }

  openEdit(t: LabTestType) {
    this.form.patchValue(t);
    this.editingId.set(t.id);
    this.showForm.set(true);
  }

  save() {
    if (this.form.invalid) return;
    this.saving.set(true);
    const op = this.editingId()
      ? this.api.updateLabTestType(this.editingId()!, this.form.value)
      : this.api.createLabTestType(this.form.value);
    op.subscribe({
      next: () => { this.saving.set(false); this.showForm.set(false); this.load(); },
      error: () => this.saving.set(false)
    });
  }

  delete(id: string) {
    if (!confirm('Delete this test type?')) return;
    this.api.deleteLabTestType(id).subscribe(() => this.load());
  }

  updateStatus(id: string, status: string) {
    this.api.updateLabBookingStatus(id, { status }).subscribe(() => this.load());
  }

  statusColor(s: string) {
    const m: any = { pending: '#ff9800', sample_collected: '#0097a7', processing: '#1565c0', report_ready: '#4caf50', cancelled: '#f44336' };
    return m[s] || '#616161';
  }

  cancel() { this.showForm.set(false); }
}
