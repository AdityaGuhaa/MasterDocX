// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import { useEffect, useState } from 'react';

// Light/dark mode. Until the user picks one, the app follows the system setting.
// The choice is saved in localStorage and applied as <html data-theme="light|dark">
// (index.html applies it before the first paint so there's no flash).

const STORAGE_KEY = 'masterdocx-theme';
const EVENT = 'masterdocx-themechange';
const systemDark = () => window.matchMedia('(prefers-color-scheme: dark)');

export const getEffectiveTheme = () => {
  const explicit = document.documentElement.dataset.theme;
  if (explicit === 'light' || explicit === 'dark') return explicit;
  return systemDark().matches ? 'dark' : 'light';
};

export const setTheme = (theme) => {
  document.documentElement.dataset.theme = theme;
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Storage can be unavailable (private mode); the choice still applies for this page.
  }
  window.dispatchEvent(new Event(EVENT));
};

// Re-render whenever the effective theme changes (toggle, or system change when not overridden)
export const useTheme = () => {
  const [theme, setThemeState] = useState(getEffectiveTheme);

  useEffect(() => {
    const update = () => setThemeState(getEffectiveTheme());
    const media = systemDark();
    window.addEventListener(EVENT, update);
    media.addEventListener('change', update);
    return () => {
      window.removeEventListener(EVENT, update);
      media.removeEventListener('change', update);
    };
  }, []);

  const toggle = () => setTheme(getEffectiveTheme() === 'dark' ? 'light' : 'dark');
  return [theme, toggle];
};
