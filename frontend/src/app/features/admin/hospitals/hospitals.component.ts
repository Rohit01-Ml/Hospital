import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';
import { Hospital } from '../../../shared/models/models';

@Component({
  selector: 'app-hospitals',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MatCardModule,
    MatButtonModule, MatIconModule, MatFormFieldModule, MatInputModule,
    MatSelectModule, MatProgressSpinnerModule, MatChipsModule,
    MatDividerModule, MatTooltipModule],
  templateUrl: './hospitals.component.html',
  styleUrls: ['./hospitals.component.scss']
})
export class HospitalsComponent implements OnInit {
  api = inject(ApiService);
  fb  = inject(FormBuilder);

  loading  = signal(true);
  saving   = signal(false);
  showForm = signal(false);
  hospitals = signal<Hospital[]>([]);
  plans     = signal<any[]>([]);

  form = this.fb.group({
    name:      ['', Validators.required],
    address:   ['', Validators.required],
    phone:     ['', Validators.required],
    email:     ['', [Validators.required, Validators.email]],
    plan:      ['starter', Validators.required],
    subdomain: ['', Validators.required],
  });

  ngOnInit() {
    this.api.getPlans().subscribe(p => this.plans.set(Object.entries(p).map(([key, val]: any) => ({ key, ...val }))));
    this.api.getHospitals().subscribe({
      next: h  => { this.hospitals.set(h); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  openNew() { this.form.reset({ plan: 'starter' }); this.showForm.set(true); }

  cancel() { this.showForm.set(false); }

  save() {
    if (this.form.invalid) return;
    this.saving.set(true);
    this.api.createHospital(this.form.value).subscribe({
      next: (h) => {
        this.hospitals.update(list => [h, ...list]);
        this.saving.set(false);
        this.showForm.set(false);
      },
      error: () => this.saving.set(false)
    });
  }

  planColor(plan: string): string {
    const m: any = { starter: '#0097a7', professional: '#1565c0', enterprise: '#7b1fa2' };
    return m[plan] || '#616161';
  }

  planLabel(plan: string): string {
    const m: any = { starter: 'Starter', professional: 'Professional', enterprise: 'Enterprise' };
    return m[plan] || plan;
  }
}
