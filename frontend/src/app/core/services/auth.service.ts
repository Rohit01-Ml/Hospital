import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { AuthResponse, User } from '../../shared/models/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = 'http://localhost:8000';
  private _user = signal<User | null>(this.loadUser());
  readonly user      = this._user.asReadonly();
  readonly isLoggedIn      = computed(() => !!this._user());
  readonly isAdmin         = computed(() => this._user()?.role === 'admin');
  readonly isPatient       = computed(() => this._user()?.role === 'patient');
  readonly isDoctor        = computed(() => this._user()?.role === 'doctor');
  readonly isReceptionist  = computed(() => this._user()?.role === 'receptionist');

  constructor(private http: HttpClient, private router: Router) {}

  private loadUser(): User | null {
    try { return JSON.parse(localStorage.getItem('hms_user') || 'null'); }
    catch { return null; }
  }

  private persist(res: AuthResponse) {
    localStorage.setItem('hms_token', res.access_token);
    localStorage.setItem('hms_user', JSON.stringify(res.user));
    this._user.set(res.user);
  }

  getToken() { return localStorage.getItem('hms_token'); }

  login(email: string, password: string) {
    return this.http.post<AuthResponse>(`${this.API}/auth/login`, { email, password })
      .pipe(tap(res => this.persist(res)));
  }

  register(name: string, email: string, password: string, role = 'patient') {
    return this.http.post<AuthResponse>(`${this.API}/auth/register`, { name, email, password, role })
      .pipe(tap(res => this.persist(res)));
  }

  googleLogin(email: string, name: string) {
    return this.http.post<AuthResponse>(`${this.API}/auth/google`, { token: 'mock', email, name })
      .pipe(tap(res => this.persist(res)));
  }

  logout() {
    localStorage.removeItem('hms_token');
    localStorage.removeItem('hms_user');
    this._user.set(null);
    this.router.navigate(['/']);
  }

  redirectByRole() {
    const role = this._user()?.role;
    if (role === 'admin')             this.router.navigate(['/admin']);
    else if (role === 'doctor')       this.router.navigate(['/doctor']);
    else if (role === 'receptionist') this.router.navigate(['/receptionist']);
    else                              this.router.navigate(['/patient']);
  }
}
