import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { ApiService } from '../../../core/services/api.service';
import { Doctor, Specialization } from '../../../shared/models/models';

@Component({
  selector: 'app-doctors',
  standalone: true,
  imports: [
    CommonModule, FormsModule, ReactiveFormsModule,
    MatButtonModule, MatIconModule, MatDialogModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatProgressSpinnerModule, MatSnackBarModule, MatSlideToggleModule
  ],
  templateUrl: './doctors.component.html',
  styleUrls: ['./doctors.component.scss']
})
export class DoctorsComponent implements OnInit {
  private api   = inject(ApiService);
  private snack = inject(MatSnackBar);
  private fb    = inject(FormBuilder);

  loading       = signal(true);
  doctors       = signal<Doctor[]>([]);
  specs         = signal<Specialization[]>([]);
  showForm      = signal(false);
  editingDoc    = signal<Doctor | null>(null);
  submitting    = signal(false);

  form = this.fb.group({
    name:              ['', [Validators.required]],
    specialization_id: ['', [Validators.required]],
    experience_years:  [0,  [Validators.required, Validators.min(0)]],
    qualification:     ['', [Validators.required]],
    phone:             [''],
    email:             ['', [Validators.email]],
    bio:               [''],
    available:         [true]
  });

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getDoctors().subscribe(docs => { this.doctors.set(docs); this.loading.set(false); });
    this.api.getSpecializations().subscribe(s => this.specs.set(s));
  }

  openAdd() {
    this.editingDoc.set(null);
    this.form.reset({ available: true, experience_years: 0 });
    this.showForm.set(true);
  }

  openEdit(doc: Doctor) {
    this.editingDoc.set(doc);
    this.form.patchValue(doc);
    this.showForm.set(true);
  }

  closeForm() { this.showForm.set(false); }

  submit() {
    if (this.form.invalid) return;
    this.submitting.set(true);
    const data = this.form.value as any;
    const req$ = this.editingDoc()
      ? this.api.updateDoctor(this.editingDoc()!.id, data)
      : this.api.createDoctor(data);
    req$.subscribe({
      next: () => {
        this.submitting.set(false);
        this.snack.open(this.editingDoc() ? 'Doctor updated' : 'Doctor added', '', { duration: 2500, panelClass: 'snack-success' });
        this.closeForm(); this.load();
      },
      error: err => {
        this.submitting.set(false);
        this.snack.open(err.error?.detail || 'Error saving doctor', '', { duration: 3000, panelClass: 'snack-error' });
      }
    });
  }

  delete(doc: Doctor) {
    if (!confirm(`Delete Dr. ${doc.name}?`)) return;
    this.api.deleteDoctor(doc.id).subscribe({
      next: () => { this.snack.open('Doctor deleted', '', { duration: 2500 }); this.load(); },
      error: () => this.snack.open('Failed to delete', '', { duration: 2500, panelClass: 'snack-error' })
    });
  }

  specName(id: string) { return this.specs().find(s => s.id === id)?.name || id; }
}
