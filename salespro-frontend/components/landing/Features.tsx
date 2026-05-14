'use client';
import { motion } from 'framer-motion';

const features = [
  { emoji: '📦', title: 'Ombor boshqaruvi', desc: "Tovarlar qoldig'ini real-time kuzating. Avtomatik ogohlantirishlar va ko'p omborxona qo'llab-quvvatlash.", tag: 'Real-time' },
  { emoji: '🛒', title: 'Kassa va POS', desc: 'Tez va qulay savdo interfeysi. Barcode skaneri, qaytarish, to\'lov turlari bir tugmada.', tag: 'Offline ham ishlaydi' },
  { emoji: '👥', title: 'CRM — Mijozlar', desc: "Har bir mijozning xarid tarixi, cashback ballari va shaxsiy takliflarni avtomatik boshqaring.", tag: 'Sodiqlik dasturi' },
  { emoji: '📊', title: 'Analytics', desc: "Sotuvchilar, do'konlar, tovarlar bo'yicha chuqur tahlil. Telegram bot orqali kunlik hisobotlar.", tag: 'Telegram bot' },
  { emoji: '💰', title: 'Moliya', desc: 'Kassa harakati, foyda-zarar, xarajatlar — barchasi aniq va tushunarli grafiklar bilan.', tag: 'P&L hisobi' },
  { emoji: '📣', title: 'Marketing', desc: 'SMS kampaniyalar, sovg\'a sertifikatlar, mijozlarni segmentlash. Shaxsiylashtirilgan takliflar.', tag: 'SMS marketing' },
];

export default function Features() {
  return (
    <section id="features" style={{ padding: '6rem 4rem', position: 'relative', zIndex: 2 }}>
      <div className="section-tag">⚡ Imkoniyatlar</div>
      <h2 style={{ fontSize: 'clamp(1.8rem, 4vw, 3rem)', fontWeight: 800, letterSpacing: '-1px', marginBottom: '1rem' }}>
        Barcha vazifalar uchun<br />bitta yechim
      </h2>
      <p style={{ color: '#9898b8', fontSize: '1.1rem', maxWidth: '560px', lineHeight: 1.6, marginBottom: '3rem' }}>
        Tovardan tortib moliyagacha — hamma narsani bitta oynadan boshqaring.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{f.emoji}</div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.7rem' }}>{f.title}</h3>
            <p style={{ color: '#9898b8', fontSize: '0.9rem', lineHeight: 1.6 }}>{f.desc}</p>
            <span style={{
              display: 'inline-block', marginTop: '1rem',
              background: 'rgba(67,233,123,0.1)', color: '#43e97b',
              borderRadius: '100px', padding: '0.2rem 0.7rem',
              fontSize: '0.75rem', fontWeight: 600,
            }}>{f.tag}</span>
          </motion.div>
        ))}
      </div>
    </section>
  );
}