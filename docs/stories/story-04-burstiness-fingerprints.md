# User Story 4: AI Fingerprint Removal & Burstiness Enhancement

**Story ID:** STORY-004
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** High (Detection Evasion - Structural Entropy)
**Estimated Effort:** 3 weeks (55 hours)
**Dependencies:** STORY-001

---

## User Story

**As a** user humanizing AI-generated papers
**I want** AI fingerprints removed and 6-dimension structural variety injected
**So that** stylistic tells are eliminated and structural entropy matches human writing patterns

---

## Description

Implement pattern-based AI fingerprint detection and removal, controlled human imperfection injection, and comprehensive burstiness enhancement across 6 dimensions. These components address stylistic tells beyond semantic patterns.

---

## Acceptance Criteria

### Fingerprint Remover (fingerprint_remover.py)

- [ ] stdin/stdout JSON interface functional
- [ ] 15+ AI filler phrase patterns detected and removed
- [ ] AI punctuation tell fixes (em dashes, comma-linked clauses)
- [ ] Parallel structure breaking (X, Y, and Z → varied structures)
- [ ] Excessive hedging removal ("may potentially" → "may")
- [ ] Pattern database (JSON, version-controlled, user-extensible)
- [ ] Performance: <3 seconds on 8,000-word paper

### Burstiness Enhancer (burstiness_enhancer.py)

- [ ] **Dimension 1:** Sentence length variation by section (Methods 15-28 words, Discussion 22-28)
- [ ] **Dimension 2:** Sentence structure variation (simple, compound, complex, compound-complex mix)
- [ ] **Dimension 3:** Beginning word diversity (track sentence-starting patterns, force alternation)
- [ ] **Dimension 4:** Grammatical variety (90-95% declarative, 1-2 interrogative in Discussion)
- [ ] **Dimension 5:** Clause variation (60% independent-only, 40% mixed)
- [ ] **Dimension 6:** Active/passive voice mixing (75-85% passive in Methods, 40% in Discussion)
- [ ] spaCy dependency parsing for structure detection
- [ ] Structural entropy measurement quantifies variation
- [ ] Performance: <10 seconds on 8,000-word paper

### Human Imperfection Injector (imperfection_injector.py)

- [ ] Controlled disfluencies (Discussion/Conclusion: 2-4 per section)
- [ ] Strategic contractions (10% ratio in informal sections)
- [ ] Minor structural variations (comma placement, synonym substitution)
- [ ] Section-aware density (Abstract/Methods: 0.002, Discussion: higher)

---

## Tasks

1. **Fingerprint Pattern Database** (8 hours)
2. **Implement fingerprint_remover.py** (10 hours)
3. **Implement burstiness_enhancer.py** (20 hours) - 6 dimensions
4. **Implement imperfection_injector.py** (8 hours)
5. **spaCy Dependency Parsing Integration** (6 hours)
6. **Testing & Validation** (3 hours)

---

## Risks & Mitigations

**Risk:** Over-injection of imperfections sounds unprofessional
**Mitigation:** Conservative density limits, section-aware rules, user-configurable thresholds

**Risk:** Structural variation introduces grammatical errors
**Mitigation:** spaCy validation before applying changes, quality check pass

**Risk:** Complex burstiness analysis increases processing time
**Mitigation:** Optimize spaCy parsing (batch processing, caching), target <10s

---

## Definition of Done

- [ ] Fingerprint remover: 15+ patterns detected and removed
- [ ] All 6 burstiness dimensions functional with section-specific targets
- [ ] Structural entropy measurement working
- [ ] Imperfection injection density matches requirements
- [ ] Combined effect: 10-15% additional detection reduction
- [ ] Performance targets met: <10 seconds total on 8K words
- [ ] Unit tests: 80%+ coverage for all 3 components
- [ ] Pattern database extensible via JSON

---

## Related Documents

- PRD: `docs/prd.md` (Epic 4)
- Architecture: `docs/architecture.md` (Section 5.3.4, 5.3.5)
