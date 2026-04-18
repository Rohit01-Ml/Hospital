import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { ApiService } from '../../../core/services/api.service';
import { Appointment } from '../../../shared/models/models';

@Component({
  selector: 'app-my-appointments',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule, MatProgressSpinnerModule, MatSnackBarModule, MatTabsModule],
  templateUrl: './my-appointments.component.html',
  styleUrls: ['./my-appointments.component.scss']
})
export class MyAppointmentsComponent implements OnInit {
  private api   = inject(ApiService);
  private snack = inject(MatSnackBar);

  loading      = signal(true);
  appointments = signal<Appointment[]>([]);

  get upcoming()  { return this.appointments().filter(a => ['waiting','in_progress'].includes(a.status)); }
  get past()      { return this.appointments().filter(a => ['completed','cancelled','skipped'].includes(a.status)); }

  ngOnInit() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.api.getAppointments().subscribe({
      next: apts => { this.appointments.set(apts); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  cancel(apt: Appointment) {
    if (!confirm('Cancel this appointment?')) return;
    this.api.cancelAppointment(apt.id).subscribe({
      next: () => { this.snack.open('Appointment cancelled', '', { duration: 2500 }); this.load(); },
      error: () => this.snack.open('Failed to cancel', '', { duration: 2500, panelClass: 'snack-error' })
    });
  }

  statusClass(s: string) { return s.replace('_', '-'); }
}
