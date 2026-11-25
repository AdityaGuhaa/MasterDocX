// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import DocumentViewer from './pages/DocumentViewer';
import DocumentUploader from './pages/DocumentUploader';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DocumentUploader />} />
            <Route path="/viewer/:docId" element={<DocumentViewer />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>MasterDocX runs entirely on your computer with a local language model. Released under the MIT License.</p>
          <p className="footer-credit">Made by Aditya Guha &amp; Claude</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
