# User Story 6: Detection Analysis & Quality Validation

**Story ID:** STORY-006
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** Critical (Core Functionality)
**Estimated Effort:** 2 weeks (40 hours)
**Dependencies:** STORY-001

---

## User Story

**As a** Claude agent orchestrator
**I want** to analyze text for AI detection likelihood and validate quality metrics
**So that** I can provide feedback for iterative refinement and ensure semantic preservation

---

## Description

Implement detection analysis via Claude agent's direct reasoning and quality validation system (BERTScore, BLEU, perplexity). Provides feedback loop for iterative refinement.

**Key Clarification:** Claude agent performs detection analysis via direct reasoning. Python component `detector_processor.py` receives analysis results and formats them.

---

## Acceptance Criteria

### Detection Analysis (Claude Agent Direct Reasoning)

- [ ] Claude agent analyzes text and estimates AI detection likelihood (0-100%)
- [ ] Section-level detection heatmap identifies high-risk sections
- [ ] AI pattern hotspot identification (sentence-level flagging)
- [ ] Conservative threshold strategy: target <15% (maps to 15-25% Originality.ai)
- [ ] Detection score confidence intervals acknowledge 60-75% correlation uncertainty

### Detection Processor (detector_processor.py)

- [ ] stdin/stdout JSON interface functional
- [ ] Receives detection results from Claude orchestrator
- [ ] Generates formatted detection scores + heatmap
- [ ] Performance: <1 second (parsing only, no AI inference)

### Perplexity Calculator (perplexity_calculator.py)

- [ ] GPT-2 base model integration for perplexity measurement (local, no API)
- [ ] Tracks perplexity per iteration (target: 55-75 range, human-like)
- [ ] Section-level perplexity analysis identifies low-perplexity sections
- [ ] Flags papers failing to increase perplexity after 3 iterations
- [ ] Prioritizes low-perplexity sections for aggressive paraphrasing
- [ ] Performance: ~5 seconds on 8,000-word paper (CPU)

### Quality Validator (validator.py)

- [ ] BERTScore calculation (semantic similarity, target ≥0.92)
- [ ] BLEU score calculation (fluency, target ≥0.80)
- [ ] Technical term preservation verification (95-98% of protected terms present)
- [ ] Quantitative accuracy check (±5% tolerance for numerical values)
- [ ] Quality violation flagging for user review
- [ ] Performance: ~45 seconds (BERTScore slow on CPU, ~10s with GPU)

### Calibration System

- [ ] User feedback collection (actual Originality.ai scores)
- [ ] Proxy correlation refinement over time
- [ ] Domain-specific calibration (metallurgy papers)

---

## Tasks

1. **Implement detector_processor.py** (8 hours) - Format detection results
2. **Implement perplexity_calculator.py** (10 hours) - GPT-2 perplexity
3. **Implement validator.py** (12 hours) - BERTScore, BLEU, term preservation
4. **Calibration System** (6 hours) - User feedback collection
5. **Testing & Validation** (4 hours)

---

## Risks & Mitigations

**Risk:** Proxy correlation degrades over time (Originality.ai updates)
**Mitigation:** User feedback loop, periodic recalibration, conservative threshold

**Risk:** BERTScore computation slow (45 seconds)
**Mitigation:** GPU acceleration if available, batch computation optimization

**Risk:** False sense of security from <15% proxy score
**Mitigation:** Clear documentation about 60-75% correlation, recommend validation

---

## Definition of Done

- [ ] Detection analysis: Claude agent provides 0-100% scores with confidence intervals
- [ ] detector_processor.py: Formats detection results, <1s performance
- [ ] Perplexity calculator: Measures text predictability, 55-75 target range
- [ ] BERTScore ≥0.92 achieved on 90%+ of iterations
- [ ] BLEU ≥0.80 achieved on 95%+ of iterations
- [ ] Term preservation: 95-98% accuracy
- [ ] Quantitative accuracy: ±5% tolerance
- [ ] User feedback system functional
- [ ] Performance targets met: Detection <1s, Perplexity ~5s, Quality ~45s
- [ ] Unit tests: 80%+ coverage for all 3 components

---

## Related Documents

- PRD: `docs/prd.md` (Epic 6)
- Architecture: `docs/architecture.md` (Section 5.3.6, 5.3.7, 5.3.8)
