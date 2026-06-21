// App Core Routing and State Provider Mount

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AnalysisProvider } from './context/AnalysisContext';
import { BackendStatus } from './components/BackendStatus';
import { HomePage } from './pages/HomePage';
import { GeminiStatusBadge } from './components/GeminiStatusBadge';
import { AnalysisPage } from './pages/AnalysisPage';
import { ResultsPage } from './pages/ResultsPage';
import './App.css';

const App: React.FC = () => {
  return (
    <AnalysisProvider>
      <BackendStatus>
        <Router>
          <div className="app-container">
            {/* Header branding */}
            <header className="no-print">
              <div className="logo">
                <h1 className="glow-text-indigo">
                  ⚡ Placement Intelligence Platform
                </h1>
              </div>
              <GeminiStatusBadge />
            </header>

            {/* Router Routes */}
            <main>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/analysis" element={<AnalysisPage />} />
                <Route path="/results" element={<ResultsPage />} />
              </Routes>
            </main>
          </div>
        </Router>
      </BackendStatus>
    </AnalysisProvider>
  );
};

export default App;
