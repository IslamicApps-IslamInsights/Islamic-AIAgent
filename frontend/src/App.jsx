import React from 'react';
import ReactDOM from 'react-dom/client';
import IslamicAIAgent from './components/IslamicAIAgent.tsx';
import './index.css';
import './App.css';

function App({ isWidget = false, apiUrl = 'http://localhost:5010', themeColor = '#D4AF37' }) {
  return (
    <div className={`App overflow-hidden ${isWidget ? 'widget-mode' : 'full-page-mode'}`}>
      <IslamicAIAgent isWidget={isWidget} apiUrl={apiUrl} themeColor={themeColor} />
    </div>
  );
}


export default App;