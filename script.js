// ============================================================
//  ALTER SPERO — script.js
// ============================================================

// ── Navbar: scroll effect ──────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

// ── Navbar: active section highlight ──────────────────────
const sections  = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-links a');

const sectionWatcher = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    navAnchors.forEach(a => a.classList.remove('active'));
    const match = document.querySelector(`.nav-links a[href="#${entry.target.id}"]`);
    if (match) match.classList.add('active');
  });
}, { threshold: 0.35 });

sections.forEach(s => sectionWatcher.observe(s));

// ── Hamburger menu ─────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');

hamburger.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  hamburger.classList.toggle('open', isOpen);
  hamburger.setAttribute('aria-expanded', isOpen);
});

// Close menu when a link is clicked
navLinks.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
  });
});

// Close menu when clicking outside
document.addEventListener('click', e => {
  if (!navbar.contains(e.target) && navLinks.classList.contains('open')) {
    navLinks.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
  }
});

// ── Hero parallax ─────────────────────────────────────────
const heroBg = document.querySelector('.hero-bg');
if (heroBg) {
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight) {
      heroBg.style.transform = `translateY(${y * 0.28}px)`;
    }
  }, { passive: true });
}

// ── Scroll reveal ─────────────────────────────────────────
const revealEls = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

revealEls.forEach(el => revealObserver.observe(el));

// ── Journal tabs ──────────────────────────────────────────
const tabs = document.querySelectorAll('.j-tab');
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => {
      t.classList.remove('active');
      t.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    // Filter articles by category (extend when CMS is connected)
  });
});

// ── Contact form ──────────────────────────────────────────
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', e => {
    e.preventDefault();

    const btn = contactForm.querySelector('button[type="submit"]');
    const origContent = btn.innerHTML;

    // Validate
    const email = contactForm.querySelector('#f-email').value;
    if (!email.includes('@')) {
      showFormMessage('Adresa de email nu este validă.', 'error');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Se trimite...';

    // Simulate send (replace with Formspree / backend call)
    setTimeout(() => {
      btn.innerHTML = '<i class="fas fa-check"></i> Mesaj trimis cu succes!';
      btn.style.background = '#2a6e4a';
      showFormMessage('Mulțumim! Te vom contacta în curând.', 'success');

      setTimeout(() => {
        btn.innerHTML = origContent;
        btn.style.background = '';
        btn.disabled = false;
        contactForm.reset();
        removeFormMessage();
      }, 4000);
    }, 1200);
  });
}

function showFormMessage(text, type) {
  removeFormMessage();
  const msg = document.createElement('p');
  msg.id = 'form-msg';
  msg.textContent = text;
  msg.style.cssText = `
    padding: .65rem 1rem;
    border-radius: 4px;
    font-size: .85rem;
    background: ${type === 'success' ? 'rgba(42,110,74,.25)' : 'rgba(160,40,40,.25)'};
    border: 1px solid ${type === 'success' ? '#2a6e4a' : '#8b2020'};
    color: ${type === 'success' ? '#7ecba4' : '#e07070'};
    margin-top: -.25rem;
  `;
  contactForm.appendChild(msg);
}

function removeFormMessage() {
  const old = document.getElementById('form-msg');
  if (old) old.remove();
}

// ── Smooth scroll offset (fixed navbar) ───────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const id = anchor.getAttribute('href').slice(1);
    const target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    const offset = navbar.offsetHeight + 16;
    const top = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});
