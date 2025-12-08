/**
 * InputArea component.
 *
 * Text input field and send button with Enter key handler.
 */

import React, { useState, KeyboardEvent, JSX } from 'react';
import styles from './styles.module.css';

interface InputAreaProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export default function InputArea({ onSend, disabled }: InputAreaProps): JSX.Element {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.inputArea}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask a question..."
        disabled={disabled}
        maxLength={1000}
        aria-label="Chat message input"
      />
      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        aria-label="Send message"
      >
        Send
      </button>
    </div>
  );
}
