'use client';
import { useEffect, useRef } from 'react';

const EMOJIS = ['🛒','💰','📦','📊','💳','🏷️','📈','🎯','⚡','✅','💎','🔥','🚀','📱'];

export default function EmojiFloat() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    for (let i = 0; i < 20; i++) {
      const el = document.createElement('div');
      el.textContent = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
      el.style.cssText = `
        position: absolute;
        font-size: ${1.5 + Math.random() * 2}rem;
        left: ${Math.random() * 100}vw;
        opacity: 0.06;
        animation: floatUp ${12 + Math.random() * 20}s linear infinite;
        animation-delay: -${Math.random() * 20}s;
        user-select: none;
        pointer-events: none;
      `;
      container.appendChild(el);
    }
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        position: 'fixed',
        inset: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  );
}