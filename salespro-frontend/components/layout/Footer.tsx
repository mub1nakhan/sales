export default function Footer() {
  return (
    <footer style={{
      background: '#1a1a26',
      borderTop: '1px solid rgba(255,255,255,0.08)',
      padding: '4rem',
      position: 'relative', zIndex: 2,
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '3rem', marginBottom: '3rem' }}>
        <div>
          <div style={{
            fontFamily: 'monospace', fontSize: '1.5rem', fontWeight: 700,
            background: 'linear-gradient(135deg, #6c63ff, #43e97b)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            marginBottom: '1rem', display: 'block',
          }}>SalesPro</div>
          <p style={{ color: '#9898b8', fontSize: '0.875rem', lineHeight: 1.7, maxWidth: '280px' }}>
            Do'konlar uchun zamonaviy savdo boshqaruv tizimi. 1500+ do'kon allaqachon ishlatmoqda.
          </p>
        </div>

        {[
          { title: 'Yechimlar', links: ["Kiyim do'koni", 'Oziq-ovqat', 'Elektronika', 'Kosmetika'] },
          { title: 'Kompaniya', links: ['Biz haqimizda', 'Blog', 'Akademiya', 'Vakansiyalar'] },
          { title: 'Aloqa', links: ['+998 71 123 45 67', 'info@salespro.uz', "Toshkent, O'zbekiston"] },
        ].map(col => (
          <div key={col.title}>
            <h4 style={{ fontWeight: 700, fontSize: '0.875rem', marginBottom: '1.2rem', textTransform: 'uppercase', letterSpacing: '1px', color: '#9898b8' }}>
              {col.title}
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
              {col.links.map(link => (
                <li key={link}>
                  <a href="#" style={{ textDecoration: 'none', color: '#9898b8', fontSize: '0.875rem', transition: 'color 0.2s' }}
                    onMouseEnter={e => (e.currentTarget.style.color = '#f0f0ff')}
                    onMouseLeave={e => (e.currentTarget.style.color = '#9898b8')}
                  >{link}</a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <p style={{ color: '#9898b8', fontSize: '0.8rem' }}>© 2025 SalesPro. Barcha huquqlar himoyalangan.</p>
        <div style={{ display: 'flex', gap: '1rem' }}>
          {['📘', '📸', '✈️', '▶️'].map(icon => (
            <a key={icon} href="#" style={{
              width: '36px', height: '36px', borderRadius: '8px',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1rem', textDecoration: 'none', transition: 'background 0.2s',
            }}>{icon}</a>
          ))}
        </div>
      </div>
    </footer>
  );
}