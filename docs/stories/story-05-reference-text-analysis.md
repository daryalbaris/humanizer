# User Story 5: Reference Text Analysis & Style Learning

**Story ID:** STORY-005
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** High (Enhancement)
**Estimated Effort:** 2.5 weeks (50 hours)
**Dependencies:** STORY-001, STORY-002

---

## User Story

**As a** user providing human-written reference texts
**I want** the system to extract and learn stylistic patterns from my examples
**So that** humanization matches authentic writing style beyond generic patterns

---

## Description

Implement the optional reference text analysis feature that extracts style patterns from user-provided human-written examples. Enhances personalization beyond generic humanization.

---

## Acceptance Criteria

### Reference Text Analyzer (reference_analyzer.py)

- [ ] stdin/stdout JSON interface functional
- [ ] Accepts 1-5 reference texts in markdown format
- [ ] Sentence length distribution captured (mean, std dev, quantiles)
- [ ] Transition phrase vocabulary extracted (50+ unique phrases per reference)
- [ ] Voice/tense ratios calculated (active/passive, past/present)
- [ ] Structural conventions identified (paragraph organization, citation styles)
- [ ] Pattern synthesis merges patterns from multiple references
- [ ] Performance: <30 seconds for reference analysis (one-time per paper)

### Reference Text Validation

- [ ] AI detection on reference texts (warn if >30% AI-like)
- [ ] Topic similarity to input paper (semantic similarity, warn if <40% overlap)
- [ ] Quality metrics (sentence length, vocabulary diversity, coherence)
- [ ] Warnings displayed if validation fails

### Style-Guided Paraphrasing Integration

- [ ] Learned patterns injected into paraphrasing prompts
- [ ] Blends reference style with target journal conventions
- [ ] Fallback to generic conventions if no reference texts provided
- [ ] Token budget enforced: 50K max for references, warning if exceeded

---

## Tasks

1. **Implement reference_analyzer.py** (15 hours)
2. **Style Pattern Extraction** (12 hours)
3. **Reference Validation Logic** (8 hours)
4. **Paraphrasing Prompt Integration** (10 hours)
5. **Token Budget Management** (3 hours)
6. **Testing & Validation** (2 hours)

---

## Risks & Mitigations

**Risk:** User provides AI-generated reference texts
**Mitigation:** Mandatory AI detection validation, clear warnings, option to proceed without

**Risk:** Irrelevant reference texts degrade quality
**Mitigation:** Similarity check, quality metrics, user notification

**Risk:** Reference texts consume excessive token budget
**Mitigation:** 50K token limit enforced, truncation if exceeded

---

## Definition of Done

- [ ] System accepts 1-5 reference texts in markdown
- [ ] Style extraction: sentence length, transition phrases, voice/tense
- [ ] Reference validation: AI detection, similarity, quality checks functional
- [ ] Paraphrasing prompts incorporate learned style patterns
- [ ] Token budget enforced: 50K max
- [ ] Quality improvement: 2-5% better detection scores vs without references
- [ ] Unit tests: 80%+ coverage for reference_analyzer.py

---

## Related Documents

- PRD: `docs/prd.md` (Epic 5)
- Architecture: `docs/architecture.md` (Section 5.3.9)
