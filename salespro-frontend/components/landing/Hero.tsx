'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';

const stats = [
  { num: '1500+', label: "Faol do'konlar" },
  { num: '40%', label: 'Vaqt tejash' },
  { num: '30%', label: "Savdo o'sishi" },
  { num: '99.9%', label: 'Uptime' },
];

export default function Hero() {
  return (
    <section style={{
      minHeight: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      textAlign: 'center',
      padding: '8rem 2rem 4rem',
      position: 'relative', zIndex: 2,
    }}>
      <div>
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="badge"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem' }}
        >
          🚀 1500+ do'kon allaqachon ishlatmoqda
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{ fontSize: 'clamp(2.8rem, 7vw, 5.5rem)', fontWeight: 800, lineHeight: 1.05, letterSpacing: '-2px', marginBottom: '1.5rem' }}
        >
          Do'koningizni<br />
          <span className="gradient-text">superkuchga</span><br />
          aylantiring
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ fontSize: '1.2rem', color: '#9898b8', maxWidth: '600px', margin: '0 auto 2.5rem', lineHeight: 1.7 }}
        >
          Savdo, ombor, kassa, mijozlar va moliyani — barchasi bitta aqlli tizimda. Django-powered, real-time analytics.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}
        >
          <a href="#pricing" className="btn-primary">🎯 Bepul sinab ko'rish</a>
          <a href="#how" className="btn-secondary">▶ Demo ko'rish</a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          style={{ display: 'flex', gap: '3rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '4rem' }}
        >
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
              style={{ textAlign: 'center' }}
            >
              <div className="gradient-text" style={{ fontSize: '2.2rem', fontWeight: 800, fontFamily: 'monospace' }}>{s.num}</div>
              <div style={{ fontSize: '0.85rem', color: '#9898b8', marginTop: '0.2rem' }}>{s.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}