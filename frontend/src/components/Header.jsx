// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import React from 'react';
import { Link } from 'react-router-dom';
import { FaBook, FaUpload } from 'react-icons/fa';

const Header = () => {
  return (
    <header className="App-header">
      <h1><FaBook style={{ marginRight: '10px' }} /> MasterDocX</h1>
      <nav>
        <Link to="/" style={{ color: 'white', textDecoration: 'none', marginRight: '20px' }}>
          <FaUpload /> Upload
        </Link>
      </nav>
    </header>
  );
};

export default Header;