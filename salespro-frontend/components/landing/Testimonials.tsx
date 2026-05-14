'use client';
import { motion } from 'framer-motion';

const testimonials = [
  { initials: 'AK', name: 'Alisher Karimov', role: "Kiyim do'koni egasi", text: "SalesPro bilan do'konimiz aylanmasi 30% ga oshdi. Tovar hisobi va hisobotlar endi bir necha soniyada tayyor." },
  { initials: 'MU', name: 'Malika Umarova', role: "Oziq-ovqat do'koni", text: "Telegram bot orqali har kuni ertalab savdo hisobotini olib turaman. Boshqa dasturga qaytish haqida o'ylamadim ham." },
  { initials: 'JN', name: 'Javlon Nazarov', role: 'Kosmetika tarmog\'i', text: "5 ta do'konni bitta tizimdan boshqarish — bu orzu edi. SalesPro buni haqiqatga aylantirdi!" },
];

export default function Testimonials() {
  return (
    <section id="testimonials" style={{
      padding: '6rem 4rem',
      background: '#12121a',
      borderTop: '1px solid rgba(255,255,255,0.08)',
      position: 'relative', zIndex: 2,
    }}>
      <div className="section-tag">💬 Fikrlar</div>
      <h2 style={{ fontSize: 'clamp(1.8rem, 4vw, 3rem)', fontWeight: 800, letterSpacing: '-1px', marginBottom: '3rem' }}>
        Mijozlarimiz nima deydi
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {testimonials.map((t, i) => (
          <motion.div
            key={t.name}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div style={{ fontSize: '1rem', marginBottom: '1rem', letterSpacing: '2px' }}>⭐⭐⭐⭐⭐</div>
            <p style={{ fontSize: '0.9rem', color: '#9898b8', lineHeight: 1.7, marginBottom: '1.5rem', fontStyle: 'italic' }}>
              "{t.text}"
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '50%',
                background: 'linear-gradient(135deg, #6c63ff, #43e97b)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: '0.875rem',
              }}>{t.initials}</div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{t.name}</div>
                <div style={{ fontSize: '0.75rem', color: '#9898b8' }}>{t.role}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}