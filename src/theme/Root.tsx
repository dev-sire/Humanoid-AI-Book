/**
 * Root component (swizzled from Docusaurus).
 *
 * Wraps the entire application and adds global ChatWidget.
 */

import React, { JSX, lazy, Suspense } from 'react';

// Lazy load ChatWidget for better performance
const ChatWidget = lazy(() => import('./components/ChatWidget'));

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <>
      {children}
      <Suspense fallback={<p>loading...</p>}>
        <ChatWidget />
      </Suspense>
    </>
  );
}
