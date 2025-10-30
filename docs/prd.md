# Product Requirements Document: AI Humanizer System

**Version:** 1.2
**Date:** October 30, 2025
**Author:** Mary (Business Analyst Agent)
**Status:** Ready for Sprint Planning

---

## Goals and Background Context

### Goals

**Primary Goals:**

1. **Detection Evasion (Priority 1):** Reduce AI detection scores below 20% on Originality.ai and Turnitin for academic papers in materials science and metallurgy, with a target success rate of 90-95% of processed papers.

2. **Quality Preservation (Priority 1):** Maintain semantic similarity (BERTScore ≥0.92) and technical accuracy while humanizing text. Preserve 100% of domain-specific terminology (alloy designations, phase names, equipment specifications, crystallographic notation).

3. **Efficiency (Priority 2):** Process typical 6,000-8,000 word papers in 10-20 minutes with cost target of $0.50-$2.00 per paper (Claude API costs).

4. **Human-in-Loop Integration (Priority 2):** Enable seamless expert input at 3-5 strategic injection points (domain insights, observations, critiques) to maximize authenticity without requiring complete rewriting.

5. **Style Adaptability (Priority 2):** Support optional user-provided human-written reference texts about the topic to learn and match authentic writing patterns, enhancing personalization beyond generic humanization.

6. **Field Convention Compliance (Priority 3):** Adhere to metallurgy/materials science writing conventions (IMRAD structure, passive voice patterns, quantitative precision, equipment specification formats).

### Background Context

AI detection tools like Originality.ai and Turnitin have reached 99%+ accuracy on raw AI-generated text using modified BERT models, perplexity analysis, and stylistic fingerprint detection. However, academic writing in materials science and metallurgy faces a unique challenge: the formal, technical prose required by scientific journals inherently exhibits characteristics that trigger AI detection (low perplexity, consistent structure, domain-specific terminology).

This system addresses the "technical writing paradox" by combining adversarial paraphrasing techniques (87.88% detection reduction in research), domain-aware text processing (preserving metallurgical terminology and conventions), strategic human expertise injection, and optional style learning from user-provided reference texts. The solution uses a modular architecture where Claude Code orchestrates the workflow and specialized Python components handle detection, paraphrasing, quality validation, and term protection. Target papers are PhD-level materials science manuscripts in **markdown format** intended for publication in journals like those indexed by ScienceDirect.

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-28 | Mary (Business Analyst) | Initial PRD creation based on Phases 1-4 research. Incorporated user corrections: removed DeepL API dependency, markdown-only input format, added reference text feature. |
| 1.1 | 2025-10-28 | Mary (Business Analyst) | **Architecture Clarification:** Revised Technical Assumptions (1, 2) and Epic 7 to explicitly clarify Claude CLI agent architecture. User requested: "I want to run it in claude cli as an agent that is capable of using the other programs as a tool not with anthropic SDK as an ai program". Removed anthropic SDK from Python dependencies, added architectural diagram, clarified that Python programs are tools (stdin/stdout) executed via Bash, NOT SDK-based Python application. |

---

## Rationale & Key Assumptions

**Why This Approach:**

1. **Modular Architecture:** Separating concerns (term protection, paraphrasing, detection, validation) allows independent optimization and failure isolation. Each component can be tested, benchmarked, and improved independently.

2. **Claude Code Orchestration:** Leveraging Claude's reasoning capabilities for workflow coordination, decision-making (aggression level selection), and strategic planning, while delegating computational tasks to specialized Python components for performance.

3. **Adversarial Paraphrasing:** Research shows 87.88% average detection reduction with iterative paraphrasing. Multiple passes with increasing aggression levels (gentle → nuclear) provide adaptive evasion.

4. **Reference Text Learning (NEW):** Allowing users to provide human-written reference texts addresses the limitation of generic humanization patterns. System can extract authentic style patterns (sentence structures, transitions, voice) from real examples in the target domain.

5. **No DeepL API:** Removed back-translation approach to simplify dependencies and reduce costs. Claude Sonnet's paraphrasing capabilities are sufficient for achieving target detection scores when combined with fingerprint removal and imperfection injection.

6. **Markdown-Only Input:** Simplified file handling reduces complexity and potential parsing errors. Users can convert PDF/DOCX to markdown using external tools if needed, ensuring clean input for processing.

**Key Assumptions:**

- User has institutional or purchased access to AI detection tools (Originality.ai or Turnitin) for validation
- Input papers are complete drafts, not fragmentary sections
- User has domain expertise to provide meaningful input at injection points
- Claude API access with sufficient rate limits (Sonnet 3.5 for orchestration, Sonnet for detection)
- Processing environment supports Python 3.9+ with required dependencies (spaCy, transformers, bert-score)

---

## Parameter Decisions Summary

The following critical parameters were decided through structured elicitation (October 28, 2025):

### 1. Term Protection Strategy
**Decision:** Context-Aware Protection (95-98% accuracy)

**Rationale:**
- Provides 5-10% better paraphrasing flexibility compared to strict 100% protection
- Critical for breaking AI patterns around technical terms
- Accepts 2-5% risk of context misinterpretation
- Implements tiered protection: Always protect (Tier 1), Context-dependent (Tier 2), Flexible synonyms (Tier 3)

**Trade-offs:**
- **Pros:** Maximum paraphrasing flexibility, effective AI pattern disruption, allows natural variation
- **Cons:** Requires complex NLP context analysis, 2-5% risk of losing context-dependent technical terms, more testing needed

### 2. Detection Validation Approach
**Decision:** Proxy-Only with Conservative Threshold (<15% target)

**Rationale:**
- No Originality.ai API costs during processing (saves $3-$4 per paper)
- Conservative <15% target on Claude Sonnet proxy compensates for 60-75% correlation uncertainty
- Provides safety margin: 15% proxy likely maps to 15-25% on actual Originality.ai
- User validates final output externally on actual Originality.ai

**Trade-offs:**
- **Pros:** Zero detection API costs, fully automated workflow, no external dependencies
- **Cons:** May over-process papers (target 15% instead of 20%), slightly higher Claude API costs (+$0.20-$0.50), longer processing time (+5-10 minutes)

### 3. Cost vs Quality Priority
**Decision:** Maximize Success Rate ($2.00-$4.00 per paper)

