import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { ApiService } from '../../../core/services/api.service';
import { Notification } from '../../../shared/models/models';

@Component({
  selector: 'app-admin-notifications',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatChipsModule, MatProgressSpinnerModule, MatDividerModule,
    MatTooltipModule, MatSlideToggleModule],
  templateUrl: './admin-notifications.component.html',
  styleUrls: ['./admin-notifications.component.scss']
})
export class AdminNotificationsComponent implements OnInit {
  api = inject(ApiService);
  fb = inject(FormBuilder);
  notifications = signal<Notification[]>([]);
  loading = signal(true);
  sending = signal(false);
  showBroadcast = signal(false);

  broadcastForm = this.fb.group({
    title: ['', Validators.required],
    message: ['', Validators.required],
    type: ['general', Validators.required]
  });

  singleForm = this.fb.group({
    user_id: ['', Validators.required],
    title: ['', Validators.required],
    message: ['', Validators.required],
    type: ['general', Validators.required]
  });

  notifTypes = ['general', 'appointment', 'payment', 'prescription', 'lab_test', 'report', 'medicine'];

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getNotifications().subscribe({
      next: d => { this.notifications.set(d); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  broadcast() {
    if (this.broadcastForm.invalid) return;
    this.sending.set(true);
    this.api.broadcastNotification(this.broadcastForm.value).subscribe({
      next: () => { this.sending.set(false); this.broadcastForm.reset({ type: 'general' }); alert('Broadcast sent!'); this.load(); },
      error: () => this.sending.set(false)
    });
  }

  sendSingle() {
    if (this.singleForm.invalid) return;
    this.sending.set(true);
    this.api.createNotification(this.singleForm.value).subscribe({
      next: () => { this.sending.set(false); this.singleForm.reset({ type: 'general' }); alert('Notification sent!'); this.load(); },
      error: () => this.sending.set(false)
    });
  }

  typeIcon(type: string) {
    const m: any = {
      appointment: 'calendar_today', payment: 'payment',
      prescription: 'description', lab_test: 'biotech',
      report: 'assessment', medicine: 'medication', general: 'info'
    };
    return m[type] || 'notifications';
  }

  typeColor(type: string) {
    const m: any = {
      appointment: '#1976d2', payment: '#388e3c',
      prescription: '#7b1fa2', lab_test: '#0097a7',
      report: '#f57c00', medicine: '#c62828', general: '#616161'
    };
    return m[type] || '#616161';
  }
}
