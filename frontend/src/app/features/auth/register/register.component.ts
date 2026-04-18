import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, RouterLink,
    MatFormFieldModule, MatInputModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, MatSnackBarModule, MatSelectModule
  ],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);
  private snack = inject(MatSnackBar);

  loading = signal(false);
  hidePass = signal(true);

  form = this.fb.group({
    name:     ['', [Validators.required, Validators.minLength(2)]],
    email:    ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    role:     ['patient', Validators.required]
  });

  submit() {
    if (this.form.invalid) return;
    this.loading.set(true);
    const { name, email, password, role } = this.form.value;
    this.auth.register(name!, email!, password!, role!).subscribe({
      next: res => {
        this.loading.set(false);
        this.snack.open(`Welcome, ${res.user.name}! Account created.`, '', { duration: 2500, panelClass: 'snack-success' });
        this.router.navigate([res.user.role === 'admin' ? '/admin' : '/patient']);
      },
      error: err => {
        this.loading.set(false);
        this.snack.open(err.error?.detail || 'Registration failed', '', { duration: 3000, panelClass: 'snack-error' });
      }
    });
  }
}