**Rationale:**
- Target 95-98% success rate (vs 80-85% in budget mode or 90-95% in balanced mode)
- Allows up to 7 paraphrasing iterations (vs 3-5 in other modes)
- Enables aggressive-intensive aggression from start
- Includes all optional features: reference text analysis, imperfection injection, enhanced fingerprint removal

**Trade-offs:**
- **Pros:** Highest success rate, minimal manual refinement needed, all features enabled
- **Cons:** Higher cost per paper ($2-$4 vs $1-$2), longer processing time (15-30 min vs 10-20 min), higher API token usage

### 4. Failure Handling Strategy
**Decision:** Return Best Attempt + Report

**Rationale:**
- If <15% proxy score (<20% Originality.ai) not achieved after 7 iterations, return lowest-detection version
- Provides detailed report: detection score progression, section-level heatmap, problematic patterns, manual refinement guidance
- Does NOT automatically escalate to "nuclear" aggression (risk of semantic drift)
- Allows checkpoint-based resume with user edits integrated

**Trade-offs:**
- **Pros:** Transparent, actionable feedback, user maintains control, no risk of over-aggressive processing
- **Cons:** Requires manual refinement for 2-5% of papers, user must have Originality.ai access for final validation

---

## Requirements

### Functional Requirements

**FR-1: Markdown Paper Processing**
- System shall accept markdown-formatted academic papers as input (6,000-12,000 words typical)
- System shall preserve markdown formatting (headers, lists, tables, citations, footnotes)
- System shall parse IMRAD section structure (Introduction, Methods, Results, Discussion, Conclusion)

**FR-2: Technical Term Protection**
- System shall implement **context-aware protection** (95-98% accuracy target) using spaCy NLP analysis
- System shall use tiered protection strategy:
  - **Tier 1 (Always protect):** Alloy designations (AISI 304, Ti-6Al-4V), phase names (austenite, martensite, ferrite), crystallographic notation (FCC, BCC, HCP)
  - **Tier 2 (Context-dependent):** Technical terms with ambiguous meaning (grain → protect in "grain size" but allow rephrasing in "grain boundary" → "intergranular region")
  - **Tier 3 (Flexible synonyms):** Generic technical terms (microstructure → morphology, morphology → structure, interface → boundary)
- System shall preserve exact numerical values with units (850°C ± 25°C, grain size: 45 μm, etc.)
- System shall protect equipment specifications (JSM-7001F, JEOL, 20 kV, etc.)
- System shall use placeholder replacement mechanism during paraphrasing and restore original terms after processing
- **Rationale:** Context-aware protection provides 5-10% better paraphrasing flexibility, critical for breaking AI patterns around technical terms, while accepting 2-5% risk of context misinterpretation

**FR-3: Reference Text Analysis (NEW)**
- System shall accept optional user-provided human-written reference texts (1-5 documents, markdown format)
- System shall extract style patterns from reference texts: sentence length distribution, transition phrases, voice/tense patterns, structural conventions
- System shall use extracted patterns to guide paraphrasing decisions, blending reference style with target journal conventions
- System shall allow processing without reference texts (fallback to generic metallurgy conventions)

**FR-4: AI Fingerprint Removal**
- System shall detect and remove 15+ AI-typical filler phrases ("it is important to note that", "at its core", "in the ever-evolving landscape", etc.)
- System shall identify and fix AI punctuation tells (em dashes, comma-linked clauses with "which")
- System shall break parallel structure patterns (e.g., "X, Y, and Z" → varied structures)
- System shall remove excessive hedging language ("may potentially", "could possibly")

**FR-5: Adversarial Paraphrasing**
- System shall implement 5-level aggression paraphrasing (gentle, moderate, aggressive, intensive, nuclear)
- System shall use Claude Sonnet for context-aware paraphrasing maintaining technical meaning
- System shall apply section-specific paraphrasing strategies:
  - Abstract: Minimal changes (gentle)
  - Introduction: Moderate changes, preserve literature context
  - Methods: Aggressive changes while preserving procedure accuracy
  - Results: Moderate changes, preserve quantitative data
  - Discussion: Intensive changes for interpretative text
  - Conclusion: Moderate-to-aggressive changes
- **System shall implement optional translation chain methodology** for hard cases (iterations 5-7 if detection >20% after iteration 4):
  - **Multi-hop translation:** English → German → Japanese → English (using Claude translation prompts, no external API)
  - **Rationale:** Translation chains introduce linguistic variations that disrupt statistical patterns detectors recognize, while preserving semantic content
  - **Trigger condition:** If detection score improvement <5% after 3 consecutive iterations, offer translation chain to user
  - **Cost:** ~$0.30-$0.50 additional per paper (3 translation passes × ~10K tokens each)
  - **Expected benefit:** 10-15% additional detection reduction for hard cases
  - **User control:** Optional feature, user can enable/disable via config or approve when triggered

**FR-6: Burstiness Enhancement (EXPANDED - Structural Entropy)**
- **Sentence length variation** by section:
  - Abstract: 18-22 words (tighter for conciseness)
  - Introduction: 20-25 words (moderate variation)
  - Methods: 15-28 words (HIGH variation for procedural steps)
  - Results: 18-24 words (moderate, data-focused)
  - Discussion: 22-28 words (higher for complex arguments)
  - System shall avoid uniform length patterns (detect sequences of 5+ similar-length sentences)

- **Sentence structure variation** (HIGH structural entropy):
  - Mix simple, compound, complex, and compound-complex constructions
  - Target distribution per section:
    - Abstract/Methods: 60% simple, 30% compound, 10% complex (clarity-focused)
    - Introduction/Discussion: 30% simple, 40% compound, 25% complex, 5% compound-complex (variety-focused)
  - Detect and break sequences of 3+ sentences with identical structure type

- **Beginning word diversity**:
  - Avoid starting 3+ consecutive sentences with same word or structure
  - Track sentence beginnings: subject-verb, prepositional phrase, subordinate clause, adverb, etc.
  - Force alternation if pattern detected (e.g., "The results show..." → "Results indicate..." → "These findings demonstrate...")

- **Grammatical variety**:
  - Primarily declarative sentences (90-95%) for academic writing
  - Occasional interrogative sentences in Discussion (1-2 per section, rhetorical questions)
  - Rare exclamatory sentences (0-1 per paper, only if contextually appropriate)
  - Avoid excessive consistency (all declarative = AI tell)

