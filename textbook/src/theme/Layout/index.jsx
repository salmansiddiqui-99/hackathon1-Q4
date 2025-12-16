/**
 * Swizzled Layout Component for Docusaurus
 * Wraps the default Docusaurus Layout with ChatbotWidget on all pages
 */

import React from 'react';
import LayoutOrig from '@theme-original/Layout';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

export default function LayoutWrapper(props) {
  return (
    <>
      <LayoutOrig {...props} />
      <ChatbotWidget />
    </>
  );
}
