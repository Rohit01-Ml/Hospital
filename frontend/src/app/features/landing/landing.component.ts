import { Component, OnInit, OnDestroy, signal, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../core/services/auth.service';

interface Slide {
  title: string;
  subtitle: string;
  cta: string;
  gradient: string;
  icon: string;
}

interface Feature {
  icon: string; title: string; description: string; color: string;
}

interface Stat {
  value: string; label: string; icon: string;
}

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss']
})
export class LandingComponent implements OnInit, OnDestroy {
  auth = inject(AuthService);
  router = inject(Router);

  currentSlide = signal(0);
  private timer: any;

  slides: Slide[] = [
    {
      title: 'Your Health, Our Priority',
      subtitle: 'Book appointments with top specialists in minutes. Zero waiting room surprises.',
      cta: 'Book Appointment',
      gradient: 'linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565c0 100%)',
      icon: 'favorite'
    },
    {
      title: 'Expert Doctors, Seamless Care',
      subtitle: 'Access 50+ specialists across 10 departments with real-time availability.',
      cta: 'Find Doctors',
      gradient: 'linear-gradient(135deg, #004d40 0%, #00695c 50%, #00897b 100%)',
      icon: 'medical_services'
    },
    {
      title: 'Live Queue Tracking',
      subtitle: 'Know exactly when it\'s your turn. Real-time token updates, no guessing.',
      cta: 'Check Queue',
      gradient: 'linear-gradient(135deg, #1b0000 0%, #4a0000 50%, #b71c1c 100%)',
      icon: 'queue'
    },
    {
      title: 'Complete Health Records',
      subtitle: 'Your medical history, appointments, and prescriptions — all in one secure place.',
      cta: 'Get Started',
      gradient: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
      icon: 'health_and_safety'
    }
  ];

  features: Feature[] = [
    { icon: 'event_available', title: 'Smart Scheduling', description: 'Book, reschedule, or cancel appointments with just a few clicks anytime, anywhere.', color: '#3949ab' },
    { icon: 'people', title: 'Queue Management', description: 'Live token tracking shows your position in real time so you never overstay.', color: '#00897b' },
    { icon: 'verified_user', title: 'Secure & Private', description: 'Your data is protected with enterprise-grade encryption and role-based access.', color: '#e53935' },
    { icon: 'star', title: 'Top Specialists', description: 'Choose from a curated list of experienced, board-certified physicians.', color: '#fb8c00' },
    { icon: 'notifications_active', title: 'Real-time Updates', description: 'Get instant notifications on appointment status and queue progress.', color: '#8e24aa' },
    { icon: 'devices', title: 'Works Everywhere', description: 'Access your health dashboard from any device — phone, tablet, or desktop.', color: '#0097a7' },
  ];

  stats: Stat[] = [
    { value: '12,000+', label: 'Patients Served', icon: 'people' },
    { value: '50+',     label: 'Specialist Doctors', icon: 'medical_services' },
    { value: '98%',     label: 'Satisfaction Rate', icon: 'thumb_up' },
    { value: '10',      label: 'Departments', icon: 'local_hospital' },
  ];

  departments = [
    { name: 'Cardiology',    icon: 'favorite',          color: '#e53935' },
    { name: 'Orthopedics',   icon: 'accessibility_new', color: '#1e88e5' },
    { name: 'Neurology',     icon: 'psychology',        color: '#8e24aa' },
    { name: 'Dermatology',   icon: 'spa',               color: '#43a047' },
    { name: 'Pediatrics',    icon: 'child_care',        color: '#fb8c00' },
    { name: 'General',       icon: 'local_hospital',    color: '#00897b' },
  ];

  ngOnInit() {
    this.timer = setInterval(() => {
      this.currentSlide.update(n => (n + 1) % this.slides.length);
    }, 4500);
  }

  ngOnDestroy() { clearInterval(this.timer); }

  goToSlide(i: number) { this.currentSlide.set(i); }

  getStarted() {
    if (this.auth.isLoggedIn()) {
      this.router.navigate([this.auth.isAdmin() ? '/admin' : '/patient']);
    } else {
      this.router.navigate(['/register']);
    }
  }
}