- **Clause variation**:
  - Mix independent and dependent clause patterns
  - Target: 60% independent-only, 40% mixed independent-dependent
  - Vary dependent clause position (leading, trailing, embedded)
  - Avoid repetitive clause structures (detect and rewrite)

- **Active/passive voice mixing**:
  - Section-specific voice targets (from Phase 3 research):
    - Abstract: 70% passive, 30% active
    - Introduction: 50% passive, 50% active
    - Methods: 75-85% passive, 15-25% active (procedural convention)
    - Results: 60% passive, 40% active
    - Discussion: 40% passive, 60% active (interpretative voice)
  - Explicit alternation strategy: Avoid 4+ consecutive sentences in same voice
  - Voice detection using spaCy dependency parsing

- **Rationale:** Human writing shows high structural entropy across multiple dimensions. AI writing shows low entropy even with varied sentence length. Structural variation is a critical detection signal beyond just length.

**FR-7: Human Imperfection Injection**
- System shall inject controlled disfluencies in Discussion/Conclusion sections (2-4 per section): "That said,", "To be fair,", "Interestingly enough,"
- System shall add strategic contractions (10% ratio in informal sections): "isn't", "doesn't", "can't"
- System shall introduce minor structural variations: comma placement variation, synonym substitutions
- System shall maintain academic formality in Abstract/Methods/Results (minimal imperfections, density 0.002)

**FR-8: Strategic Injection Point Identification**
- System shall identify 3-5 strategic locations requiring human expert input:
  - Introduction: Domain insight (priority 5)
  - Results: Specific observation from experience (priority 4)
  - Discussion: Literature critique with expertise (priority 5)
  - Discussion: Domain-specific interpretation (priority 4)
  - Conclusion: Personal research direction (priority 3)
- System shall provide guidance prompts for each injection point (e.g., "Add specific observation from your research experience on grain boundary behavior...")
- System shall pause workflow at each injection point for user input
- System shall allow skipping injection points if user prefers automated processing

**FR-9: AI Detection Analysis**
- System shall evaluate text using **Claude Sonnet as detection proxy** (60-75% accuracy correlation with Originality.ai)
- System shall use **conservative threshold strategy:** target <15% on Claude Sonnet proxy (provides safety margin for 15-25% range on actual Originality.ai)
- System shall generate detection scores (0-100%) and confidence intervals
- System shall identify high-risk sections and AI-pattern hotspots for targeted refinement
- System shall support iterative refinement loop (max **7 iterations** for high-quality mode) until detection score <15%
- System shall provide section-level detection heatmap (identify which sections trigger detection most)
- **Rationale:** Conservative threshold compensates for proxy uncertainty; 7 iterations support "Maximize Success Rate" mode

**FR-14: Perplexity Measurement (NEW - CRITICAL ADDITION)**
- System shall calculate **perplexity scores** using GPT-2 or similar language model to measure text predictability
- System shall track perplexity per iteration to ensure improvement toward human range
- **Target perplexity range:**
  - AI-generated text: 20-40 (low perplexity, highly predictable)
  - Human-written text: 50-80 (higher perplexity, less predictable)
  - System target: Increase perplexity from initial score to 55-75 range
- System shall provide section-level perplexity analysis (identify low-perplexity sections)
- System shall flag papers that fail to increase perplexity after 3 iterations (hard case indicator)
- System shall prioritize low-perplexity sections for aggressive paraphrasing
- **Rationale:** Perplexity is the primary signal used by BERT-based detectors (Originality.ai). Without measuring it, we're optimizing blindly. Claude proxy is a black box - perplexity provides concrete metric for unpredictability.

**FR-10: Quality Validation**
- System shall calculate BERTScore (semantic similarity target ≥0.92)
- System shall calculate BLEU score (fluency target ≥0.80)
- System shall verify 100% technical term preservation (no lost or altered terms)
- System shall verify quantitative accuracy (±5% tolerance for numerical values)
- System shall flag quality violations for user review before finalizing

**FR-11: Workflow State Management**
- System shall save checkpoints after each major processing stage (term protection, paraphrasing iteration, validation)
- System shall support resume-from-checkpoint if workflow interrupted
- System shall maintain processing log with timestamps, component outputs, detection scores per iteration
- System shall generate final report: original detection score, final detection score, iterations required, quality metrics, warnings/flags

**FR-12: Failure Handling & Recovery**
- If detection score target (<15% proxy, ~<20% Originality.ai) not achieved after maximum iterations (7), system shall:
  - **Return best attempt:** Export the iteration with lowest detection score achieved
  - **Generate detailed report:** Include detection score progression (all 7 iterations), section-level heatmap (which sections still trigger detection), specific AI patterns identified but not eliminated, problematic sentence examples
  - **Provide manual refinement guidance:** Flag 5-10 most problematic sentences with suggested manual rewrites
- System shall NOT automatically escalate to "nuclear" aggression without user consent (risk of semantic drift)
- System shall allow user to resume processing with manual edits integrated (checkpoint-based resume)
- **Rationale:** User selected "Return Best Attempt + Report" strategy; provides transparency and actionable feedback for manual refinement

**FR-13: Multi-Format Output**
- System shall export humanized paper in markdown format (primary)
- System shall optionally export processing report (JSON or markdown)
- System shall optionally export comparison view (original vs humanized, side-by-side or diff format)

### Non-Functional Requirements

**NFR-1: Performance (Maximize Success Rate Mode)**
- Processing time: **15-30 minutes** per 6,000-8,000 word paper (up to 7 iterations, excluding human injection time)
- Token usage: **200K-350K input tokens, 100K-180K output tokens** per paper (7 iterations)
  - Included in user's Claude Code subscription (no separate charges)
  - System tracks token usage for transparency
- Maximum memory usage: 3 GB RAM during processing (spaCy models + transformers + reference text analysis)
- Support for batch processing: 3-5 papers sequentially without manual intervention (if no human injection required)
- **Rationale:** User selected "Maximize Success Rate" mode, prioritizing 90-95% success rate over speed

**NFR-2: Reliability (Maximize Success Rate Mode)**
- Success rate: **90-95%** of papers achieve <20% AI detection score (actual Originality.ai) within 7 iterations
- Target proxy score: <15% on Claude agent analysis (maps to ~15-25% on Originality.ai with safety margin)
- Fault tolerance: System shall handle processing failures gracefully (retry logic with exponential backoff, checkpoint recovery)
- Data integrity: Zero data loss during processing (checkpoint mechanism after each iteration)
- Term preservation: **95-98% accuracy** (context-aware protection, tiered strategy)
- **Rationale:** User selected "Maximize Success Rate" mode; 7 iterations + aggressive-intensive paraphrasing + all optional features enabled

