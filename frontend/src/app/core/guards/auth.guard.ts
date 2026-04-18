import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isLoggedIn()) return true;
  router.navigate(['/login']);
  return false;
};

export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isAdmin()) return true;
  if (auth.isDoctor())            router.navigate(['/doctor']);
  else if (auth.isReceptionist()) router.navigate(['/receptionist']);
  else if (auth.isLoggedIn())     router.navigate(['/patient']);
  else                            router.navigate(['/login']);
  return false;
};

export const patientGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isPatient()) return true;
  if (auth.isDoctor())            router.navigate(['/doctor']);
  else if (auth.isAdmin())        router.navigate(['/admin']);
  else if (auth.isReceptionist()) router.navigate(['/receptionist']);
  else                            router.navigate(['/login']);
  return false;
};

export const doctorGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isDoctor()) return true;
  if (auth.isAdmin())             router.navigate(['/admin']);
  else if (auth.isReceptionist()) router.navigate(['/receptionist']);
  else if (auth.isLoggedIn())     router.navigate(['/patient']);
  else                            router.navigate(['/login']);
  return false;
};

export const receptionistGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isReceptionist()) return true;
  if (auth.isAdmin())         router.navigate(['/admin']);
  else if (auth.isDoctor())   router.navigate(['/doctor']);
  else if (auth.isLoggedIn()) router.navigate(['/patient']);
  else                        router.navigate(['/login']);
  return false;
};

export const publicGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  if (!auth.isLoggedIn()) return true;
  auth.redirectByRole();
  return false;
};
