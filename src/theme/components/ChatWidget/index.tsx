/**
 * ChatWidget component.
 *
 * Main chat widget that orchestrates all child components and manages state.
 */

import React, { useState, useEffect, JSX } from 'react';
import ChatButton from './ChatButton';
import ChatWindow from './ChatWindow';
import { sendMessage, ChatRequest, ChatResponse } from './api/chatApi';
import { Message } from './MessageList';

const STORAGE_KEY = 'rag_chatbot_session';

export default function ChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedText, setSelectedText] = useState('');
  const [lastMessage, setLastMessage] = useState('');

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSession = localStorage.getItem(STORAGE_KEY);
    if (savedSession) {
      try {
        const { sessionId: savedSessionId, messages: savedMessages } = JSON.parse(savedSession);
        setSessionId(savedSessionId);
        setMessages(savedMessages);
      } catch (e) {
        console.error('Failed to load session:', e);
      }
    }
  }, []);

  // Save session to localStorage when it changes
  useEffect(() => {
    if (sessionId && messages.length > 0) {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ sessionId, messages })
      );
    }
  }, [sessionId, messages]);

  // Listen for text selection on the page
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim() || '';

      if (text.length >= 1 && text.length <= 1000) {
        setSelectedText(text);
      } else if (text.length > 1000) {
        setSelectedText(''); // Ignore if too long
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, []);

  const handleSend = async (message: string) => {
    setLastMessage(message);
    setError(null);
    setIsLoading(true);

    // Add user message immediately
    const userMessage: Message = {
      role: 'user',
      content: message,
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const request: ChatRequest = {
        message,
        session_id: sessionId || undefined,
        selected_text: selectedText || undefined,
      };

      const response: ChatResponse = await sendMessage(request);

      // Update session ID if it's a new session
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Clear selected text after successful send
      setSelectedText('');
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(
        'Failed to get response. Please check your connection and try again.'
      );

      // Remove the user message that failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastMessage) {
      handleSend(lastMessage);
    }
  };

  const handleClearSelection = () => {
    setSelectedText('');
  };

  const handleClearChat = () => {
    // Clear all state
    setMessages([]);
    setSessionId(null);
    setError(null);
    setSelectedText('');
    setLastMessage('');

    // Clear localStorage
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <>
      <ChatButton onClick={() => setIsOpen(!isOpen)} isOpen={isOpen} />
      {isOpen && (
        <ChatWindow
          messages={messages}
          onClose={() => setIsOpen(false)}
          onSend={handleSend}
          isLoading={isLoading}
          error={error}
          onRetry={handleRetry}
          selectedText={selectedText}
          onClearSelection={handleClearSelection}
          onClearChat={handleClearChat}
        />
      )}
    </>
  );
}
