'use client';
import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0,
      zIndex: 100,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '1.2rem 4rem',
      background: scrolled ? 'rgba(10,10,15,0.9)' : 'rgba(10,10,15,0.5)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      transition: 'background 0.3s',
    }}>
      <div style={{
        fontFamily: 'monospace',
        fontSize: '1.4rem',
        fontWeight: 700,
        background: 'linear-gradient(135deg, #6c63ff, #43e97b)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}>
        Sales<span style={{ WebkitTextFillColor: '#ff6584' }}>Pro</span>
      </div>

      <ul style={{ display: 'flex', gap: '2.5rem', listStyle: 'none' }}>
        {[
          { label: 'Imkoniyatlar', href: '#features' },
          { label: 'Qanday ishlaydi', href: '#how' },
          { label: 'Narxlar', href: '#pricing' },
          { label: 'Mijozlar', href: '#testimonials' },
        ].map(item => (
          <li key={item.href}>
            <a href={item.href} style={{
              textDecoration: 'none',
              color: '#9898b8',
              fontSize: '0.9rem',
              fontWeight: 500,
              transition: 'color 0.2s',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = '#f0f0ff')}
            onMouseLeave={e => (e.currentTarget.style.color = '#9898b8')}
            >
              {item.label}
            </a>
          </li>
        ))}
      </ul>

      <Link href="#pricing" style={{
        background: '#6c63ff',
        color: 'white',
        padding: '0.6rem 1.4rem',
        borderRadius: '8px',
        fontSize: '0.85rem',
        fontWeight: 600,
        textDecoration: 'none',
        transition: 'transform 0.2s, box-shadow 0.2s',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(108,99,255,0.4)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
      >
        Bepul boshlash →
      </Link>
    </nav>
  );
}