**NFR-3: Usability**
- Command-line interface with clear progress indicators (current stage, iteration count, detection score)
- Interactive prompts for injection points with clear guidance text
- Configuration via YAML file (API keys, aggression levels, quality thresholds, optional settings)
- Comprehensive error messages with actionable troubleshooting steps

**NFR-4: Maintainability**
- Modular component architecture (8+ independent Python modules)
- Each component with unit tests (80%+ code coverage target)
- Comprehensive inline documentation and docstrings
- Version-controlled glossary and pattern files (easy updates for new terms/patterns)

**NFR-5: Scalability**
- Support for papers up to 20,000 words (extended research articles)
- Glossary expandable to 500+ terms without performance degradation
- Pattern database expandable to 100+ AI fingerprints
- Reference text analysis support for up to 10 reference documents (50,000 words total)

**NFR-6: Security & Privacy**
- API keys stored in environment variables (no hardcoded secrets)
- Input papers processed locally (no cloud storage of sensitive research)
- Optional encryption for checkpoint files (if papers contain sensitive data)
- Compliance with institutional data handling policies

**NFR-7: Compatibility**
- Python 3.9+ runtime environment
- Cross-platform support: Windows, macOS, Linux
- Claude Code integration via Bash tool and stdin/stdout communication
- Dependency management via requirements.txt (reproducible environments)

---

## Technical Assumptions

### Architecture & Technology Stack

**Assumption 1: Orchestrator-Worker Pattern (Claude Code Agent Architecture)**

**Architecture Overview:**
- **Claude agent** (running in Claude Code environment) serves as orchestrator - the user interacts with Claude directly
- Claude orchestrator handles: high-level reasoning, workflow coordination, decision-making, iterative refinement logic, **direct AI inference** (paraphrasing, detection analysis, translation)
- **Python programs serve as tools** (NOT standalone applications) - executed via Bash tool, no SDK imports
- Python workers handle: computational tasks (NLP, ML, text processing, quality validation, state management)
- **Communication pattern:** Claude uses Bash tool → executes Python scripts → receives results via stdout (JSON serialization)
- **Architecture clarification:** Claude agent performs ALL AI tasks directly using its own inference capabilities (no separate API calls). Python tools perform computational work only.

**Architectural Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│                            USER                                 │
│                    (Claude Code Subscription)                   │
│                              ↕                                  │
│                  ┌───────────────────────┐                      │
│                  │  Claude Agent         │                      │
│                  │  (Orchestrator)       │                      │
│                  │                       │                      │
│                  │ - Workflow logic      │                      │
│                  │ - Decision making     │                      │
│                  │ - Direct AI inference │                      │
│                  │   • Paraphrasing      │                      │
│                  │   • Detection analysis│                      │
│                  │   • Translation chain │                      │
│                  │ - Human injection     │                      │
│                  └───────────┬───────────┘                      │
│                              │                                  │
│                     Uses Bash tool to execute                   │
│                              ↓                                  │
│      ┌───────────────────────────────────────────────┐          │
│      │        Python Tool Components (Workers)       │          │
│      │         (NO API calls, stdin/stdout I/O)      │          │
│      ├───────────────────────────────────────────────┤          │
│      │  term_protector.py                            │          │
│      │  paraphraser_processor.py                     │          │
│      │  fingerprint_remover.py                       │          │
│      │  burstiness_enhancer.py                       │          │
│      │  detector_processor.py                        │          │
│      │  perplexity_calculator.py (uses local GPT-2)  │          │
│      │  validator.py (BERTScore, BLEU)               │          │
│      │  reference_analyzer.py                        │          │
│      │  state_manager.py                             │          │
│      └───────────────────────────────────────────────┘          │
│                                                                 │
│  Data Flow: JSON (stdin) → Python tool → JSON (stdout) → Claude│
└─────────────────────────────────────────────────────────────────┘

