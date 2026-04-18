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
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';
import { Report } from '../../../shared/models/models';

@Component({
  selector: 'app-admin-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatTableModule, MatChipsModule, MatProgressSpinnerModule, MatTooltipModule],
  templateUrl: './admin-reports.component.html',
  styleUrls: ['./admin-reports.component.scss']
})
export class AdminReportsComponent implements OnInit {
  api = inject(ApiService);
  fb = inject(FormBuilder);
  reports = signal<Report[]>([]);
  loading = signal(true);
  saving = signal(false);
  showForm = signal(false);
  editingId = signal<string | null>(null);
  displayedColumns = ['title', 'patient', 'status', 'date', 'actions'];
  statusOptions: Array<'normal' | 'abnormal' | 'critical'> = ['normal', 'abnormal', 'critical'];

  form = this.fb.group({
    patient_id: ['', Validators.required],
    title: ['', Validators.required],
    findings: [''],
    interpretation: [''],
    status: ['normal' as 'normal' | 'abnormal' | 'critical', Validators.required],
    file_url: ['']
  });

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getReports().subscribe({
      next: d => { this.reports.set(d); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  openAdd() { this.form.reset({ status: 'normal' }); this.editingId.set(null); this.showForm.set(true); }

  openEdit(r: Report) {
    this.form.patchValue({ ...r, file_url: r.file_url ?? '' });
    this.editingId.set(r.id);
    this.showForm.set(true);
  }

  save() {
    if (this.form.invalid) return;
    this.saving.set(true);
    const payload = { ...this.form.value, uploaded_by: 'admin' };
    const op = this.editingId()
      ? this.api.updateReport(this.editingId()!, payload)
      : this.api.uploadReport(payload);
    op.subscribe({
      next: () => { this.saving.set(false); this.showForm.set(false); this.load(); },
      error: () => this.saving.set(false)
    });
  }

  delete(id: string) {
    if (!confirm('Delete this report?')) return;
    this.api.deleteReport(id).subscribe(() => this.load());
  }

  download(id: string) {
    this.api.downloadReport(id).subscribe(r => alert(r.message || 'Download initiated'));
  }

  statusColor(s: string) {
    return s === 'normal' ? '#4caf50' : s === 'abnormal' ? '#ff9800' : '#f44336';
  }

  cancel() { this.showForm.set(false); }
}
