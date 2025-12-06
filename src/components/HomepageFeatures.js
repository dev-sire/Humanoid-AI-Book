import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'From AI to Physical Intelligence',
    description: (
      <>
        Understand how intelligence moves from simulation to the real world —
        covering perception, decision pipelines, and embodiment in robots.
      </>
    ),
  },
  {
    title: 'Humanoid Robotics Systems',
    description: (
      <>
        Deep dive into humanoid architecture including sensing, locomotion,
        manipulation, and real-time control constraints.
      </>
    ),
  },
  {
    title: 'Bridging Theory & Deployment',
    description: (
      <>
        Learn how algorithms survive contact with reality — latency,
        uncertainty, hardware limits, and safety-critical design.
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <h3 className={styles.featureTitle}>{title}</h3>
        <p className={styles.featureDescription}>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <header className={styles.sectionHeader}>
          <h2>What This Book Covers</h2>
          <p>
            A structured journey from foundational concepts to real-world
            physical AI and humanoid robotics systems.
          </p>
        </header>

        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
