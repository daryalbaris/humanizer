# User Story 3: Adversarial Paraphrasing Engine

**Story ID:** STORY-003
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** Critical (Core Functionality)
**Estimated Effort:** 3 weeks (60 hours)
**Dependencies:** STORY-001, STORY-002

---

## User Story

**As a** Claude agent orchestrator
**I want** to generate paraphrased text across 5 aggression levels and perform translation chains
**So that** I can achieve 87.88% detection reduction through iterative, adaptive humanization

---

## Description

Implement the 5-level adversarial paraphrasing capabilities using Claude agent's direct inference. The orchestrator (Claude) generates paraphrased text, and paraphraser_processor.py handles post-processing (term restoration, validation).

**Key Clarification:** Claude agent performs paraphrasing via direct inference. Python component `paraphraser_processor.py` receives already-paraphrased text and performs post-processing only.

---

## Acceptance Criteria

### Paraphrasing Levels (Claude Agent Direct Inference)

- [ ] **Level 1 (Gentle):** Minor synonym substitution, preserve structure
- [ ] **Level 2 (Moderate):** Sentence restructuring, varied transitions
- [ ] **Level 3 (Aggressive):** Major structural changes, active ↔ passive voice
- [ ] **Level 4 (Intensive):** Aggressive paraphrasing + section reordering
- [ ] **Level 5 (Nuclear):** Maximum variation, acceptable BERTScore drop to 0.90

### Post-Processing Component (paraphraser_processor.py)

- [ ] stdin/stdout JSON interface functional
- [ ] Receives paraphrased text from Claude orchestrator
- [ ] Restores protected terms with exact original formatting
- [ ] Validates numerical accuracy (±5% tolerance)
- [ ] Checks formatting preservation (subscripts, superscripts, Greek letters)
- [ ] Verifies citation integrity
- [ ] Performance: <1 second processing time

### Adaptive Aggression Selection

- [ ] Aggression increases if detection score stagnant for 2 iterations
- [ ] Section-specific strategies applied (IMRAD detection + rules)
- [ ] Early termination if <2% improvement per iteration

### Translation Chain Methodology

- [ ] Multi-hop translation: English → German → Japanese → English
- [ ] Trigger: If detection improvement <5% after 3 consecutive iterations
- [ ] Claude orchestrator performs translations (multilingual capabilities)
- [ ] paraphraser_processor.py receives translated text
- [ ] Quality validation: BERTScore ≥0.90 after translation chain
- [ ] User-controllable (optional feature)
- [ ] Processing time: +2-4 minutes when translation chain used

### Iterative Refinement

- [ ] Max 7 iterations implemented
- [ ] Early termination working (if no improvement)
- [ ] Token usage tracking accurate within 5%
- [ ] Quality maintained: BERTScore ≥0.92 across aggression levels (except nuclear: ≥0.90)

---

## Tasks

1. **Design Paraphrasing Prompts** (12 hours) - Claude agent prompt engineering
2. **Implement paraphraser_processor.py** (10 hours) - Post-processing tool
3. **Adaptive Aggression Logic** (8 hours) - Decision-making algorithm
4. **Translation Chain Integration** (12 hours) - Multi-hop translation
5. **Section-Specific Strategies** (8 hours) - IMRAD conventions
6. **Iterative Loop & Termination** (6 hours) - Max 7 iterations logic
7. **Testing & Quality Validation** (4 hours)

---

## Risks & Mitigations

**Risk:** Semantic drift at nuclear aggression (BERTScore 0.90-0.91)
**Mitigation:** Nuclear level reserved for desperate cases, user notification, manual review

**Risk:** Diminishing returns after 3-5 iterations
**Mitigation:** Early termination if <2% improvement, alert user to hard case

**Risk:** Translation chain quality drop
**Mitigation:** Quality validation before accepting, user notification

---

## Definition of Done

- [ ] All 5 aggression levels functional with distinct strategies
- [ ] paraphraser_processor.py: stdin/stdout JSON, <1s performance
- [ ] Adaptive aggression: increases when stagnant
- [ ] Translation chain: EN→DE→JA→EN functional, BERTScore ≥0.90
- [ ] Iterative loop: max 7 iterations, early termination working
- [ ] Quality targets met: BERTScore ≥0.92 (gentle-intensive), ≥0.90 (nuclear)
- [ ] Token usage tracking within 5% accuracy
- [ ] Unit tests: 80%+ coverage for paraphraser_processor.py
- [ ] Integration test: Full paraphrasing cycle with term protection

---

## Related Documents

- PRD: `docs/prd.md` (Epic 3)
- Architecture: `docs/architecture.md` (Section 5.3.1, 5.3.3)
