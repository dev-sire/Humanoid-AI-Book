/**
 * ChatButton component.
 *
 * Floating button in bottom-right corner that toggles chat window.
 */

import React, { JSX } from 'react';
import styles from './styles.module.css';

interface ChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export default function ChatButton({ onClick, isOpen }: ChatButtonProps): JSX.Element {
  return (
    <button
      className={styles.chatButton}
      onClick={onClick}
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
      title={isOpen ? 'Close chat' : 'Ask a question'}
    >
      {isOpen ? '✕' : '💬'}
    </button>
  );
}
