import React from 'react';
import { Link } from 'react-router-dom';
import { FaBook, FaUpload, FaRobot } from 'react-icons/fa';

const Header = () => {
  return (
    <header className="App-header">
      <h1>AI Document Reader</h1>
      <nav>
        <Link to="/" style={{ color: 'white', textDecoration: 'none', marginRight: '20px' }}>
          <FaUpload /> Upload
        </Link>
        <Link to="/viewer" style={{ color: 'white', textDecoration: 'none' }}>
          <FaBook /> Viewer
        </Link>
      </nav>
    </header>
  );
};

export default Header;