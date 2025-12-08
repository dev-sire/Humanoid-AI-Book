import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from '../css/module.module.css';
import Root from '@theme/Root';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();

  return (
    <header className={styles.hero}>
      <div className="container">
        <div className={styles.heroGrid}>
          
          {/* LEFT CONTENT */}
          <div className={styles.heroContent}>
            <h1 className={styles.title}>
              {siteConfig.title}
            </h1>

            <p className={styles.subtitle}>
              Bridging <strong>digital intelligence</strong> with 
              <strong> real-world robotic systems</strong> — from theory to deployment.
            </p>

            <div className={styles.ctaRow}>
              <Link
                className="button button--primary button--lg"
                to="/docs/intro">
                📘 Start Reading
              </Link>

              <Link
                className="button button--outline button--lg"
                to="/docs/glossary">
                📑 Glossary
              </Link>
            </div>

            <div className={styles.meta}>
              <span>🧠 Physical AI</span>
              <span>🤖 Humanoids</span>
              <span>⚙️ Real-World Robotics</span>
            </div>
          </div>

          {/* RIGHT VISUAL */}
          <div className={styles.heroVisual}>
            <div className={styles.glow} />
            <img
              src="/img/robot.svg"
              alt="Physical AI illustration"
            />
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  return (
    <Root>
      <Layout
        title="Physical AI & Humanoid Robotics"
        description="A practical guide to bridging AI with real-world robotic systems">
        <HomepageHeader />
      </Layout>
    </Root>
  );
}
