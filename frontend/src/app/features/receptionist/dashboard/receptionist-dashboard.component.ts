import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-receptionist-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule],
  templateUrl: './receptionist-dashboard.component.html',
  styleUrls: ['./receptionist-dashboard.component.scss']
})
export class ReceptionistDashboardComponent implements OnInit {
  api  = inject(ApiService);
  auth = inject(AuthService);

  loading      = signal(true);
  stats        = signal<any>(null);
  queueOverview = signal<any[]>([]);
  todayApts    = signal<any[]>([]);

  today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  ngOnInit() {
    forkJoin({
      stats: this.api.getReceptionistDashboard(),
      queue: this.api.getQueueOverview(),
      apts:  this.api.getTodayAllAppointments(),
    }).subscribe({
      next: ({ stats, queue, apts }) => {
        this.stats.set(stats);
        this.queueOverview.set(queue);
        this.todayApts.set(apts);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  statusClass(s: string) { return s.replace('_', '-'); }
}
