import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, RouterLink,
    MatFormFieldModule, MatInputModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, MatSnackBarModule, MatDividerModule
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);
  private snack = inject(MatSnackBar);

  loading = signal(false);
  hidePass = signal(true);
  showRecDept = signal(false);

  form = this.fb.group({
    email:    ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(4)]]
  });

  submit() {
    if (this.form.invalid) return;
    this.loading.set(true);
    const { email, password } = this.form.value;
    this.auth.login(email!, password!).subscribe({
      next: res => {
        this.loading.set(false);
        this.snack.open(`Welcome back, ${res.user.name}!`, '', { duration: 2500, panelClass: 'snack-success' });
        this.auth.redirectByRole();
      },
      error: err => {
        this.loading.set(false);
        this.snack.open(err.error?.detail || 'Invalid credentials', '', { duration: 3000, panelClass: 'snack-error' });
      }
    });
  }

  googleLogin() {
    this.loading.set(true);
    this.auth.googleLogin('demo.google@gmail.com', 'Google Demo User').subscribe({
      next: res => {
        this.loading.set(false);
        this.auth.redirectByRole();
      },
      error: () => { this.loading.set(false); }
    });
  }

  fillDemo(role: string) {
    const map: Record<string, {email: string; password: string}> = {
      admin:              { email: 'admin@hospital.com',  password: 'secret' },
      patient:            { email: 'john@example.com',    password: 'secret' },
      doctor:             { email: 'sarah.j@hospital.com',password: 'secret' },
      'rec-cardiology':   { email: 'riya@hospital.com',   password: 'secret' },
      'rec-ortho':        { email: 'priya@hospital.com',  password: 'secret' },
      'rec-neuro':        { email: 'amit@hospital.com',   password: 'secret' },
      'rec-general':      { email: 'sneha@hospital.com',  password: 'secret' },
    };
    if (map[role]) this.form.patchValue(map[role]);
  }
}
