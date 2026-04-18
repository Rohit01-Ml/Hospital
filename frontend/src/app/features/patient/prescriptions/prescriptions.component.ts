import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';
import { Prescription } from '../../../shared/models/models';

@Component({
  selector: 'app-prescriptions',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatDividerModule, MatProgressSpinnerModule, MatTooltipModule],
  templateUrl: './prescriptions.component.html',
  styleUrls: ['./prescriptions.component.scss']
})
export class PrescriptionsComponent implements OnInit {
  api = inject(ApiService);
  prescriptions = signal<Prescription[]>([]);
  loading = signal(true);

  ngOnInit() {
    this.api.getPrescriptions().subscribe({
      next: data => { this.prescriptions.set(data); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  printPrescription(rx: Prescription) {
    const today = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
    const followUp = rx.follow_up_date
      ? new Date(rx.follow_up_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })
      : null;

    const medRows = rx.medicines.map((m, i) => `
      <tr>
        <td style="padding:8px 10px;border-bottom:1px solid #f0e6f6;font-weight:500;">${i + 1}. ${m.name}</td>
        <td style="padding:8px 10px;border-bottom:1px solid #f0e6f6;">${m.dosage}</td>
        <td style="padding:8px 10px;border-bottom:1px solid #f0e6f6;">${m.frequency}</td>
        <td style="padding:8px 10px;border-bottom:1px solid #f0e6f6;">${m.duration}</td>
        <td style="padding:8px 10px;border-bottom:1px solid #f0e6f6;color:#555;">${m.instructions}</td>
      </tr>
    `).join('');

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Prescription — ${rx.diagnosis}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #212121; background: #fff; padding: 32px; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #7b1fa2; padding-bottom: 16px; margin-bottom: 20px; }
    .hospital-name { font-size: 22px; font-weight: 800; color: #4a148c; }
    .hospital-sub  { font-size: 12px; color: #888; margin-top: 2px; }
    .rx-badge { font-size: 42px; font-weight: 900; color: #ce93d8; }
    .section-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #7b1fa2; margin: 16px 0 8px; }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
    .info-item label { font-size: 11px; color: #888; display: block; }
    .info-item span  { font-size: 14px; font-weight: 500; }
    .diagnosis-box { background: #f9f0ff; border-left: 4px solid #7b1fa2; padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 16px; font-weight: 600; color: #4a148c; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 16px; }
    thead tr { background: #f3e5f5; }
    th { padding: 8px 10px; text-align: left; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #7b1fa2; }
    .notes-box { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; font-size: 13px; color: #444; margin-bottom: 16px; }
    .followup-box { display: inline-flex; align-items: center; gap: 8px; background: #e8f5e9; color: #2e7d32; border-radius: 8px; padding: 8px 14px; font-size: 13px; font-weight: 600; }
    .footer { margin-top: 32px; border-top: 1px solid #e0e0e0; padding-top: 16px; display: flex; justify-content: space-between; align-items: flex-end; }
    .sig-line { border-top: 1px solid #333; width: 160px; text-align: center; padding-top: 6px; font-size: 12px; color: #888; }
    .print-date { font-size: 11px; color: #aaa; }
    @media print { body { padding: 16px; } }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="hospital-name">MediCare+ Hospital</div>
      <div class="hospital-sub">City General Hospital &bull; 123 Medical Drive &bull; Tel: +1-555-1000</div>
    </div>
    <div class="rx-badge">℞</div>
  </div>

  <div class="info-grid">
    <div class="info-item"><label>Doctor</label><span>${rx.doctor_name}</span></div>
    <div class="info-item"><label>Date</label><span>${new Date(rx.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}</span></div>
    <div class="info-item"><label>Prescription ID</label><span>#${rx.id.toUpperCase()}</span></div>
    <div class="info-item"><label>Appointment</label><span>#${rx.appointment_id}</span></div>
  </div>

  <div class="section-title">Diagnosis</div>
  <div class="diagnosis-box">${rx.diagnosis}</div>

  <div class="section-title">Medicines</div>
  <table>
    <thead>
      <tr>
        <th>Medicine</th><th>Dosage</th><th>Frequency</th><th>Duration</th><th>Instructions</th>
      </tr>
    </thead>
    <tbody>${medRows}</tbody>
  </table>

  ${rx.notes ? `<div class="section-title">Clinical Notes</div><div class="notes-box">${rx.notes}</div>` : ''}

  ${followUp ? `<div class="followup-box">📅 Follow-up: ${followUp}</div>` : ''}

  <div class="footer">
    <div class="print-date">Printed on ${today}</div>
    <div>
      <div class="sig-line">${rx.doctor_name}</div>
    </div>
  </div>
</body>
</html>`;

    const win = window.open('', '_blank', 'width=800,height=900');
    if (!win) return;
    win.document.write(html);
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); }, 400);
  }
}
