# Epic: AI Humanizer System

**Epic ID:** EPIC-001
**Version:** 1.0
**Date:** 2025-10-30
**Status:** Ready for Implementation
**Priority:** Critical
**Estimated Effort:** 19.5 weeks (385 hours)

---

## Epic Goal

Build a complete AI text humanization system that transforms AI-generated academic papers in materials science/metallurgy into human-like text that evades AI detection tools (Originality.ai, Turnitin) while preserving technical accuracy, semantic meaning, and domain-specific terminology.

**Target Success Rate:** 90-95% of papers achieve <20% AI detection score

---

## Epic Description

### Problem Statement

AI detection tools have reached 99%+ accuracy on raw AI-generated text. Academic writing in materials science faces a unique challenge: the formal, technical prose required by scientific journals inherently exhibits characteristics that trigger AI detection (low perplexity, consistent structure, domain-specific terminology).

### Solution Overview

The AI Humanizer System addresses this through a Claude Code agent orchestrator coordinating specialized Python computational tools:

**Architecture Pattern:** Orchestrator-Worker
- **Orchestrator:** Claude agent (running in Claude Code) performs all AI tasks via direct inference
- **Workers:** 9 Python tools execute computational tasks (NLP analysis, scoring, validation, state management)
- **No Additional APIs:** All capabilities included in user's Claude Code subscription

**Core Capabilities:**
1. **Context-Aware Term Protection** (95-98% accuracy) - 3-tier protection strategy
2. **Adversarial Paraphrasing** (5 aggression levels) - gentle → nuclear
3. **Translation Chain** (EN→DE→JA→EN for hard cases)
4. **AI Fingerprint Removal** (15+ patterns detected and removed)
5. **6-Dimension Burstiness Enhancement** (structural entropy across length, structure, beginnings, grammar, clauses, voice)
6. **Reference Text Learning** (extract style from user-provided human examples)
7. **Detection Proxy** (Claude agent analysis + GPT-2 perplexity measurement)
8. **Quality Validation** (BERTScore ≥0.92, BLEU ≥0.80, term preservation)
9. **Human-in-Loop Integration** (3-5 strategic injection points per paper)

### Technology Stack

