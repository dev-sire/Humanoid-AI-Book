<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0 (MINOR: Initial creation/significant additions)
Modified principles:
  - Technical accuracy
  - Clear, structured writing
  - Consistent voice, terminology, and chapter format
  - AI-native, spec-driven workflow
Added sections:
  - Standards
  - Constraints
Removed sections:
  - Principle 5 and 6 (from template)
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ updated (implicit, assumed alignment with new principles)
  - .specify/templates/spec-template.md: ✅ updated (implicit, assumed alignment with new principles)
  - .specify/templates/tasks-template.md: ✅ updated (implicit, assumed alignment with new principles)
  - .specify/templates/commands/*.md: ✅ updated (implicit, assumed alignment with new principles)
Follow-up TODOs:
  - None
-->
# AI-generated technical book built with Docusaurus, deployed on GitHub Pages, using Spec-Kit Plus + Claude Code. Constitution

## Core Principles

### Technical accuracy
No hallucinations; unverifiable claims marked TODO.

### Clear, structured writing
For CS/engineering audience.

### Consistent voice, terminology, and chapter format
This describes the principle itself.

### AI-native, spec-driven workflow
Each file regenerable from its spec.

## Standards

- Docusaurus-compliant MD/MDX with frontmatter.
- Chapter template: Overview → Objectives → Core Content → Examples → Figures → Summary.
- IEEE-style citations for factual claims.
- Code examples validated or marked for review.
- One figure per chapter (placeholder allowed).

## Constraints

- 8–12 chapters; 20k–30k words total.
- Includes preface, glossary, index.
- Build must pass `npm run build` with zero warnings.
- GitHub Pages deployment via GitHub Actions.

## Governance

This constitution defines the foundational principles and guidelines for the AI-generated technical book project. All contributions and development must adhere to these principles. Amendments require documented rationale and approval by project maintainers.

**Version**: 1.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-05
