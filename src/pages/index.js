import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from '../css/module.module.css';
import Root from '@theme/Root';
import Translate from '@docusaurus/Translate';
import useBaseUrl from '@docusaurus/useBaseUrl';

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
              <Translate id="homepage.subtitle.part1">Bridging</Translate>{' '}
              <strong>
                <Translate id="homepage.subtitle.digital">
                  digital intelligence
                </Translate>
              </strong>{' '}
              <Translate id="homepage.subtitle.part2">with</Translate>{' '}
              <strong>
                <Translate id="homepage.subtitle.robotic">
                  real-world robotic systems
                </Translate>
              </strong>{' '}
              <Translate id="homepage.subtitle.part3">
                — from theory to deployment.
              </Translate>
            </p>

            <div className={styles.ctaRow}>
              <Link
                className="button button--primary button--lg"
                to={useBaseUrl('docs/intro')}
              >
                📘{' '}
                <Translate id="homepage.startReading">
                  Start Reading
                </Translate>
              </Link>

              <Link
                className="button button--outline button--lg"
                to={useBaseUrl('docs/glossary')}
              >
                📑{' '}
                <Translate id="homepage.glossary">
                  Glossary
                </Translate>
              </Link>
            </div>

            <div className={styles.meta}>
              <span>
                🧠 <Translate id="homepage.meta.physicalAI">Physical AI</Translate>
              </span>
              <span>
                🤖 <Translate id="homepage.meta.humanoids">Humanoids</Translate>
              </span>
              <span>
                ⚙️ <Translate id="homepage.meta.robotics">Real-World Robotics</Translate>
              </span>
            </div>
          </div>

          {/* RIGHT VISUAL */}
          <div className={styles.heroVisual}>
            <div className={styles.glow} />
            <img
              src={useBaseUrl('/img/robot.svg')}
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
          description="A practical guide to bridging AI with real-world robotic systems"
          >
          <HomepageHeader />
        </Layout>
    </Root>
  );
}
