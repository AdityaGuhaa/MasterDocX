// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiPlus, FiSun, FiMoon } from 'react-icons/fi';
import Logo from './Logo';
import { useTheme } from '../theme';

const Header = () => {
  const { pathname } = useLocation();
  const onViewer = pathname.startsWith('/viewer');
  const [theme, toggleTheme] = useTheme();
  const nextTheme = theme === 'dark' ? 'light' : 'dark';

  return (
    <header className="nav">
      <div className="nav-inner">
        <Link to="/" className="brand" aria-label="MasterDocX home">
          <Logo className="brand-logo" />
          <span className="brand-divider" aria-hidden="true" />
          <span className="brand-name">MasterDocX</span>
        </Link>
        <div className="nav-actions">
          {onViewer && (
            <Link to="/" className="nav-link">
              <FiPlus size={15} /> New document
            </Link>
          )}
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${nextTheme} mode`}
            title={`Switch to ${nextTheme} mode`}
          >
            <span className={`theme-icon ${theme === 'dark' ? 'is-hidden' : ''}`}>
              <FiMoon size={17} />
            </span>
            <span className={`theme-icon ${theme === 'dark' ? '' : 'is-hidden'}`}>
              <FiSun size={17} />
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
