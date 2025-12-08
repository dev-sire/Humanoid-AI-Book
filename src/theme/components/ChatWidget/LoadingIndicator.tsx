/**
 * LoadingIndicator component.
 *
 * Animated three-dot loading indicator.
 */

import React, { JSX } from 'react';
import styles from './styles.module.css';

export default function LoadingIndicator(): JSX.Element {
  return (
    <div className={styles.loadingIndicator}>
      <div className={styles.loadingDot}></div>
      <div className={styles.loadingDot}></div>
      <div className={styles.loadingDot}></div>
    </div>
  );
}
