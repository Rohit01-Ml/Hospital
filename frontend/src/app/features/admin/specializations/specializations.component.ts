import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';
import { Specialization } from '../../../shared/models/models';

@Component({
  selector: 'app-specializations',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule,
    MatButtonModule, MatIconModule, MatFormFieldModule,
    MatInputModule, MatProgressSpinnerModule, MatSnackBarModule
  ],
  templateUrl: './specializations.component.html',
  styleUrls: ['./specializations.component.scss']
})
export class SpecializationsComponent implements OnInit {
  private api   = inject(ApiService);
  private snack = inject(MatSnackBar);
  private fb    = inject(FormBuilder);

  loading    = signal(true);
  specs      = signal<Specialization[]>([]);
  showForm   = signal(false);
  editing    = signal<Specialization | null>(null);
  submitting = signal(false);

  form = this.fb.group({
    name:        ['', Validators.required],
    description: [''],
    icon:        ['local_hospital']
  });

  icons = ['favorite','accessibility_new','psychology','spa','child_care','local_hospital','biotech','science','visibility','hearing'];

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getSpecializations().subscribe(s => { this.specs.set(s); this.loading.set(false); });
  }

  openAdd() {
    this.editing.set(null);
    this.form.reset({ icon: 'local_hospital' });
    this.showForm.set(true);
  }

  openEdit(spec: Specialization) {
    this.editing.set(spec);
    this.form.patchValue(spec);
    this.showForm.set(true);
  }

  submit() {
    if (this.form.invalid) return;
    this.submitting.set(true);
    const data = this.form.value as any;
    const req$ = this.editing()
      ? this.api.updateSpecialization(this.editing()!.id, data)
      : this.api.createSpecialization(data);
    req$.subscribe({
      next: () => {
        this.submitting.set(false);
        this.snack.open(this.editing() ? 'Updated' : 'Created', '', { duration: 2500, panelClass: 'snack-success' });
        this.showForm.set(false); this.load();
      },
      error: err => {
        this.submitting.set(false);
        this.snack.open(err.error?.detail || 'Error', '', { duration: 3000, panelClass: 'snack-error' });
      }
    });
  }

  delete(spec: Specialization) {
    if (!confirm(`Delete "${spec.name}"?`)) return;
    this.api.deleteSpecialization(spec.id).subscribe({
      next: () => { this.snack.open('Deleted', '', { duration: 2500 }); this.load(); },
      error: () => this.snack.open('Failed', '', { duration: 2500, panelClass: 'snack-error' })
    });
  }
}
