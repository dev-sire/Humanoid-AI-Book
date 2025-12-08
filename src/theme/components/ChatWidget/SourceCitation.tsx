/**
 * SourceCitation component.
 *
 * Displays source citations with title, score, and clickable link.
 */

import React, { JSX } from 'react';
import styles from './styles.module.css';
import { Source } from './api/chatApi';

interface SourceCitationProps {
  sources: Source[];
}

/**
 * Convert file path to Docusaurus URL.
 *
 * Examples:
 * - "nvidia-isaac-platform/isaac-sdk-and-sim/index.mdx" -> "/ai-native-book/docs/nvidia-isaac-platform/isaac-sdk-and-sim"
 * - "robot-simulation-gazebo/index.mdx" -> "/ai-native-book/docs/robot-simulation-gazebo"
 * - "intro.md" -> "/ai-native-book/docs/intro"
 */
function filePathToUrl(filePath: string): string {
  // Remove file extension
  let path = filePath.replace(/\.(mdx?|md)$/, '');

  // Remove trailing /index
  path = path.replace(/\/index$/, '');

  // Add baseUrl and docs prefix
  return `/ai-native-book/docs/${path}`;
}

export default function SourceCitation({ sources }: SourceCitationProps): JSX.Element {
  if (sources.length === 0) {
    return <p></p>;
  }

  return (
    <div className={styles.sources}>
      <h4>📚 Sources:</h4>
      {sources.map((source, index) => (
        <div key={`${source.file_path}-${index}`} className={styles.sourceItem}>
          <a href={filePathToUrl(source.file_path)} target="_blank" rel="noopener noreferrer">
            {source.title}
          </a>
          <span className={styles.sourceScore}>
            ({Math.round(source.relevance_score * 100)}% relevant)
          </span>
        </div>
      ))}
    </div>
  );
}