**Orchestrator:**
- Claude Code agent (user's subscription)
- Direct AI inference for paraphrasing, detection analysis, translation

**Python Tools (Computational Workers):**
- Python 3.11.x
- spaCy 3.7+ with en_core_web_trf transformer model
- transformers 4.35+ (GPT-2 base for perplexity)
- bert-score 0.3.13+ (semantic similarity)
- nltk 3.8+ (BLEU score)
- Pydantic 2.5+ (validation)

**Storage:**
- File-based (JSON/JSONL)
- No database required

---

## Business Value

### Primary Benefits

1. **Detection Evasion:** 90-95% success rate achieving <20% detection on Originality.ai
2. **Quality Preservation:** Semantic similarity ≥0.92, 95-98% term preservation
3. **Efficiency:** 15-30 minutes processing time per 6,000-8,000 word paper
4. **Cost-Effective:** Token usage included in Claude Code subscription (200K-350K input, 100K-180K output)
5. **Human-in-Loop:** Expert input at strategic points without complete rewriting

### Target Users

- PhD candidates in materials science/metallurgy
- Researchers publishing in academic journals (ScienceDirect, Elsevier, Springer)
- Academic professionals requiring detection-resistant AI assistance

---

## Stories

This epic contains 8 user stories, each representing a major component of the system:

1. **Story 1:** Development Environment & Infrastructure Setup (2 weeks, 40 hours)
2. **Story 2:** Metallurgy Glossary & Term Protection System (2 weeks, 45 hours)
3. **Story 3:** Adversarial Paraphrasing Engine (3 weeks, 60 hours)
4. **Story 4:** AI Fingerprint Removal & Burstiness Enhancement (3 weeks, 55 hours)
5. **Story 5:** Reference Text Analysis & Style Learning (2.5 weeks, 50 hours)
6. **Story 6:** Detection Analysis & Quality Validation (2 weeks, 40 hours)
7. **Story 7:** Orchestrator Agent & Workflow Management (3 weeks, 55 hours)
8. **Story 8:** Testing, Documentation & Deployment (2 weeks, 40 hours)

**Story Details:** See individual story documents in `docs/stories/`

---

## Dependencies

### External Dependencies

**User Requirements:**
- Active Claude Code subscription
- Local Python 3.11+ environment
- 8 GB RAM minimum, 16 GB recommended
- 5 GB storage (ML models + papers)

**No Additional API Keys Required:**
- No Anthropic API key (included in Claude Code)
- No detection service APIs (Originality.ai, GPTZero)
- No translation APIs (DeepL, Google Translate)

### Story Dependencies

**Critical Path (Sequential):**
Story 1 → Story 2 → Story 3 → Story 6 → Story 7 → Story 8

**Parallel Opportunities:**
- Story 4 and Story 5 can run parallel with Story 3

---

## Success Criteria

### Functional Success Criteria

- [ ] System processes markdown input (6,000-8,000 words)
- [ ] 95-98% technical term preservation accuracy
- [ ] Context-aware protection with 3-tier strategy functional
- [ ] 5 aggression levels (gentle → nuclear) implemented
- [ ] Translation chain (EN→DE→JA→EN) working for hard cases
- [ ] 15+ AI fingerprint patterns detected and removed
- [ ] 6-dimension burstiness enhancement functional
- [ ] Reference text learning extracts style from 1-5 examples
- [ ] Claude agent detection analysis provides 0-100% scores
- [ ] GPT-2 perplexity measurement (target 55-75 range)
- [ ] BERTScore ≥0.92, BLEU ≥0.80 maintained
- [ ] 3-5 human injection points identified and functional
- [ ] Checkpoint-resume capability working
- [ ] Processing time: 15-30 minutes per paper

### Quality Success Criteria

- [ ] **90-95% success rate:** Papers achieve <20% Originality.ai detection
- [ ] **Semantic similarity:** BERTScore ≥0.92 on 90%+ of iterations
- [ ] **Fluency:** BLEU ≥0.80 on 95%+ of iterations
- [ ] **Term preservation:** 95-98% accuracy (context-aware)
- [ ] **Numerical accuracy:** ±5% tolerance maintained
- [ ] **Perplexity target:** 55-75 range achieved on 90%+ papers

### Technical Success Criteria

- [ ] All 9 Python tools follow stdin/stdout JSON interface
- [ ] Unit test coverage ≥80%
- [ ] Integration tests pass (end-to-end, checkpoint recovery)
- [ ] Docker container builds and runs successfully
- [ ] Installation guide tested on Windows, macOS, Linux
- [ ] Performance benchmarks documented
- [ ] Error handling functional (retries, graceful degradation)
- [ ] Logging captures all component interactions

---

## Risks & Mitigation

### High-Priority Risks

**Risk 1: Detection Proxy Correlation Uncertainty**
- **Description:** Claude agent's detection analysis has estimated 60-75% correlation with Originality.ai
- **Impact:** Papers may pass proxy but fail actual detection
- **Mitigation:**
  - Conservative <15% proxy target (maps to 15-25% Originality.ai)
  - User validates first 5-10 papers on actual Originality.ai
  - Collect user feedback for proxy calibration refinement

**Risk 2: Semantic Drift at Nuclear Aggression**
- **Description:** BERTScore may drop to 0.90-0.91 at nuclear aggression level
- **Impact:** Loss of technical accuracy and meaning
- **Mitigation:**
  - Nuclear level reserved for desperate cases only
  - User notification before nuclear application
  - Manual review option before finalizing

**Risk 3: Glossary Gaps for Specialized Domains**
- **Description:** 100-150 core terms may not cover all specialized metallurgy subdomains
- **Impact:** Important technical terms not protected, paraphrased incorrectly
- **Mitigation:**
  - User-friendly YAML interface for custom term addition
  - Potential term detection (title-case, hyphenated compounds)
  - Domain extension glossaries available
  - Detailed logging of protection decisions

**Risk 4: Burstiness Enhancement Complexity**
- **Description:** 6-dimension structural analysis may exceed 10-second target
- **Impact:** Longer processing times, user frustration
- **Mitigation:**
  - Optimize spaCy parsing (batch processing, caching)
  - Parallel processing where possible
  - GPU acceleration option for BERTScore (45s → 10s)

### Medium-Priority Risks

**Risk 5: Translation Chain Quality Drop**
- **Description:** EN→DE→JA→EN may reduce BERTScore to 0.90
- **Impact:** Slight semantic drift in hard cases
- **Mitigation:**
  - Translation chain is optional, user-controllable
  - Only triggered if detection improvement <5% after 3 iterations
  - Quality validation before accepting translated version

**Risk 6: Reference Text AI Contamination**
- **Description:** Users may provide AI-generated reference texts
- **Impact:** System learns AI patterns instead of human style
- **Mitigation:**
  - Mandatory AI detection validation on reference texts
  - Clear warnings if >30% AI-like
  - Option to proceed without contaminated references

---

## Acceptance Criteria

### Epic Completion Criteria

The epic is considered complete when:

1. **All 8 Stories Completed:**
   - Each story meets individual acceptance criteria
   - Story dependencies satisfied in correct sequence

2. **End-to-End System Functional:**
   - User can process a markdown paper start-to-finish
   - Checkpoint-resume works after interruption
   - Human injection points prompt correctly
   - Final humanized output generated

3. **Success Rate Validation:**
   - Tested on 20+ sample papers (6,000-8,000 words)
   - 90-95% achieve <20% on Originality.ai
   - BERTScore ≥0.92 maintained on 90%+
   - Term preservation 95-98% accuracy

4. **Production Readiness:**
   - Docker container deployable
   - Installation guide validated on 3 platforms
   - Unit test coverage ≥80%
   - Integration tests passing
   - Documentation complete (user + developer guides)

5. **Performance Targets Met:**
   - Processing time: 15-30 minutes per paper
   - Token usage: 200K-350K input, 100K-180K output
   - Memory usage: <3 GB RAM
   - Each tool performs within specified targets

---

## Timeline & Milestones

**Total Estimated Duration:** 19.5 weeks (sequential), 14-16 weeks (with parallelization)

### Phase 1: Foundation (Weeks 1-4)
- **Milestone 1.1:** Development environment operational (Week 2)
- **Milestone 1.2:** Term protection system functional (Week 4)

### Phase 2: Core Humanization (Weeks 5-11)
- **Milestone 2.1:** Paraphrasing engine complete (Week 8)
- **Milestone 2.2:** Burstiness & fingerprint removal complete (Week 11)

### Phase 3: Enhancement & Validation (Weeks 12-15)
- **Milestone 3.1:** Reference text learning functional (Week 13.5)
- **Milestone 3.2:** Detection & quality validation complete (Week 15)

### Phase 4: Integration & Deployment (Weeks 16-19.5)
- **Milestone 4.1:** Orchestrator agent operational (Week 18)
- **Milestone 4.2:** Testing & documentation complete (Week 19.5)
- **Milestone 4.3:** Production deployment (Week 19.5)

---

## Related Documents

- **PRD:** `docs/prd.md` (v1.1) - Product Requirements Document
- **Architecture:** `docs/architecture.md` (v1.0) - Backend Architecture
- **Architecture Update Summary:** `docs/ARCHITECTURE_UPDATE_SUMMARY.md` - Claude Code execution model clarification
- **Stories:** `docs/stories/story-*.md` - Individual user story documents

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-30 | John (Product Manager) | Initial epic creation from PRD v1.1. Converted 8 PRD epics into 8 user stories under this single epic. |

---

**Epic Status:** ✅ Ready for Story Development
**Next Step:** Create detailed user stories in `docs/stories/` directory
