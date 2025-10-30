# User Story 7: Orchestrator Agent & Workflow Management

**Story ID:** STORY-007
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** Critical (Integration)
**Estimated Effort:** 3 weeks (55 hours)
**Dependencies:** STORY-002, STORY-003, STORY-004, STORY-005, STORY-006

---

## User Story

**As a** Claude agent running in Claude Code
**I want** to orchestrate all Python tool components, manage workflow state, and handle human injection points
**So that** the complete humanization workflow executes correctly with iterative refinement

---

## Description

Implement the Claude Code agent orchestrator that coordinates all Python tool components, manages workflow state, handles human injection points, and provides user interaction.

**Architecture:** User interacts with Claude agent directly; Claude uses Bash tool to execute Python programs as workers (not SDK-based Python application).

---

## Acceptance Criteria

### Claude Agent Orchestrator (Prompt/Instructions)

- [ ] User interacts with Claude directly via Claude Code interface
- [ ] Claude agent coordinates entire workflow (component sequencing)
- [ ] Workflow coordination logic: term protection → paraphrasing → fingerprint → detection → validation
- [ ] Iterative refinement loop: max 7 iterations, early termination based on detection scores
- [ ] Claude performs AI tasks via direct inference (paraphrasing, detection analysis, translation)
- [ ] Adaptive aggression level selection based on detection score feedback
- [ ] Human injection point management (identification, prompts, waiting for input)
- [ ] Decision-making (when to escalate, when to terminate, when to trigger translation)
- [ ] Uses Bash tool to execute Python programs, receives JSON via stdout

### Python Tool Wrappers (stdin/stdout interface)

- [ ] All 9 tools follow consistent stdin/stdout JSON pattern
- [ ] term_protector.py: Receives paper text → outputs protected text
- [ ] paraphraser_processor.py: Receives paraphrased text → applies post-processing
- [ ] fingerprint_remover.py: Receives text → outputs cleaned text
- [ ] burstiness_enhancer.py: Receives text → outputs varied text
- [ ] detector_processor.py: Receives detection results → generates heatmap
- [ ] perplexity_calculator.py: Receives text → outputs perplexity scores
- [ ] validator.py: Receives original + humanized → outputs quality metrics
- [ ] All tools: NO API calls, stateless, simple JSON I/O

### State Management (state_manager.py)

- [ ] Checkpoint mechanism saves after each iteration
- [ ] Resume capability restarts from checkpoint
- [ ] Processing log (timestamps, scores, component outputs)
- [ ] Atomic writes prevent corruption
- [ ] Backup checkpoints in separate directory

### Strategic Injection Point Identifier

- [ ] 3-5 injection points identified (Introduction, Results, Discussion ×2, Conclusion)
- [ ] Priority scoring (1-5, highest priority first)
- [ ] Guidance prompt generation (contextual, actionable)
- [ ] User input collection (pause workflow, wait, integrate)
- [ ] Skip option (fully automated fallback)

### User Interaction (CLI)

- [ ] Progress indicators (current stage, iteration count, detection score)
- [ ] Interactive prompts (injection points, error recovery)
- [ ] Configuration loading (YAML config parsing)
- [ ] Token usage and cost tracking
- [ ] Final report generation

### Error Handling

- [ ] Processing failures recovered gracefully
- [ ] Validation failures handled with user guidance
- [ ] Bash execution errors captured and logged
- [ ] Checkpoint recovery on unexpected termination

---

## Tasks

1. **Define Claude Agent Orchestrator Prompts** (15 hours) - Workflow instructions
2. **Implement state_manager.py** (10 hours) - Checkpoint/resume
3. **Build Injection Point Logic** (8 hours) - Identify and prompt
4. **CLI User Interaction** (8 hours) - Progress, prompts, config
5. **Error Handling & Recovery** (8 hours)
6. **Integration Testing** (6 hours) - End-to-end workflow

---

## Risks & Mitigations

**Risk:** Workflow complexity (9 components, 20-30 Bash calls)
**Mitigation:** Modular design, comprehensive error handling, detailed logging

**Risk:** Bash execution overhead (10-30 seconds)
**Mitigation:** Batch operations where possible, JSON optimization

**Risk:** User confusion during human injection
**Mitigation:** Example responses, detailed guidance, skip option

---

## Definition of Done

- [ ] Orchestrator coordinates all 9 components in correct sequence
- [ ] Iterative loop: max 7 iterations, early termination if <2% improvement
- [ ] Adaptive aggression: increases if stagnant for 2 iterations
- [ ] Human injection points: 3-5 identified, guidance clear, skip functional
- [ ] Checkpoint system: saves after each iteration, resume works
- [ ] Error handling: recovers from processing/validation failures
- [ ] CLI: clear progress, user-friendly prompts, comprehensive output
- [ ] Configuration: YAML loading, env variables, customizable thresholds
- [ ] Performance: Total processing 15-30 minutes for 8K word paper
- [ ] Success rate: 90-95% of papers achieve <20% Originality.ai
- [ ] Unit tests: 80%+ coverage for state_manager.py
- [ ] Integration test: Full end-to-end workflow

---

## Related Documents

- PRD: `docs/prd.md` (Epic 7)
- Architecture: `docs/architecture.md` (Section 5.3.1, 5.3.10)
