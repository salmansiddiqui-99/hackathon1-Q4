/**
 * Unit Tests: React Components
 * Tests for HeroSection, ModuleCard, ChatbotWidget, ActionButtons
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock @docusaurus/Link
jest.mock('@docusaurus/Link', () => {
  return ({ children, to, href, ...props }) => (
    <a href={to || href} {...props}>{children}</a>
  );
});

// Import components
import HeroSection from '../src/components/HeroSection';
import ModuleCard from '../src/components/ModuleCard';
import ChatbotWidget from '../src/components/ChatbotWidget';
import ActionButtons from '../src/components/ActionButtons';

describe('HeroSection Component', () => {
  test('renders hero title', () => {
    render(<HeroSection />);
    expect(screen.getByText(/Physical AI & Humanoid Robotics Course/i)).toBeInTheDocument();
  });

  test('renders hero subtitle', () => {
    render(<HeroSection />);
    expect(screen.getByText(/Master the intersection of AI and robotics/i)).toBeInTheDocument();
  });

  test('renders CTA buttons', () => {
    render(<HeroSection />);
    expect(screen.getByText(/Start Learning/i)).toBeInTheDocument();
    expect(screen.getByText(/View on GitHub/i)).toBeInTheDocument();
  });

  test('Start Learning button links to docs', () => {
    render(<HeroSection />);
    const button = screen.getByText(/Start Learning/i);
    expect(button.closest('a')).toHaveAttribute('href', '/docs/intro');
  });

  test('GitHub button has external link', () => {
    render(<HeroSection />);
    const button = screen.getByText(/View on GitHub/i);
    expect(button.closest('a')).toHaveAttribute('target', '_blank');
  });
});

describe('ModuleCard Component', () => {
  const mockModule = {
    module_id: 1,
    name: 'Module 1: ROS 2',
    description: 'Learn ROS 2 fundamentals',
    chapters: [
      { number: 'Ch 1', title: 'Chapter 1', link: '/docs/module1/chapter1' },
      { number: 'Ch 2', title: 'Chapter 2', link: '/docs/module1/chapter2' },
    ],
  };

  test('renders module name', () => {
    render(<ModuleCard {...mockModule} />);
    expect(screen.getByText(/Module 1: ROS 2/i)).toBeInTheDocument();
  });

  test('renders module description', () => {
    render(<ModuleCard {...mockModule} />);
    expect(screen.getByText(/Learn ROS 2 fundamentals/i)).toBeInTheDocument();
  });

  test('renders chapter list', () => {
    render(<ModuleCard {...mockModule} />);
    expect(screen.getByText(/Chapter 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Chapter 2/i)).toBeInTheDocument();
  });

  test('chapter links are correct', () => {
    render(<ModuleCard {...mockModule} />);
    const chapter1Link = screen.getByText(/Chapter 1/i).closest('a');
    expect(chapter1Link).toHaveAttribute('href', '/docs/module1/chapter1');
  });
});

describe('ChatbotWidget Component', () => {
  test('renders chat button', () => {
    render(<ChatbotWidget />);
    const button = screen.getByRole('button', { name: /Open AI Assistant/i });
    expect(button).toBeInTheDocument();
  });

  test('chat window is hidden by default', () => {
    render(<ChatbotWidget />);
    expect(screen.queryByText(/AI Assistant/i)).not.toBeInTheDocument();
  });

  test('clicking button opens chat window', () => {
    render(<ChatbotWidget />);
    const button = screen.getByRole('button', { name: /Open AI Assistant/i });
    fireEvent.click(button);
    expect(screen.getByText(/AI Assistant/i)).toBeInTheDocument();
  });

  test('displays coming soon message', () => {
    render(<ChatbotWidget />);
    const button = screen.getByRole('button', { name: /Open AI Assistant/i });
    fireEvent.click(button);
    expect(screen.getByText(/Coming soon in Phase 5/i)).toBeInTheDocument();
  });

  test('close button closes chat window', () => {
    render(<ChatbotWidget />);
    const openButton = screen.getByRole('button', { name: /Open AI Assistant/i });
    fireEvent.click(openButton);

    const closeButton = screen.getByRole('button', { name: /Close chat/i });
    fireEvent.click(closeButton);

    expect(screen.queryByText(/AI Assistant/i)).not.toBeInTheDocument();
  });
});

describe('ActionButtons Component', () => {
  test('renders personalize button', () => {
    render(<ActionButtons />);
    expect(screen.getByText(/Personalize/i)).toBeInTheDocument();
  });

  test('renders translate button', () => {
    render(<ActionButtons />);
    expect(screen.getByText(/Translate to Urdu/i)).toBeInTheDocument();
  });

  test('displays coming soon note', () => {
    render(<ActionButtons />);
    expect(screen.getByText(/coming in future updates/i)).toBeInTheDocument();
  });

  test('personalize button shows alert', () => {
    global.alert = jest.fn();
    render(<ActionButtons />);

    const button = screen.getByText(/Personalize/i);
    fireEvent.click(button);

    expect(global.alert).toHaveBeenCalledWith(
      expect.stringContaining('Personalization feature coming soon')
    );
  });

  test('translate button shows alert', () => {
    global.alert = jest.fn();
    render(<ActionButtons />);

    const button = screen.getByText(/Translate to Urdu/i);
    fireEvent.click(button);

    expect(global.alert).toHaveBeenCalledWith(
      expect.stringContaining('Translation to Urdu coming soon')
    );
  });
});
