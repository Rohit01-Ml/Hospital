import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-queue-overview',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressSpinnerModule, MatSnackBarModule],
  templateUrl: './queue-overview.component.html',
  styleUrls: ['./queue-overview.component.scss']
})
export class QueueOverviewComponent implements OnInit, OnDestroy {
  api          = inject(ApiService);
  snack        = inject(MatSnackBar);
  loading      = signal(true);
  queues       = signal<any[]>([]);
  doctorQueues = signal<Record<string, any>>({});
  expandedDoc  = signal<string | null>(null);
  actionLoading = signal<string | null>(null);
  lastUpdated  = signal('');
  countdown    = signal(15);

  private timer?: Subscription;

  ngOnInit() {
    this.load();
    this.timer = interval(1000).subscribe(() => {
      this.countdown.update(c => {
        if (c <= 1) { this.load(); return 15; }
        return c - 1;
      });
    });
  }

  ngOnDestroy() { this.timer?.unsubscribe(); }

  load() {
    this.api.getQueueOverview().subscribe(q => {
      this.queues.set(q);
      this.loading.set(false);
      this.lastUpdated.set(new Date().toLocaleTimeString());
      const docId = this.expandedDoc();
      if (docId) this.loadDoctorQueue(docId, false);
    });
  }

  loadDoctorQueue(docId: string, showLoading = true) {
    if (showLoading) this.actionLoading.set('loading_' + docId);
    this.api.getReceptionistDoctorQueue(docId).subscribe({
      next: data => {
        this.doctorQueues.update(m => ({ ...m, [docId]: data }));
        if (showLoading) this.actionLoading.set(null);
      },
      error: () => { if (showLoading) this.actionLoading.set(null); }
    });
  }

  toggleExpand(docId: string) {
    if (this.expandedDoc() === docId) {
      this.expandedDoc.set(null);
    } else {
      this.expandedDoc.set(docId);
      this.loadDoctorQueue(docId);
    }
  }

  callNext(docId: string) {
    this.actionLoading.set('next_' + docId);
    this.api.receptionistNextPatient(docId).subscribe({
      next: res => {
        this.snack.open(res.message || 'Next patient called', '', { duration: 3000 });
        this.actionLoading.set(null);
        this.load();
      },
      error: err => {
        this.snack.open(err.error?.detail || 'Failed to call next', '', { duration: 3000 });
        this.actionLoading.set(null);
      }
    });
  }

  setStatus(aptId: string, status: string, docId: string) {
    this.actionLoading.set(aptId);
    const labels: Record<string, string> = {
      in_progress: 'Patient marked as consulting',
      completed: 'Appointment completed',
      cancelled: 'Appointment cancelled',
      waiting: 'Moved back to waiting',
    };
    this.api.receptionistUpdateAptStatus(aptId, status).subscribe({
      next: () => {
        this.snack.open(labels[status] || 'Updated', '', { duration: 2000 });
        this.actionLoading.set(null);
        this.load();
        this.loadDoctorQueue(docId);
      },
      error: err => {
        this.snack.open(err.error?.detail || 'Failed', '', { duration: 3000 });
        this.actionLoading.set(null);
      }
    });
  }

  togglePriority(apt: any, docId: string) {
    this.actionLoading.set('prio_' + apt.id);
    this.api.receptionistTogglePriority(apt.id).subscribe({
      next: res => {
        const msg = res.priority ? '⚡ Marked as Priority — patient will be called next' : 'Priority removed';
        this.snack.open(msg, '', { duration: 3000 });
        this.actionLoading.set(null);
        this.load();
        this.loadDoctorQueue(docId);
      },
      error: err => {
        this.snack.open(err.error?.detail || 'Failed', '', { duration: 3000 });
        this.actionLoading.set(null);
      }
    });
  }

  docQueue(docId: string): any { return this.doctorQueues()[docId]; }

  statusColor(status: string): string {
    return { waiting: 'waiting', in_progress: 'progress', completed: 'done', cancelled: 'cancelled' }[status] ?? '';
  }

  statusLabel(status: string): string {
    return { waiting: 'Waiting', in_progress: 'Consulting', completed: 'Done', cancelled: 'Cancelled' }[status] ?? status;
  }

  isActing(id: string): boolean { return this.actionLoading() === id; }

  formatWait(minutes: number): string {
    if (!minutes || minutes <= 0) return '0m';
    if (minutes < 60) return `${minutes}m`;
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  }
}
