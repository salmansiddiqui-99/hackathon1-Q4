/**
 * Custom Layout Wrapper for Physical AI Textbook
 * Forces dark mode and applies futuristic theme colors
 */

import React, { useEffect } from 'react';
import Layout from '@theme-original/Layout';

export default function CustomLayout(props) {
  useEffect(() => {
    // Force dark mode on mount
    const htmlElement = document.documentElement;
    htmlElement.setAttribute('data-theme', 'dark');

    // Apply primary/secondary colors to navbar and sidebar
    const applyThemeColors = () => {
      // Navbar styling
      const navbar = document.querySelector('.navbar');
      if (navbar) {
        navbar.style.backgroundColor = 'var(--color-bg-darker)';
        navbar.style.borderBottom = '1px solid var(--color-border)';
      }

      // Navbar links
      const navbarItems = document.querySelectorAll('.navbar__item, .navbar__link');
      navbarItems.forEach((item) => {
        item.style.color = 'var(--color-text)';
        item.addEventListener('mouseenter', () => {
          item.style.color = 'var(--color-primary)';
        });
        item.addEventListener('mouseleave', () => {
          item.style.color = 'var(--color-text)';
        });
      });

      // Sidebar styling
      const sidebar = document.querySelector('.sidebar');
      if (sidebar) {
        sidebar.style.backgroundColor = 'var(--color-bg-light)';
      }

      // Sidebar menu items
      const menuItems = document.querySelectorAll('.menu__item, .menu__link');
      menuItems.forEach((item) => {
        item.style.color = 'var(--color-text)';
        item.addEventListener('mouseenter', () => {
          item.style.backgroundColor = 'rgba(0, 217, 255, 0.1)';
          item.style.color = 'var(--color-primary)';
        });
        item.addEventListener('mouseleave', () => {
          if (!item.classList.contains('menu__item--active')) {
            item.style.backgroundColor = 'transparent';
            item.style.color = 'var(--color-text)';
          }
        });
      });

      // Active sidebar items
      const activeItems = document.querySelectorAll('.menu__item--active');
      activeItems.forEach((item) => {
        item.style.backgroundColor = 'rgba(0, 217, 255, 0.15)';
        item.style.color = 'var(--color-primary)';
        item.style.borderLeft = '3px solid var(--color-primary)';
      });

      // Links styling
      const links = document.querySelectorAll('a:not(.navbar__item):not(.menu__link)');
      links.forEach((link) => {
        link.style.color = 'var(--color-primary)';
        link.addEventListener('mouseenter', () => {
          link.style.color = 'var(--color-secondary)';
        });
        link.addEventListener('mouseleave', () => {
          link.style.color = 'var(--color-primary)';
        });
      });
    };

    // Apply theme colors on mount
    applyThemeColors();

    // Re-apply on navigation (Docusaurus SPA navigation)
    const observer = new MutationObserver(() => {
      applyThemeColors();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    // Cleanup
    return () => {
      observer.disconnect();
    };
  }, []);

  return <Layout {...props} />;
}
