import React from 'react';
import IslamicAIAgent from './components/IslamicAIAgent.tsx';
import './App.css';

function App() {
  return (
    <div className="App">
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 py-8 px-4">
        <IslamicAIAgent />
      </div>
    </div>
  );
}

export default App;