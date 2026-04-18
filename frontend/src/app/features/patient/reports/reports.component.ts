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
import { Report } from '../../../shared/models/models';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatProgressSpinnerModule, MatDividerModule, MatTooltipModule],
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent implements OnInit {
  api = inject(ApiService);
  reports = signal<Report[]>([]);
  loading = signal(true);

  ngOnInit() {
    this.api.getReports().subscribe({
      next: data => { this.reports.set(data); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  download(id: string) {
    this.api.downloadReport(id).subscribe(r => alert(r.message || 'Download initiated'));
  }

  statusColor(s: string) {
    return s === 'normal' ? '#4caf50' : s === 'abnormal' ? '#ff9800' : '#f44336';
  }

  statusIcon(s: string) {
    return s === 'normal' ? 'check_circle' : s === 'abnormal' ? 'warning' : 'error';
  }
}
