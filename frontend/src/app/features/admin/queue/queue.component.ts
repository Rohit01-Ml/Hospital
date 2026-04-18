import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTabsModule } from '@angular/material/tabs';
import { interval, Subscription } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { Doctor, QueueStatus, Appointment } from '../../../shared/models/models';

@Component({
  selector: 'app-queue',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatButtonModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, MatProgressSpinnerModule,
    MatSnackBarModule, MatTooltipModule, MatTabsModule
  ],
  templateUrl: './queue.component.html',
  styleUrls: ['./queue.component.scss']
})
export class QueueComponent implements OnInit, OnDestroy {
  private api   = inject(ApiService);
  private snack = inject(MatSnackBar);

  loading      = signal(true);
  doctors      = signal<Doctor[]>([]);
  selectedDoc  = signal<string>('');
  queue        = signal<QueueStatus | null>(null);
  acting       = signal(false);
  countdown    = signal(10);
  private sub?: Subscription;
  private tick?: Subscription;

  get selectedDoctor() {
    return this.doctors().find(d => d.id === this.selectedDoc());
  }

  get waiting()    { return this.queue()?.appointments.filter(a => a.status === 'waiting')     ?? []; }
  get inProgress() { return this.queue()?.appointments.filter(a => a.status === 'in_progress') ?? []; }
  get done()       { return this.queue()?.appointments.filter(a => a.status === 'completed' || a.status === 'skipped') ?? []; }

  get progressPct() {
    const q = this.queue();
    if (!q || !q.total_patients) return 0;
    return Math.round((this.done.length / q.total_patients) * 100);
  }

  ngOnInit() {
    this.api.getDoctors().subscribe(docs => {
      this.doctors.set(docs);
      if (docs.length > 0) {
        this.selectedDoc.set(docs[0].id);
        this.loadQueue();
        this.startAutoRefresh();
      }
      this.loading.set(false);
    });
  }

  loadQueue() {
    const docId = this.selectedDoc();
    if (!docId) return;
    this.api.getQueue(docId).subscribe(q => this.queue.set(q));
  }

  onDoctorChange(id: string) {
    this.selectedDoc.set(id);
    this.queue.set(null);
    this.loadQueue();
    this.resetCountdown();
  }

  startAutoRefresh() {
    this.sub?.unsubscribe();
    this.tick?.unsubscribe();
    this.resetCountdown();
    this.tick = interval(1000).subscribe(() => {
      this.countdown.update(n => {
        if (n <= 1) { this.loadQueue(); return 10; }
        return n - 1;
      });
    });
  }

  resetCountdown() { this.countdown.set(10); }

  nextPatient() {
    this.acting.set(true);
    this.api.nextPatient(this.selectedDoc()).subscribe({
      next: res => {
        this.acting.set(false);
        this.snack.open(`✓ ${res.message}`, '', { duration: 2500, panelClass: 'snack-success' });
        this.loadQueue();
      },
      error: () => { this.acting.set(false); this.snack.open('Error calling next patient', '', { duration: 2000 }); }
    });
  }

  skipPatient(apt: Appointment) {
    this.acting.set(true);
    this.api.skipPatient(this.selectedDoc(), apt.id).subscribe({
      next: res => {
        this.acting.set(false);
        this.snack.open(res.message, '', { duration: 2500 });
        this.loadQueue();
      },
      error: () => { this.acting.set(false); }
    });
  }

  completeApt(apt: Appointment) {
    this.acting.set(true);
    this.api.completeAppointment(this.selectedDoc(), apt.id).subscribe({
      next: () => {
        this.acting.set(false);
        this.snack.open('✓ Consultation marked complete', '', { duration: 2500, panelClass: 'snack-success' });
        this.loadQueue();
      },
      error: () => { this.acting.set(false); }
    });
  }

  statusColor(s: string): string {
    const m: any = { waiting: '#f57c00', in_progress: '#1565c0', completed: '#2e7d32', skipped: '#9e9e9e', cancelled: '#c62828' };
    return m[s] || '#616161';
  }

  ngOnDestroy() { this.sub?.unsubscribe(); this.tick?.unsubscribe(); }
}
