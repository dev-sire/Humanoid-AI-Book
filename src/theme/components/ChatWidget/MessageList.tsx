/**
 * MessageList component.
 *
 * Renders user and assistant messages with auto-scroll.
 */

import React, { JSX, useEffect, useRef } from 'react';
import styles from './styles.module.css';
import SourceCitation from './SourceCitation';
import { Source } from './api/chatApi';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps): JSX.Element {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.messageList} role="log" aria-live="polite">
      {messages.length === 0 && (
        <div style={{ textAlign: 'center', color: 'var(--ifm-color-emphasis-600)', padding: '20px' }}>
          <p>👋 Welcome to the Physical AI & Humanoid Robotics chatbot!</p>
          <p style={{ fontSize: '14px' }}>Ask me anything about the book content.</p>
        </div>
      )}

      {messages.map((message, index) => (
        <div key={index}>
          <div
            className={`${styles.message} ${
              message.role === 'user' ? styles.userMessage : styles.assistantMessage
            }`}
          >
            {message.content}
          </div>
          {message.role === 'assistant' && message.sources && (
            <SourceCitation sources={message.sources} />
          )}
        </div>
      ))}

      <div ref={messagesEndRef} />
    </div>
  );
}
