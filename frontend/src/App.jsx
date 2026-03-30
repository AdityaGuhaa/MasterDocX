import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import DocumentViewer from './pages/DocumentViewer';
import DocumentUploader from './pages/DocumentUploader';
import './App.css';

function App() {
  const [documents, setDocuments] = useState([]);

  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DocumentUploader />} />
            <Route path="/viewer/:docId" element={<DocumentViewer />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;