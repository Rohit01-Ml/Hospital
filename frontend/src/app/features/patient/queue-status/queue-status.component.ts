import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { MyQueueStatus, QueueStatus } from '../../../shared/models/models';

@Component({
  selector: 'app-queue-status',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './queue-status.component.html',
  styleUrls: ['./queue-status.component.scss']
})
export class QueueStatusComponent implements OnInit, OnDestroy {
  private api   = inject(ApiService);
  private route = inject(ActivatedRoute);

  doctorId = '';
  loading  = signal(true);
  myStatus = signal<MyQueueStatus | null>(null);
  queue    = signal<QueueStatus | null>(null);
  private sub?: Subscription;

  ngOnInit() {
    this.doctorId = this.route.snapshot.paramMap.get('doctorId')!;
    this.load();
    // Auto-refresh every 15s
    this.sub = interval(15000).pipe(
      switchMap(() => this.api.getQueue(this.doctorId))
    ).subscribe(q => this.queue.set(q));
  }

  load() {
    this.loading.set(true);
    this.api.getMyQueueStatus(this.doctorId).subscribe({
      next: s => { this.myStatus.set(s); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
    this.api.getQueue(this.doctorId).subscribe(q => this.queue.set(q));
  }

  ngOnDestroy() { this.sub?.unsubscribe(); }

  formatWait(minutes: number): string {
    if (!minutes || minutes <= 0) return '0m';
    if (minutes < 60) return `${minutes}m`;
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  }

  get progressPct() {
    const q = this.queue();
    if (!q || !q.total_patients) return 0;
    return Math.round((q.current_token / q.total_patients) * 100);
  }
}
