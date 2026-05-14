'use client';
import { motion } from 'framer-motion';

const steps = [
  { num: '01', emoji: '📝', title: "Ro'yxatdan o'ting", desc: "Email va telefon orqali 2 daqiqada ro'yxatdan o'ting. Karta kerak emas." },
  { num: '02', emoji: '⚙️', title: 'Sozlang', desc: "Tovarlaringizni, xodimlaringizni va do'kon ma'lumotlarini kiriting." },
  { num: '03', emoji: '🚀', title: 'Savdo boshlang', desc: "POS orqali savdo qiling, real-time hisobotlarni kuzating." },
  { num: '04', emoji: '📈', title: "O'sib boring", desc: "Tahlillar asosida to'g'ri qarorlar qabul qiling." },
];

export default function HowItWorks() {
  return (
    <section id="how" style={{
      padding: '6rem 4rem',
      background: '#12121a',
      borderTop: '1px solid rgba(255,255,255,0.08)',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      position: 'relative', zIndex: 2,
    }}>
      <div className="section-tag">🔧 Jarayon</div>
      <h2 style={{ fontSize: 'clamp(1.8rem, 4vw, 3rem)', fontWeight: 800, letterSpacing: '-1px', marginBottom: '1rem' }}>
        Qanday ishlaydi?
      </h2>
      <p style={{ color: '#9898b8', fontSize: '1.1rem', marginBottom: '3rem' }}>
        3 oddiy qadamda do'koningizni raqamlashtiring.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '2rem' }}>
        {steps.map((s, i) => (
          <motion.div
            key={s.num}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            style={{ textAlign: 'center', padding: '2rem 1.5rem' }}
          >
            <div style={{
              width: '56px', height: '56px', borderRadius: '16px',
              background: 'rgba(108,99,255,0.15)',
              border: '1px solid rgba(108,99,255,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'monospace', fontSize: '1.2rem', fontWeight: 700,
              color: '#6c63ff', margin: '0 auto 1.2rem',
            }}>{s.num}</div>
            <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>{s.emoji}</div>
            <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>{s.title}</h3>
            <p style={{ color: '#9898b8', fontSize: '0.875rem', lineHeight: 1.6 }}>{s.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}