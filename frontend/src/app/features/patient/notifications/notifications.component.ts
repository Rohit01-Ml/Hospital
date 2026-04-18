import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';
import { Notification } from '../../../shared/models/models';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatProgressSpinnerModule, MatDividerModule, MatTooltipModule],
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss']
})
export class NotificationsComponent implements OnInit {
  api = inject(ApiService);
  notifications = signal<Notification[]>([]);
  loading = signal(true);

  ngOnInit() { this.load(); }

  load() {
    this.api.getNotifications().subscribe({
      next: data => { this.notifications.set(data); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  markRead(id: string) {
    this.api.markNotificationRead(id).subscribe(() => {
      this.notifications.update(ns => ns.map(n => n.id === id ? { ...n, read: true } : n));
    });
  }

  markAllRead() {
    this.api.markAllRead().subscribe(() => {
      this.notifications.update(ns => ns.map(n => ({ ...n, read: true })));
    });
  }

  unreadCount() {
    return this.notifications().filter(n => !n.read).length;
  }

  typeIcon(type: string) {
    const m: any = {
      appointment: 'calendar_today', payment: 'payment',
      prescription: 'description', lab_test: 'biotech',
      report: 'assessment', medicine: 'medication', general: 'info',
      follow_up: 'event_repeat'
    };
    return m[type] || 'notifications';
  }

  typeColor(type: string) {
    const m: any = {
      appointment: '#1976d2', payment: '#388e3c',
      prescription: '#7b1fa2', lab_test: '#0097a7',
      report: '#f57c00', medicine: '#c62828', general: '#616161',
      follow_up: '#2e7d32'
    };
    return m[type] || '#616161';
  }
}
