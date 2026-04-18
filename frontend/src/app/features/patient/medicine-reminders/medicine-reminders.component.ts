import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { ApiService } from '../../../core/services/api.service';
import { MedicineReminder } from '../../../shared/models/models';

@Component({
  selector: 'app-medicine-reminders',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule, MatChipsModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatSlideToggleModule, MatProgressSpinnerModule, MatDividerModule],
  templateUrl: './medicine-reminders.component.html',
  styleUrls: ['./medicine-reminders.component.scss']
})
export class MedicineRemindersComponent implements OnInit {
  api = inject(ApiService);
  fb = inject(FormBuilder);
  reminders = signal<MedicineReminder[]>([]);
  loading = signal(true);
  saving = signal(false);
  showForm = signal(false);
  editingId = signal<string | null>(null);

  frequencyOptions = ['Once daily', 'Twice daily', 'Three times daily', 'Every 6 hours', 'Every 8 hours', 'As needed'];
  timeOptions = ['Morning (8:00 AM)', 'Afternoon (2:00 PM)', 'Evening (6:00 PM)', 'Night (10:00 PM)', 'Before breakfast', 'After breakfast', 'Before lunch', 'After lunch', 'Before dinner', 'After dinner'];

  form = this.fb.group({
    medicine_name: ['', Validators.required],
    dosage: ['', Validators.required],
    frequency: ['', Validators.required],
    times: [[] as string[], Validators.required],
    start_date: ['', Validators.required],
    end_date: [''],
    instructions: ['']
  });

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getMedicineReminders().subscribe({
      next: data => { this.reminders.set(data); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  openAdd() { this.form.reset(); this.editingId.set(null); this.showForm.set(true); }

  edit(r: MedicineReminder) {
    this.form.patchValue({ ...r, times: r.times, end_date: r.end_date ?? '' });
    this.editingId.set(r.id);
    this.showForm.set(true);
  }

  save() {
    if (this.form.invalid) return;
    this.saving.set(true);
    const payload = { ...this.form.value, times: this.form.value.times || [] };
    const op = this.editingId()
      ? this.api.updateReminder(this.editingId()!, payload)
      : this.api.createReminder(payload);
    op.subscribe({
      next: () => { this.saving.set(false); this.showForm.set(false); this.load(); },
      error: () => this.saving.set(false)
    });
  }

  toggle(r: MedicineReminder) {
    this.api.updateReminder(r.id, { ...r, active: !r.active }).subscribe(() => this.load());
  }

  delete(id: string) {
    if (!confirm('Delete this reminder?')) return;
    this.api.deleteReminder(id).subscribe(() => this.load());
  }

  cancel() { this.showForm.set(false); }
}