Key Points:
1. User interacts with Claude agent ONLY (not with Python scripts)
2. Claude agent performs AI tasks directly using inference (NOT via API calls)
3. Python tools are invoked via Bash, receive input via stdin, output via stdout
4. Python tools do NOT import anthropic SDK or call any APIs
5. Python tools remain simple, stateless, computational workers
6. User's Claude Code subscription provides all AI capabilities
```

**Rationale:** Leverages Claude's direct inference for AI tasks (paraphrasing, detection, translation) while delegating compute-intensive tasks to optimized Python code. Python components remain simple, stateless tools with no API dependencies.

**Risk:** Bash execution overhead (~0.5-1 second per call × 20-30 calls per paper = 10-30 seconds overhead). Mitigation: Batch operations where possible.

**Assumption 2: Python Dependencies (Tool Components Only)**
- **spaCy** (v3.7+) with `en_core_web_trf` transformer model for context-aware NER and term protection
- **transformers** (v4.35+) and **bert-score** (v0.3.13+) for semantic similarity validation
- **GPT-2** or similar language model for perplexity calculation (via transformers)
- **NO anthropic SDK** - Python programs are tools that receive input via stdin/args and output via stdout (JSON). No API calls from Python code.
- **NO DeepL API** (user-specified constraint, removed back-translation approach)
- **NO PDF/DOCX libraries** (user-specified constraint, markdown-only input)
- **Rationale:** Mature, well-documented libraries with proven performance in NLP tasks. spaCy's transformer model provides context analysis needed for tiered term protection. Python components remain simple, stateless tools without external API dependencies.
- **Risk:** Total dependency size ~2-3 GB (spaCy models + transformers). Mitigation: Document installation steps, provide Docker container option.

**Assumption 3: Claude Code Subscription & Token Usage**
- User requires active **Claude Code subscription** (no additional API keys needed)
- Claude agent performs AI tasks directly using inference (included in subscription)
- Token usage happens automatically as part of Claude agent's processing
- **Estimated token usage per paper** (7 iterations, "Maximize Success Rate" mode):
  - **Average case (8,000-word paper):**
    - Input: 200K-250K tokens (paper × 7 iterations + detection analysis + quality validation + reference texts)
    - Output: 100K-130K tokens (paraphrased versions + analysis reports)
  - **Complex case (12,000+ words, heavy math/tables/citations):**
    - Input: 250K-350K tokens
    - Output: 130K-180K tokens
- **Rationale:** Claude agent processes papers as part of normal Claude Code usage. Token usage is tracked but covered by user's existing subscription.
- **Note:** Actual costs depend on user's Claude Code pricing tier. System tracks token usage for transparency but doesn't charge separately.

**Assumption 4: Detection Proxy Correlation (REQUIRES VALIDATION)**
- Claude agent's detection analysis achieves estimated 60-75% accuracy correlation with Originality.ai based on general research (Phase 1 findings)
- **IMPORTANT:** Correlation has NOT been validated for:
  - Metallurgy domain specifically (technical jargon may affect detection accuracy)
  - Post-paraphrasing text (correlation may differ for AI-generated vs AI-humanized text)
  - Latest Originality.ai model versions (detection models update frequently)
- Conservative threshold strategy (<15% proxy → ~15-25% Originality.ai) compensates for uncertainty
- **Rationale:** No cost-effective alternative to Originality.ai API (not publicly available). Claude agent's detection analysis provides best available proxy for automated processing.
- **Risk:** Correlation may degrade over time as Originality.ai updates detection models. Mitigation: Periodic recalibration, user provides feedback on actual Originality.ai scores for system learning.
- **Risk:** Initial papers may have inaccurate proxy predictions. Mitigation: User should validate first 5-10 papers on actual Originality.ai to establish baseline correlation for their domain.
- **Enhancement:** System collects user feedback on actual Originality.ai scores to refine proxy calibration over time (machine learning from user data).

### Data & Processing

**Assumption 5: Metallurgy Glossary Completeness (UNDERESTIMATED)**
- **Initial glossary: 100-150 core terms** covering common alloy systems, phase names, crystallographic notation
- **Realistic comprehensive glossary: 300-500 terms** for 95%+ coverage:
  - Alloy designations: 80+ (AISI, SAE, EN, JIS, ISO standards across steel, Al, Ti, Cu, Ni systems)
  - Phase names: 50+ (austenite, martensite, ferrite, pearlite, bainite, etc.)
  - Techniques/equipment: 70+ (SEM, TEM, XRD, DSC, DTA, EBSD, APT + manufacturer names)
  - Properties/characteristics: 50+ (hardness, toughness, ductility, grain size terminology)
  - Chemical elements/compounds: 50+ (including abbreviations and full names)
- Tiered structure: Tier 1 (always protect), Tier 2 (context-dependent), Tier 3 (flexible synonyms)
- **Rationale:** Initial 100-term glossary provides MVP coverage (~80-85% of common terms). User expands as needed for specialized domains.
- **Risk:** Specialized papers (additive manufacturing, nanostructures, corrosion science) may use domain-specific terminology not in base glossary. Mitigation: (1) Version-controlled glossary with domain extensions, (2) System detects potential technical terms (title-case compounds, hyphenated terms) and prompts user to add, (3) User can provide custom glossary via YAML config.

**Assumption 6: Reference Text Availability (Optional Feature)**
- User may provide 0-5 human-written reference texts (markdown format)
- Reference texts should be relevant to target paper topic (e.g., similar materials, same journal style, same research group)
- System extracts statistical patterns: sentence length distribution, transition phrase frequency, voice/tense ratios
- **Rationale:** Style learning from authentic examples enhances humanization beyond generic patterns. Optional feature (system works without reference texts).
- **Risk:** Irrelevant reference texts may degrade output quality (wrong style patterns). Mitigation: System validates reference text similarity to input paper, warns if mismatch detected.

**Assumption 7: Paper Structure (IMRAD)**
- Input papers follow IMRAD structure: Introduction, Methods, Results, Discussion, Conclusion
- System applies section-specific paraphrasing strategies (see FR-5)
- **Rationale:** IMRAD is universal standard for scientific papers in materials science (Phase 3 research)
- **Risk:** Non-IMRAD papers (review articles, short communications) may not parse correctly. Mitigation: System detects section headers automatically, falls back to generic processing if IMRAD not detected.

### Processing & Quality Control

**Assumption 8: Iterative Refinement Convergence (REVISED EXPECTATIONS)**
- **Realistic convergence distribution:**
  - 70-75% of papers: <15% proxy score after 3-5 iterations (easy cases)
  - 20-25% of papers: 15-25% proxy score after 7 iterations (moderate difficulty, may require manual refinement)
  - 5-10% of papers: >25% proxy score after 7 iterations (hard cases, require manual refinement)
- **Overall success rate: 90-95%** achieve <20% Originality.ai detection (not 95-98% as originally claimed)
- Maximum 7 iterations prevents infinite loops and runaway costs
- **Rationale:** Research (Phase 2) showed adversarial paraphrasing achieves 87.88% detection reduction on average, but results have high variance. Diminishing returns effect: first 2-3 iterations provide 80% of improvement, remaining iterations provide marginal gains.
- **Risk:** Hard case papers with characteristics:
  - Heavy technical density (>70% technical terminology) - limited paraphrasing flexibility
  - Highly structured (enumerated lists, step-by-step procedures) - structure itself is AI tell
  - Repetitive phrasing (standard method descriptions) - repetition amplifies patterns
  - Short length (<3,000 words) - limited text to "hide" AI patterns in
- **Mitigation:** (1) System detects hard cases in iteration 1 and warns user, (2) Adaptive aggression level selection, (3) Early termination if no improvement after 3 consecutive iterations, (4) Detailed failure report guides manual refinement.

**Assumption 9: Semantic Similarity Threshold**
- BERTScore ≥0.92 ensures semantic similarity (meaning preservation)
- BLEU ≥0.80 ensures fluency (readability)
- **Rationale:** Industry-standard thresholds for paraphrasing quality. 0.92 BERTScore allows ~8% structural variation while preserving core meaning.
- **Risk:** Highly technical sentences may score lower due to BERT's training data bias toward general English. Mitigation: Domain-specific BERT model consideration for future enhancement (e.g., SciBERT), user can adjust thresholds via config.

**Assumption 10: Human Expertise Availability (REVISED TIME ESTIMATE)**
- User has PhD-level domain expertise to provide meaningful input at 3-5 injection points
- **Realistic time requirement: 30-60 minutes total** (5-15 minutes per injection point, not 10-20 minutes total as originally estimated)
- Time breakdown per injection point:
  - Reading context and guidance prompt: 1-2 minutes
  - Thinking/formulating response: 3-8 minutes
  - Writing authentic insight: 3-5 minutes
  - Optional: Literature lookup/verification: 5-10 minutes (for critique-type injections)
- **Rationale:** Human input dramatically improves authenticity (Phase 4 research). Strategic injection at high-impact locations maximizes benefit. Original time estimate underestimated cognitive load and quality requirements.
- **Risk:** User may lack time or skip injection points entirely. Mitigation: System allows skipping injection points, provides automated fallback for fully unattended processing (expected success rate drops to 85-90%).
- **Risk:** User may not have deep expertise in all paper sections. Mitigation: System allows partial human injection (e.g., provide input for 2 of 5 points, skip others where expertise lacking).
- **Enhancement:** System provides example injection responses extracted from reference texts (if provided) to guide user and reduce cognitive load.

### Environment & Infrastructure

**Assumption 11: Processing Environment**
- Python 3.9+ runtime
- 3 GB RAM minimum (spaCy models + transformers)
- Local processing (no cloud storage of papers for privacy)
- API keys stored in environment variables (no hardcoded secrets)
- **Rationale:** Standard requirements for NLP processing with transformer models. Local processing ensures paper confidentiality.
- **Risk:** Environment setup complexity (spaCy model download, dependency conflicts). Mitigation: Provide comprehensive installation guide, Docker container option for reproducible environment.

**Assumption 12: Error Handling & Fault Tolerance (EXPANDED)**
- **API failures:** Exponential backoff retry (3 attempts max), graceful degradation
- **Checkpoint mechanism:** State saved after each iteration (resume capability), atomic write operations
- **Validation failures:** User notified with actionable error messages and recovery options
- **Additional error scenarios:**
  - **Invalid markdown parsing:** System attempts repair, fallbacks to plain text if malformed, notifies user of formatting issues
  - **Memory exhaustion:** System enforces 25,000-word limit, rejects larger papers with clear error message and guidance (suggestion: process in sections)
  - **Quality validation failures:** If BERTScore <0.92 after 7 iterations, notify user with quality report, allow manual acceptance or rollback to previous iteration
  - **Glossary term conflicts:** System detects ambiguous terms (same word, different contexts) and prompts user to clarify intent
- **Rationale:** Robust error handling critical for 15-30 minute processing time. User should not lose progress due to transient failures. Additional error scenarios identified through critique.
- **Risk:** Checkpoint file corruption. Mitigation: Atomic write operations, checksum validation, backup checkpoints stored in separate directory.

**Assumption 13: Context Window Limitations (NEW)**
- Claude has 200K token context window. Per-paper token budget allocation:
  - Input paper: 10K-25K tokens (8,000-20,000 words)
  - Reference texts (0-5 documents): 0-50K tokens
  - Glossary + AI pattern database: 10K tokens
  - Conversation history (7 iterations): 50K-70K tokens
  - Processing overhead: 20K tokens
  - **Total: 90K-175K tokens** (within 200K limit, but requires management)
- **Constraint:** Combined paper + reference texts must not exceed 75K tokens (~60,000 words) to leave headroom for processing
- **Rationale:** Context window management critical for long papers or multiple reference texts. Exceeding window would cause processing failure mid-iteration.
- **Risk:** Very long papers (>15,000 words) with multiple reference texts may approach limit. Mitigation: (1) System validates token count before processing, warns if approaching limit, (2) For papers >15,000 words, offer section-by-section processing option, (3) Limit reference texts to 5 documents with combined 50K token max.

**Assumption 14: Reference Text Quality Control (NEW)**
- User-provided reference texts are assumed to be:
  - Authentic human-written content (not AI-generated)
  - Domain-relevant (similar topic, same field)
  - Good quality writing (published papers, well-edited)
  - Non-plagiarized original content
- **Validation requirements:**
  - System analyzes reference texts for AI detection before using (warns if >30% AI-like score)
  - System measures topic similarity between reference texts and input paper using semantic similarity (warns if <40% overlap)
  - System checks reference text quality: average sentence length, vocabulary diversity, coherence (warns if quality metrics below threshold)
- **Rationale:** Low-quality or irrelevant reference texts degrade output quality by introducing inappropriate style patterns. AI-generated reference texts defeat the purpose of style learning.
- **Risk:** User unknowingly provides AI-generated reference texts. Mitigation: Mandatory validation step, clear warning messages, option to proceed without reference texts if validation fails.
- **Risk:** User provides plagiarized content as reference. Mitigation: Disclaimer that user is responsible for ensuring reference texts are appropriately sourced, system does not check plagiarism (user should use Turnitin separately).

**Assumption 15: Regulatory & Ethical Compliance (NEW)**
- **Disclaimer:** User is solely responsible for compliance with:
  - Target journal's AI use policies (disclosure requirements, restrictions)
  - Institutional guidelines on AI-assisted writing
  - Academic integrity standards and honor codes
  - Funding agency policies on AI use in publications
- **System behavior:**
  - Output includes processing metadata (timestamp, iterations, detection scores) for transparency
  - README and documentation include prominent warnings about checking journal policies
  - System does NOT claim to make text "undetectable" (no guarantees)
- **Ethical considerations:**
  - Some journals prohibit AI-generated text entirely
  - Some journals require disclosure: "This manuscript was prepared with AI assistance"
  - Some journals allow AI for editing/paraphrasing but not content generation
  - Plagiarism detection systems (Turnitin, iThenticate) may flag heavily paraphrased text
- **Rationale:** AI humanization for academic publishing raises ethical concerns. System provides transparency tools, but user bears responsibility for appropriate use.
- **Risk:** User submits to journal with strict AI prohibition, faces retraction or sanctions. Mitigation: Prominent warnings in documentation, README checklist: "Have you checked target journal's AI policy?", No warranty or guarantee of detection evasion.

---

## Epic and User Stories

This PRD is organized as **1 Epic** containing **8 User Stories**. For complete epic and story details, see:

📂 **Epic Overview**: [`docs/epic-ai-humanizer.md`](epic-ai-humanizer.md) (EPIC-001)
📂 **User Stories**: [`docs/stories/`](stories/) directory

### Epic-Story Structure

```
EPIC-001: AI Humanizer System (19.5 weeks / 385 hours)
├── STORY-001: Development Environment & Infrastructure Setup (2 weeks / 40h)
├── STORY-002: Metallurgy Glossary & Term Protection System (2 weeks / 45h)
├── STORY-003: Adversarial Paraphrasing Engine (3 weeks / 60h)
├── STORY-004: AI Fingerprint Removal & Burstiness Enhancement (3 weeks / 55h)
├── STORY-005: Reference Text Analysis & Style Learning (2.5 weeks / 50h)
├── STORY-006: Detection Analysis & Quality Validation (2 weeks / 40h)
├── STORY-007: Orchestrator Agent & Workflow Management (3 weeks / 55h)
└── STORY-008: Testing, Documentation & Deployment (2 weeks / 40h)
```

### Quick Reference: User Stories

| Story | Document | Priority | Effort | Dependencies | Key Deliverable |
|-------|----------|----------|--------|--------------|-----------------|
| **STORY-001** | [story-01-environment-setup.md](stories/story-01-environment-setup.md) | Critical | 2 weeks (40h) | None | Working dev environment + Docker |
| **STORY-002** | [story-02-term-protection.md](stories/story-02-term-protection.md) | Critical | 2 weeks (45h) | STORY-001 | 100-150 term glossary + protection system |
| **STORY-003** | [story-03-paraphrasing-engine.md](stories/story-03-paraphrasing-engine.md) | Critical | 3 weeks (60h) | STORY-001, 002 | 5-level paraphrasing + translation chain |
| **STORY-004** | [story-04-burstiness-fingerprints.md](stories/story-04-burstiness-fingerprints.md) | High | 3 weeks (55h) | STORY-001 | 6-dimension structural entropy + patterns |
| **STORY-005** | [story-05-reference-text-analysis.md](stories/story-05-reference-text-analysis.md) | High | 2.5 weeks (50h) | STORY-001, 002 | Style learning from user examples |
| **STORY-006** | [story-06-detection-validation.md](stories/story-06-detection-validation.md) | Critical | 2 weeks (40h) | STORY-001 | Detection analysis + perplexity + BERTScore |
| **STORY-007** | [story-07-orchestrator.md](stories/story-07-orchestrator.md) | Critical | 3 weeks (55h) | STORY-002-006 | Claude Code agent + workflow |
| **STORY-008** | [story-08-testing-docs.md](stories/story-08-testing-docs.md) | High | 2 weeks (40h) | All stories | Production-ready system + guides |

### Epic Summary

**Total Estimated Effort:** 19.5 weeks (385 hours) for complete system

**Critical Path:** STORY-001 → STORY-002 → STORY-003 → STORY-006 → STORY-007 → STORY-008

**Parallel Opportunities:** STORY-004 and STORY-005 can be developed in parallel with STORY-003

**Key Enhancements (from Findings Review):**
- ✅ **Perplexity measurement added** (FR-14, STORY-006): Track text predictability, target 55-75 range
- ✅ **Translation chain added** (FR-5, STORY-003): English→German→Japanese→English for hard cases, +10-15% detection reduction
- ✅ **6-dimension burstiness** (FR-6, STORY-004): Length, structure, beginnings, grammar, clauses, voice - comprehensive structural entropy

**Success Rate Target:** 90-95% of papers achieve <20% AI detection score (Originality.ai)

---

## Critical Findings Review & PRD Enhancements

**Date:** October 28, 2025
**Reviewer:** User provided 3 critical findings from research review
**Impact:** HIGH - All 3 findings identified significant gaps in original PRD

### Finding 1: Missing Perplexity Measurement ✅ RESOLVED

**Issue Identified:**
- PRD mentioned "perplexity reduction" conceptually but included no mechanism to measure it
- FR-9 (AI Detection Analysis) used Claude proxy only (black box)
- Research shows perplexity is the PRIMARY signal used by BERT-based detectors
- "Flying blind" without concrete metric for text unpredictability

**Resolution Implemented:**
- **Added FR-14: Perplexity Measurement**
  - Calculate perplexity using GPT-2 or similar language model
  - Track per-iteration improvement from AI range (20-40) toward human range (55-75)
  - Target: Increase perplexity to 55-75 range (human-like)
  - Section-level analysis to identify low-perplexity sections for targeted refinement
  - Flag papers failing to improve after 3 iterations (hard case indicator)
- **Updated Epic 6 (Detection & Validation):**
  - Added perplexity calculator to scope
  - GPT-2 or similar LM integration
  - 4 new success criteria for perplexity measurement
  - Performance target: <15 seconds per perplexity calculation
- **Rationale:** Provides concrete, measurable optimization target. No longer optimizing blindly for unknown detection signals.

**Impact:** HIGH - Enables data-driven optimization toward specific unpredictability target

---

### Finding 2: No Translation Chain Methodology ✅ RESOLVED

**Issue Identified:**
- Multiple sources cite translation chains as highly effective for breaking detection patterns (87.88% effectiveness)
- PRD completely omitted this technique
- Original rationale: "Removed back-translation to simplify dependencies and reduce costs" (DeepL API removal)
- **Critical error:** Translation chains don't require DeepL API - can use Claude translation prompts

**Resolution Implemented:**
- **Enhanced FR-5: Adversarial Paraphrasing**
  - Added optional translation chain methodology for hard cases (iterations 5-7)
  - Multi-hop translation: English → German → Japanese → English
  - Uses Claude translation prompts (no external API needed)
  - Trigger: If detection improvement <5% after 3 consecutive iterations
  - Cost: ~$0.30-$0.50 additional per paper
  - Expected benefit: 10-15% additional detection reduction for hard cases
  - User control: Optional feature, configurable
- **Updated Epic 3 (Paraphrasing Engine):**
  - Added translation chain to scope
  - 3 new success criteria for translation chain functionality
  - Performance: 4-6 minutes if translation chain used (vs 2-4 minutes normal)
- **Rationale:** Translation through multiple languages introduces linguistic variations that disrupt statistical patterns detectors recognize, while preserving semantic content

**Impact:** MEDIUM-HIGH - Provides proven escalation strategy for hard cases, +10-15% detection reduction potential

---

### Finding 3: Insufficient Burstiness Implementation ✅ RESOLVED

**Issue Identified:**
- Original FR-6 addressed sentence LENGTH variation only
- **Missing 5 critical dimensions of structural variation:**
  1. Sentence structure variation (simple, compound, complex, compound-complex)
  2. Beginning word diversity (avoid 3+ consecutive sentences starting same way)
  3. Grammatical variety (declarative, interrogative, exclamatory mix)
  4. Clause variation (independent/dependent patterns)
  5. Active/passive voice mixing (section-specific ratios)
- Research: Human writing shows high structural ENTROPY; AI shows low entropy even with varied length
- Structural variation is critical detection signal beyond just length

**Resolution Implemented:**
- **Completely Rewrote FR-6: Burstiness Enhancement (EXPANDED - Structural Entropy)**
  - **Dimension 1: Sentence length variation** (original scope, retained)
  - **Dimension 2: Sentence structure variation** (NEW)
    - Mix simple, compound, complex, compound-complex
    - Target distributions per section (60% simple in Methods, 40% compound in Discussion, etc.)
    - Detect and break sequences of 3+ identical structure types
    - spaCy dependency parsing for structure detection
  - **Dimension 3: Beginning word diversity** (NEW)
    - Track sentence-starting patterns (subject-verb, prepositional phrase, subordinate clause, adverb)
    - Force alternation if 3+ consecutive sentences start same way
  - **Dimension 4: Grammatical variety** (NEW)
    - Mix declarative (90-95%), interrogative (1-2 per Discussion), rare exclamatory
    - Avoid excessive consistency (all declarative = AI tell)
  - **Dimension 5: Clause variation** (NEW)
    - Mix independent-only (60%) and independent-dependent (40%)
    - Vary dependent clause position (leading, trailing, embedded)
  - **Dimension 6: Active/passive voice mixing** (NEW)
    - Section-specific targets: 75-85% passive in Methods, 40% passive in Discussion, etc.
    - Avoid 4+ consecutive sentences in same voice
    - spaCy voice detection via dependency parsing
  - Structural entropy measurement (quantify variation across all 6 dimensions)
- **Completely Rewrote Epic 4: AI Fingerprint Removal, Imperfection Injection & Burstiness Enhancement**
  - Renamed to emphasize Structural Entropy focus
  - **Effort increased:** 2 weeks (35h) → 3 weeks (55h) due to expanded scope
  - Added all 6 dimensions to scope with implementation details
  - 7 new success criteria for comprehensive burstiness (one per dimension + entropy measurement)
  - Performance target increased: <5 seconds → <10 seconds (complex analysis)
  - Expected detection reduction increased: 5-10% → 10-15% (comprehensive structural variation)
  - 2 new risks/mitigations: grammatical errors from manipulation, processing time
- **Rationale:** Structural entropy across multiple dimensions is critical for breaking AI detection patterns that identify low-entropy text even when sentence length varies

**Impact:** HIGH - Addresses fundamental gap in burstiness approach, comprehensive structural variation essential for detection evasion

---

### PRD Update Summary

**Total Changes:**
- **1 new Functional Requirement:** FR-14 (Perplexity Measurement)
- **2 Functional Requirements enhanced:** FR-5 (Translation Chain), FR-6 (6-Dimension Burstiness)
- **3 Epics updated:** Epic 3 (translation chain added), Epic 4 (expanded scope + 20h), Epic 6 (perplexity added)
- **Total effort increased:** 18.5 weeks (365h) → 19.5 weeks (385h)
- **Success criteria added:** 14 new checkboxes across 3 epics
- **New components:** Perplexity calculator, Translation chain logic, 5 new burstiness analyzers

**Validation:**
- All 3 findings reviewed and resolved with concrete implementations
- No findings rejected or deferred
- All enhancements aligned with research-backed effectiveness data
- PRD now comprehensive and addresses all major detection signals

**PRD Status:** ✅ COMPLETE (v1.1) - Architecture Clarified - Ready for Implementation

**Architecture Clarification (v1.1):**
- **User request:** "I want to run it in claude cli as an agent that is capable of using the other programs as a tool not with anthropic SDK as an ai program"
- **Resolution:** Explicitly clarified Claude CLI agent architecture in Assumptions 1, 2 and Epic 7
- **Key changes:**
  - Removed anthropic SDK from Python dependencies
  - Added architectural diagram showing Claude CLI orchestrator → Bash tool → Python workers
  - Clarified Python programs are stateless tools (stdin/stdout), NOT SDK-based application
  - Claude orchestrator calls Claude API directly, Python tools perform computational tasks only

**Next Steps:**
1. Implementation can begin with Epic 1 (Environment Setup)
2. Critical path remains: Epic 1 → 2 → 3 → 6 → 7 → 8
3. Epic 4 & 5 can be developed in parallel with Epic 3
4. Estimated delivery: 19.5 weeks from start

**Implementation Note:**
- Epic 7 (Orchestrator) involves creating Claude CLI agent prompt, NOT Python SDK application
- Python components are simple tools: receive JSON via stdin, output JSON via stdout
- No anthropic SDK imports in Python code; all Claude API calls happen at orchestrator level

---

## Changelog

### v1.2 - Epic Structure Reorganization (2025-10-30)

**Summary:** Converted PRD structure from inline epics to standard Agile epic-story hierarchy

**Changes:**
- **Epic restructuring:** Converted 8 inline epics to 1 epic document + 8 user story documents
- **Created documents:**
  - `docs/epic-ai-humanizer.md` (EPIC-001): Main epic overview
  - `docs/stories/story-01-environment-setup.md` (STORY-001)
  - `docs/stories/story-02-term-protection.md` (STORY-002)
  - `docs/stories/story-03-paraphrasing-engine.md` (STORY-003)
  - `docs/stories/story-04-burstiness-fingerprints.md` (STORY-004)
  - `docs/stories/story-05-reference-text-analysis.md` (STORY-005)
  - `docs/stories/story-06-detection-validation.md` (STORY-006)
  - `docs/stories/story-07-orchestrator.md` (STORY-007)
  - `docs/stories/story-08-testing-docs.md` (STORY-008)
- **PRD updates:**
  - Replaced inline epic descriptions with reference section
  - Added epic-story hierarchy tree diagram
  - Updated Quick Reference table with links to story documents
  - Maintained all original content (acceptance criteria, tasks, risks, DoD)

**Rationale:** Standard Agile structure improves organization, enables sprint planning, and provides clearer epic-story relationships

**PRD Status:** ✅ v1.2 COMPLETE - Epic Structure Reorganized - Ready for Sprint Planning

---

