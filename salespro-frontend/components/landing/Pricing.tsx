'use client';
import { motion } from 'framer-motion';

const plans = [
  {
    emoji: '🌱', name: 'Starter', price: '29', period: "oyiga / 1 do'kon",
    features: ["1 ta do'kon", '2 ta kassa joyi', 'Asosiy hisobotlar', '5,000 ta tovar', 'Email qo\'llab-quvvatlash'],
    popular: false,
  },
  {
    emoji: '⚡', name: 'Business', price: '79', period: "oyiga / 3 ta do'kon",
    features: ["3 ta do'kon", 'Cheksiz kassa joyi', 'Chuqur analytics', 'Telegram bot', 'CRM + Marketing', 'Ustuvor support'],
    popular: true,
  },
  {
    emoji: '🏢', name: 'Enterprise', price: 'Kelishuv', period: 'oyiga / cheksiz',
    features: ["Cheksiz do'konlar", 'API integratsiya', 'Shaxsiy manager', 'White-label', '24/7 support'],
    popular: false,
  },
];

export default function Pricing() {
  return (
    <section id="pricing" style={{ padding: '6rem 4rem', textAlign: 'center', position: 'relative', zIndex: 2 }}>
      <div className="section-tag">💎 Tariflar</div>
      <h2 style={{ fontSize: 'clamp(1.8rem, 4vw, 3rem)', fontWeight: 800, letterSpacing: '-1px', marginBottom: '1rem' }}>
        Qulay narxlar
      </h2>
      <p style={{ color: '#9898b8', fontSize: '1.1rem', marginBottom: '3rem' }}>
        7 kunlik bepul sinov davri. Karta kerak emas.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', maxWidth: '900px', margin: '0 auto' }}>
        {plans.map((plan, i) => (
          <motion.div
            key={plan.name}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            style={{
              background: plan.popular ? 'rgba(108,99,255,0.08)' : 'rgba(255,255,255,0.04)',
              border: plan.popular ? '1px solid #6c63ff' : '1px solid rgba(255,255,255,0.08)',
              borderRadius: '20px',
              padding: '2.5rem 2rem',
              position: 'relative',
              transition: 'transform 0.3s',
            }}
          >
            {plan.popular && (
              <div style={{
                position: 'absolute', top: '-1px', left: '50%', transform: 'translateX(-50%)',
                background: '#6c63ff', color: 'white',
                fontSize: '0.75rem', fontWeight: 600,
                padding: '0.3rem 1rem', borderRadius: '0 0 8px 8px',
              }}>🔥 Eng mashhur</div>
            )}
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{plan.emoji}</div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: '#9898b8', marginBottom: '0.5rem' }}>{plan.name}</div>
            <div style={{ fontSize: plan.price === 'Kelishuv' ? '1.8rem' : '2.5rem', fontWeight: 800, fontFamily: 'monospace', marginBottom: '0.3rem' }}>
              {plan.price !== 'Kelishuv' && <sup style={{ fontSize: '1rem' }}>$</sup>}
              {plan.price}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#9898b8', marginBottom: '1.5rem' }}>{plan.period}</div>

            <ul style={{ listStyle: 'none', textAlign: 'left', marginBottom: '2rem' }}>
              {plan.features.map(f => (
                <li key={f} style={{
                  padding: '0.5rem 0', fontSize: '0.875rem', color: '#9898b8',
                  display: 'flex', alignItems: 'center', gap: '0.6rem',
                  borderBottom: '1px solid rgba(255,255,255,0.08)',
                }}>
                  <span style={{ color: '#43e97b' }}>✓</span> {f}
                </li>
              ))}
            </ul>

            <a href="#" className={plan.popular ? 'btn-primary' : 'btn-secondary'}
              style={{ width: '100%', justifyContent: 'center' }}>
              {plan.popular ? 'Boshlash 🚀' : 'Boshlash'}
            </a>
          </motion.div>
        ))}
      </div>
    </section>
  );
}