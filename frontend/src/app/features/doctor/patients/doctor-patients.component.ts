import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatChipsModule } from '@angular/material/chips';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-doctor-patients',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule,
    MatProgressSpinnerModule, MatFormFieldModule, MatInputModule, MatTableModule,
    MatSortModule, MatTooltipModule, MatExpansionModule, MatChipsModule],
  templateUrl: './doctor-patients.component.html',
  styleUrls: ['./doctor-patients.component.scss']
})
export class DoctorPatientsComponent implements OnInit {
  api = inject(ApiService);
  patients   = signal<any[]>([]);
  loading    = signal(true);
  search     = '';
  sortField  = 'last_visit';
  sortDir: 'asc' | 'desc' = 'desc';
  expandedPatient: string | null = null;

  displayedColumns = ['id', 'name', 'email', 'total_visits', 'last_visit', 'prescriptions'];

  ngOnInit() {
    this.api.getDoctorPatients().subscribe({
      next: d => { this.patients.set(d); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  filtered() {
    const q = this.search.toLowerCase();
    let list = this.patients().filter(p =>
      !q || p.name.toLowerCase().includes(q) ||
      p.email.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q)
    );
    return list.sort((a, b) => {
      const av = a[this.sortField] ?? '';
      const bv = b[this.sortField] ?? '';
      return this.sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
  }

  onSort(s: Sort) {
    this.sortField = s.active;
    this.sortDir   = s.direction as 'asc' | 'desc' || 'desc';
  }

  toggleExpand(id: string) {
    this.expandedPatient = this.expandedPatient === id ? null : id;
  }

  printPrescription(presc: any) {
    const win = window.open('', '_blank', 'width=800,height=600');
    if (!win) return;
    const meds = (presc.medicines || []).map((m: any) =>
      `<tr>
        <td>${m.name}</td><td>${m.dosage}</td>
        <td>${m.frequency}</td><td>${m.duration}</td>
        <td>${m.instructions || '-'}</td>
      </tr>`
    ).join('');
    win.document.write(`
      <html><head><title>Prescription</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 32px; color: #111; }
        h2 { color: #1565c0; } h3 { margin-top: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 8px; }
        th { background: #1565c0; color: white; padding: 8px; text-align: left; }
        td { padding: 8px; border-bottom: 1px solid #ddd; }
        .row { display: flex; gap: 32px; margin: 8px 0; }
        .label { font-weight: bold; color: #555; }
        @media print { button { display: none; } }
      </style></head><body>
      <h2>Prescription</h2>
      <div class="row"><span><span class="label">Patient ID:</span> ${presc.patient_id}</span>
        <span><span class="label">Doctor:</span> Dr. ${presc.doctor_name}</span>
        <span><span class="label">Date:</span> ${new Date(presc.created_at).toLocaleDateString()}</span>
      </div>
      <div class="row"><span><span class="label">Diagnosis:</span> ${presc.diagnosis}</span></div>
      <h3>Medicines</h3>
      <table><thead><tr><th>Medicine</th><th>Dosage</th><th>Frequency</th><th>Duration</th><th>Instructions</th></tr></thead>
      <tbody>${meds}</tbody></table>
      ${presc.notes ? `<h3>Notes</h3><p>${presc.notes}</p>` : ''}
      ${presc.follow_up_date ? `<p><span class="label">Follow-up:</span> ${presc.follow_up_date}</p>` : ''}
      <br><button onclick="window.print()">Print</button>
      </body></html>
    `);
    win.document.close();
    win.focus();
    setTimeout(() => win.print(), 500);
  }
}
