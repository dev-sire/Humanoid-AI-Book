/**
 * ErrorMessage component.
 *
 * Displays error messages with retry option.
 */

import React, { JSX } from 'react';
import styles from './styles.module.css';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps): JSX.Element {
  return (
    <div className={styles.errorMessage}>
      <div>{message}</div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: '8px',
            padding: '6px 12px',
            background: 'var(--ifm-color-danger)',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
