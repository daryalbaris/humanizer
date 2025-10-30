# User Story 2: Metallurgy Glossary & Term Protection System

**Story ID:** STORY-002
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** Critical (Core Functionality)
**Estimated Effort:** 2 weeks (45 hours)
**Dependencies:** STORY-001

---

## User Story

**As a** user processing metallurgy papers
**I want** context-aware protection of technical terms with 95-98% accuracy
**So that** domain-specific terminology is preserved while allowing paraphrasing flexibility

---

## Description

Build the context-aware term protection system with tiered glossary (Tier 1: always protect, Tier 2: context-dependent, Tier 3: flexible synonyms). This component ensures 95-98% technical term preservation while allowing paraphrasing flexibility to break AI patterns.

---

## Acceptance Criteria

###  Glossary Compilation

- [ ] Metallurgy glossary contains 100-150 core terms with tier classifications
- [ ] Alloy designations: 80+ terms (AISI, SAE, EN, JIS standards)
- [ ] Phase names: 50+ terms (austenite, martensite, ferrite, etc.)
- [ ] Techniques/equipment: 70+ terms (SEM, TEM, XRD, manufacturers)
- [ ] Properties: 50+ terms (hardness, grain size terminology)
- [ ] Glossary data structure: JSON with tiers, context rules, synonyms

### Term Protection Component (term_protector.py)

- [ ] stdin/stdout JSON interface functional
- [ ] spaCy NLP context analysis implemented
- [ ] Tiered protection logic (Tier 1/2/3 decision tree) working
- [ ] Placeholder replacement mechanism ({{TERM_N}}, {{NUM_N}}) bijective
- [ ] Term restoration after paraphrasing with 100% accuracy
- [ ] Context-aware protection achieves 95-98% accuracy on test papers
- [ ] Performance: <2 seconds for protection + restoration on 8,000-word paper

### Numerical & Equipment Protection

- [ ] Numerical values preserved: 850°C ± 25°C, grain size: 45 μm
- [ ] Equipment specifications protected 100%: JSM-7001F, JEOL, 20 kV
- [ ] Measurement units preserved: μm, nm, GPa, HV, etc.
- [ ] Statistical values preserved: mean ± std dev, confidence intervals

### User Extensibility

- [ ] User can add custom terms via YAML without code changes
- [ ] Potential technical term detection (title-case compounds, hyphenated terms)
- [ ] System detects unprotected technical terms and prompts user
- [ ] Detailed logging of protection decisions for debugging

---

## Tasks

1. **Compile Metallurgy Glossary** (12 hours)
2. **Implement spaCy Context Analysis** (8 hours)
3. **Build Tiered Protection Logic** (10 hours)
4. **Implement Placeholder System** (6 hours)
5. **Add User Extension Interface** (4 hours)
6. **Testing & Validation** (5 hours)

---

## Risks & Mitigations

**Risk:** 2-5% context misinterpretation (Tier 2 terms)
**Mitigation:** Conservative Tier 2 rules, user feedback loop, detailed logging

**Risk:** Glossary gaps for specialized domains
**Mitigation:** Domain extension glossaries, user-friendly addition interface

---

## Definition of Done

- [ ] 100-150 core terms in glossary with tier classifications
- [ ] Context-aware protection: 95-98% accuracy validated on 10+ test papers
- [ ] Placeholder replacement: Bijective (no term loss)
- [ ] User can extend glossary via YAML
- [ ] Performance target met: <2 seconds on 8K words
- [ ] Unit tests: 80%+ coverage for term_protector.py
- [ ] Integration test: Full protection → paraphrasing → restoration cycle

---

## Related Documents

- PRD: `docs/prd.md` (Epic 2)
- Architecture: `docs/architecture.md` (Section 5.3.2: term_protector.py)
