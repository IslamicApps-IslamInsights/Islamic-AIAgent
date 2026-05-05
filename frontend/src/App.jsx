import React from 'react';
import ReactDOM from 'react-dom/client';
import IslamicAIAgent from './components/IslamicAIAgent.tsx';
import { BackendReadinessWrapper } from './utils/backendReadiness.jsx';
import './index.css';
import './App.css';

function App({ isWidget = false, apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5010', themeColor = '#D4AF37' }) {
  return (
    <BackendReadinessWrapper apiUrl={apiUrl}>
      <div className={`App overflow-hidden ${isWidget ? 'widget-mode' : 'full-page-mode'}`}>
        <IslamicAIAgent isWidget={isWidget} apiUrl={apiUrl} themeColor={themeColor} />
      </div>
    </BackendReadinessWrapper>
  );
}


export default App;
