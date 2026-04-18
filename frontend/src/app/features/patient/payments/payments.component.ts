import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTableModule } from '@angular/material/table';
import { ApiService } from '../../../core/services/api.service';
import { Payment } from '../../../shared/models/models';

@Component({
  selector: 'app-payments',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatProgressSpinnerModule, MatDividerModule,
    MatTooltipModule, MatTableModule],
  templateUrl: './payments.component.html',
  styleUrls: ['./payments.component.scss']
})
export class PaymentsComponent implements OnInit {
  api = inject(ApiService);
  payments = signal<Payment[]>([]);
  loading = signal(true);
  paying = signal<string | null>(null);
  displayedColumns = ['appointment', 'amount', 'status', 'method', 'date', 'actions'];

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getPayments().subscribe({
      next: data => { this.payments.set(data); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  mockPay(aptId: string, payId: string) {
    this.paying.set(payId);
    this.api.mockPay(aptId).subscribe({
      next: () => { this.paying.set(null); this.load(); },
      error: () => this.paying.set(null)
    });
  }

  totalPaid() {
    return this.payments().filter(p => p.status === 'paid').reduce((s, p) => s + p.amount, 0);
  }

  pendingCount() {
    return this.payments().filter(p => p.status === 'pending').length;
  }

  statusColor(s: string) {
    const m: any = { paid: '#4caf50', pending: '#ff9800', failed: '#f44336', refunded: '#9c27b0' };
    return m[s] || '#616161';
  }

  statusIcon(s: string) {
    const m: any = { paid: 'check_circle', pending: 'schedule', failed: 'cancel', refunded: 'replay' };
    return m[s] || 'payment';
  }
}
