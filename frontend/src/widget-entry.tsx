import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// This is the entry point for the widget
const initWidget = () => {
  // 1. Find the script tag that loaded us (to get data attributes)
  const scriptTag = document.currentScript || document.querySelector('script[data-api-url]');
  const apiUrl = scriptTag?.getAttribute('data-api-url') || 'http://localhost:5010';
  const themeColor = scriptTag?.getAttribute('data-theme-color') || '#D4AF37';

  // 2. Create the container element for our widget
  const container = document.createElement('div');
  container.id = 'islamic-ai-widget-root';
  document.body.appendChild(container);

  // 3. Create Shadow DOM for style isolation
  // We use shadow DOM to prevent host site styles from leaking in
  const shadowRoot = container.attachShadow({ mode: 'open' });

  // 4. Create a style target within the shadow DOM
  const mountPoint = document.createElement('div');
  mountPoint.className = 'islamic-widget-mount';
  mountPoint.style.width = '100%';
  mountPoint.style.height = '100%';
  shadowRoot.appendChild(mountPoint);

  // Sync styles into Shadow DOM
  const syncStyles = () => {
    // 1. Clone all style and link tags from head
    const styleElements = document.querySelectorAll('style, link[rel="stylesheet"]');
    
    styleElements.forEach(original => {
      // Create a unique key for tracking
      const key = original.tagName === 'STYLE' 
        ? original.textContent?.substring(0, 100) 
        : (original as HTMLLinkElement).href;
      
      if (!key) return;

      // Check if already synced in this shadow root
      const existing = Array.from(shadowRoot.querySelectorAll('style, link[rel="stylesheet"]'))
        .find(s => (s.tagName === 'STYLE' ? s.textContent?.substring(0, 100) : (s as HTMLLinkElement).href) === key);

      if (!existing) {
        const clone = original.cloneNode(true);
        shadowRoot.appendChild(clone);
      }
    });

    // 2. Ensure Google Fonts are present (Insurance)
    if (!shadowRoot.getElementById('widget-fonts-sync')) {
      const fontStyle = document.createElement('style');
      fontStyle.id = 'widget-fonts-sync';
      fontStyle.textContent = `@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');`;
      shadowRoot.appendChild(fontStyle);
    }
  };

  // Immediate sync
  syncStyles();

  // Watch for dynamic style updates (Vite HMR and runtime styled-components)
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === 'childList') {
        syncStyles();
      }
    }
  });
  observer.observe(document.head, { childList: true, subtree: true });

  // 5. Render the React App
  const root = ReactDOM.createRoot(mountPoint);
  root.render(
    <React.StrictMode>
      <App isWidget={true} apiUrl={apiUrl} themeColor={themeColor} />
    </React.StrictMode>
  );
};

// Check if we should auto-initialize
if (document.readyState === 'complete') {
  initWidget();
} else {
  window.addEventListener('load', initWidget);
}

// Export for manual initialization if needed
export { initWidget };
