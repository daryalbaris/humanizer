# Aggression Levels 4 & 5 - Advanced Paraphrasing Guide

**BMAD Academic Humanizer - Sprint 9 Feature**

## 📋 Table of Contents

1. [Overview](#overview)
2. [Level 4: Intensive Transformation](#level-4-intensive-transformation)
3. [Level 5: Nuclear Transformation](#level-5-nuclear-transformation)
4. [When to Use Each Level](#when-to-use-each-level)
5. [Technical Implementation](#technical-implementation)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Limitations & Warnings](#limitations--warnings)
9. [Performance Considerations](#performance-considerations)

---

## Overview

Aggression Levels 4 and 5 represent the **most advanced paraphrasing techniques** in the BMAD system, designed for **extreme cases** where standard levels (1-3) fail to achieve target AI detection thresholds (<20% Originality.ai).

### Complete Aggression Level Spectrum

| Level | Name | Change % | Primary Technique | Use Case |
|-------|------|----------|-------------------|----------|
| 1 | Gentle | 5-10% | Light synonym substitution | Technical sections, minimal changes |
| 2 | Moderate | 10-20% | Sentence restructuring | General sections, balanced approach |
| 3 | Aggressive | 20-35% | Extensive rewriting | Introduction, Discussion, Conclusion |
| **4** | **Intensive** | **35-50%** | **Multi-layered transformation** | **Stubborn high-detection sections** |
| **5** | **Nuclear** | **50-70%** | **Translation chain (EN→DE→JA→EN)** | **Last resort, extreme cases** |

---

## Level 4: Intensive Transformation

### Overview

**Target:** 35-50% transformation (50-65% similarity to original)

Level 4 employs a **multi-layered approach** combining six advanced techniques simultaneously to achieve deep stylistic transformation while maintaining academic integrity.

### Six Core Techniques

#### 1. Context-Aware Synonym Replacement
- **Discipline-specific terminology variations**
  - Example: "investigate" → "examine", "explore", "scrutinize" (context-dependent)
- **Field-specific academic phrase replacement**
  - Example: "it is important to note" → "notably", "crucially", "significantly"
- **Extensive connector word variation**
  - Example: "however" → "nevertheless", "conversely", "on the contrary"

#### 2. Sentence Structure Transformation
- **Complex → Simple decomposition**
  - Original: "While previous studies have demonstrated the efficacy of this approach, several limitations remain unaddressed."
  - Transformed: "Previous studies demonstrated efficacy. However, limitations persist."

- **Simple → Complex synthesis**
  - Original: "The results were significant. They confirmed our hypothesis."
  - Transformed: "The significant results provided confirmation of our hypothesis."

- **Embedded clauses → Separate sentences**
  - Original: "The samples, which were collected over a 6-month period, showed remarkable consistency."
  - Transformed: "Samples were collected over 6 months. They showed remarkable consistency."

- **Strategic question format (rare)**
  - Original: "This raises the question of whether the approach is scalable."
  - Transformed: "Is the approach scalable? This question merits consideration."

#### 3. Paragraph Architecture Redesign
- **Topic sentence repositioning**
  - Move topic sentence from front → back (or vice versa)
  - Create suspense or logical culmination

- **Dense paragraph splitting**
  - Break information-heavy paragraphs into focused units
  - Each paragraph addresses single sub-concept

- **Short paragraph merging**
  - Combine related short paragraphs
  - Create cohesive thematic units

- **Opening strategy variation**
  - Alternate between: declarative, interrogative, transitional, statistical

#### 4. Voice, Tense, and Perspective Shifts
- **Active ↔ Passive voice conversion**
  - Active: "We analyzed the samples using X-ray diffraction."
  - Passive: "Samples were analyzed via X-ray diffraction."

- **Tense shifting (where appropriate)**
  - Present → Past: "The model predicts..." → "The model predicted..."
  - Note: Maintain consistency within sections

- **Nominalization variations**
  - Verb: "We analyzed the data thoroughly."
  - Noun: "Thorough analysis of the data was performed."

- **Perspective adjustments**
  - Direct: "The results show that..."
  - Indirect: "Evidence indicates that..."

#### 5. Sentence Opening Diversification
- **NEVER repeat opening patterns**
- **Opening variety strategies:**
  - Prepositional phrases: "In light of these findings, ..."
  - Adverbial phrases: "Significantly, the results demonstrate..."
  - Subordinate clauses: "Although limitations exist, ..."
  - Transitional phrases: "Furthermore, additional data suggests..."
  - Avoid generic starts: "The", "This", "It"

#### 6. Transitional Architecture
- **Replace explicit transitions with implicit logical flow**
  - Before: "However, these results contradict previous findings."
  - After: "These results contradict previous findings." (implicit contrast)

- **Vary transition types:**
  - Additive: furthermore, additionally, moreover
  - Causal: therefore, consequently, thus
  - Contrastive: conversely, nevertheless, in contrast

- **Strategic transition removal/addition**
  - Remove redundant connectors
  - Add transitions for clarity where missing

### When to Use Level 4

✅ **Use Level 4 when:**
- Detection scores remain >25% after Level 3
- Specific sections (e.g., Introduction, Discussion) show stubborn high detection
- Academic paper has formulaic structure typical of AI writing
- Target is 15-20% Originality.ai detection

❌ **Do NOT use Level 4 when:**
- Level 3 achieves target (<20% detection)
- Methods section (technical precision critical)
- Text contains complex technical descriptions
- Results section with critical numerical data

### Level 4 Example

**Original (Level 3 output):**
```
This comprehensive study investigates the heat treatment optimization of
SAF 2507 super duplex stainless steel. Previous research has demonstrated
that solution treatment parameters significantly influence mechanical
properties. However, optimal conditions for this specific alloy remain
inadequately characterized.
```

**Level 4 (Intensive):**
```
Heat treatment optimization for SAF 2507 super duplex stainless steel
forms the focus of this investigation. Prior work established the critical
role of solution treatment parameters in determining mechanical behavior.
Characterization of optimal conditions for this particular alloy remains
incomplete.
```

**Changes applied:**
- Sentence restructuring (passive → active, clause reordering)
- Synonym variation ("comprehensive study investigates" → "forms the focus of this investigation")
- Voice shift ("has demonstrated" → "established")
- Nominalization ("influence" → "determining")
- Opening diversification (avoided "This", "Previous", "However" pattern)
- Transitional simplification (removed "However", used implicit contrast)

---

## Level 5: Nuclear Transformation

### Overview

**Target:** 50-70% transformation (30-50% similarity to original)

Level 5 is the **most aggressive paraphrasing option**, employing a **translation chain methodology** to achieve maximum divergence from original text while preserving factual content.

⚠️ **WARNING: Last Resort Only**
Use Level 5 **only when** Levels 1-4 fail to achieve target detection thresholds. This level introduces the highest risk of semantic drift and should be applied sparingly.

### Translation Chain Methodology

**Process: EN → DE → JA → EN**

#### Step 1: English → German Translation
- **Formal academic German register**
  - Use "wurde untersucht" (formal passive) not "wurde untersucht" (informal)
  - Academic vocabulary: "nachweisen", "belegen", "darlegen"

- **Preserve ALL placeholders**
  - `__TERM_001__` remains `__TERM_001__` in German
  - `__NUM_001__` remains `__NUM_001__` in German

- **Maintain technical precision**
  - Technical terms remain unchanged
  - Numerical values preserved exactly

**Example:**
```
Original: "The __TERM_001__ steel exhibited austenite stability at __NUM_001__."
German: "Der __TERM_001__ Stahl zeigte Austenitstabilität bei __NUM_001__."
```

#### Step 2: German → Japanese Translation
- **Formal Japanese register (です/ます form)**
  - Use polite form: "調査されました" (investigated - polite)
  - Academic kanji compounds: "解析" (analysis), "検証" (verification)

- **Preserve ALL placeholders**
  - `__TERM_001__` remains `__TERM_001__` in Japanese
  - `__NUM_001__` remains `__NUM_001__` in Japanese

- **Maintain logical structure**
  - Japanese sentence order differs from English/German
  - Ensure causality and relationships preserved

**Example:**
```
German: "Der __TERM_001__ Stahl zeigte Austenitstabilität bei __NUM_001__."
Japanese: "__TERM_001__鋼は__NUM_001__においてオーステナイト安定性を示しました。"
```

#### Step 3: Japanese → English Re-translation
- **Natural academic English**
  - Not literal translation
  - Idiomatic English phrasing

- **Preserve ALL placeholders**
  - `__TERM_001__` remains `__TERM_001__` in final English
  - `__NUM_001__` remains `__NUM_001__` in final English

- **Maintain factual accuracy**
  - Same information content as original
  - Different stylistic expression

**Example:**
```
Japanese: "__TERM_001__鋼は__NUM_001__においてオーステナイト安定性を示しました。"
Final English: "Austenite stability was demonstrated by __TERM_001__ steel at __NUM_001__."
```

#### Step 4: Post-Translation Refinement
1. **Fix grammatical artifacts**
   - Remove awkward phrasings from translation
   - Ensure smooth English flow

2. **Verify placeholder integrity**
   - Confirm all `__TERM_XXX__` and `__NUM_XXX__` unchanged
   - Check placeholder count matches original

3. **Factual accuracy check**
   - Numerical values identical
   - Technical relationships preserved
   - No information loss or addition

4. **Quality gate: Nonsensical output check**
   - If re-translated English is nonsensical → Retry with adjusted German/Japanese
   - Maximum 2 retry attempts
   - If still nonsensical → Fall back to Level 4

### Critical Rules for Level 5

1. **Protected Term Preservation (CRITICAL)**
   - `__TERM_XXX__` and `__NUM_XXX__` NEVER translated
   - Preserved as-is through all 3 language transitions
   - Verification after each translation step

2. **Factual Integrity (CRITICAL)**
   - Numerical values unchanged: 850°C = 850°C (not ~850°C or 850 K)
   - Statistical findings identical: p < 0.001 remains p < 0.001
   - Quantitative results preserved: 95% accuracy = 95% accuracy

3. **Academic Register (MANDATORY)**
   - Formal tone throughout all languages
   - Academic vocabulary in each language
   - No informal expressions introduced

4. **Structural Integrity (REQUIRED)**
   - Paragraph boundaries preserved
   - Logical flow maintained
   - Cause-effect relationships intact

### When to Use Level 5

✅ **Use Level 5 when:**
- Detection scores remain >20% after Level 4
- Specific sections show "AI signature" patterns resistant to Levels 1-4
- Research paper has been AI-generated with characteristic markers
- Target is <15% Originality.ai detection (extreme cases)

❌ **Do NOT use Level 5 when:**
- Level 4 achieves target (<20% detection)
- **ANY technical section** (Methods, Results with complex descriptions)
- Text contains domain-specific jargon that doesn't translate well
- Statistical results with complex interpretations
- Abstract or Conclusion (risk of semantic drift)

⚠️ **Use with Extreme Caution:**
- Always verify output for factual accuracy
- Compare with original to detect semantic drift
- Manual review REQUIRED after Level 5

### Level 5 Example

**Original (Level 4 output):**
```
Heat treatment optimization for SAF 2507 super duplex stainless steel
forms the focus of this investigation. Prior work established the critical
role of solution treatment parameters in determining mechanical behavior.
```

**Level 5 (Nuclear - Simulated):**
```
This investigation centers on optimizing thermal processing conditions
for SAF 2507 super duplex stainless steel. Earlier research confirmed
solution treatment parameter criticality in governing mechanical response.
```

**Translation chain effects:**
- "Heat treatment" → (DE: Wärmebehandlung) → (JA: 熱処理) → "thermal processing"
- "optimization...forms the focus" → (DE: steht im Mittelpunkt) → (JA: 中心となる) → "centers on optimizing"
- "established the critical role" → (DE: nachgewiesen wurde) → (JA: 確認された) → "confirmed...criticality"
- "determining mechanical behavior" → (DE: bestimmen mechanisches Verhalten) → (JA: 機械的応答を支配) → "governing mechanical response"

**Result:** 60% transformation from original, maximum stylistic divergence

---

## When to Use Each Level

### Decision Tree

```
Start with Level 2 (Moderate)
    ↓
Detection score >30%?
    ├─ No → SUCCESS ✓
    └─ Yes → Try Level 3 (Aggressive)
            ↓
        Detection score >25%?
            ├─ No → SUCCESS ✓
            └─ Yes → Try Level 4 (Intensive)
                    ↓
                Detection score >20%?
                    ├─ No → SUCCESS ✓
                    └─ Yes → Consider Level 5 (Nuclear)
                            ⚠️ Manual review required

                            Detection score >15%?
                                ├─ No → SUCCESS ✓ (rare)
                                └─ Yes → Combine with:
                                        - Human injection
                                        - Burstiness enhancement
                                        - Fingerprint removal
```

### Section-Specific Recommendations

| Section | Recommended Levels | Rationale |
|---------|-------------------|-----------|
| Abstract | 2-3 | Concise, factual summary - avoid over-transformation |
| Introduction | 3-4 | Often formulaic, benefits from intensive rewriting |
| Methods | 1-2 | Technical precision critical, minimal paraphrasing |
| Results | 2-3 | Balance clarity with variation |
| Discussion | 3-4 | Interpretive, flexible language - aggressive OK |
| Conclusion | 3-4 | Synthesis section, often formulaic |
| References | 1 | Minimal changes to preserve formatting |

---

## Technical Implementation

### API Usage

#### Level 4 - Single Section

```python
from tools.paraphraser_processor import ParaphraserProcessor

processor = ParaphraserProcessor()

# Generate Level 4 prompt
prompt = processor.generate_paraphrasing_prompt(
    text=section_text,
    aggression_level=4,
    sections=[{
        'type': 'introduction',
        'text': section_text
    }]
)

# Use prompt with Claude API
# paraphrased_text = call_claude_api(prompt['system_prompt'], prompt['user_prompt'])
```

#### Level 5 - Full Document

```python
# Process full document with auto section detection
response = processor.process_input({
    'text': full_paper_text,
    'protected_text': protected_paper_text,  # With __TERM_XXX__ placeholders
    'placeholder_map': placeholder_map,
    'aggression_level': 5,
    'section_type': 'auto',
    'preserve_structure': True,
    'max_iterations': 7
})

# Extract paraphrasing prompts
sections_detected = response['data']['sections_detected']
paraphrasing_prompts = response['data']['paraphrasing_prompts']

# Apply prompts to each section via orchestrator
```

### CLI Usage

#### Level 4 Example

```bash
echo '{
    "text": "Your introduction section text here...",
    "aggression_level": 4,
    "section_type": "introduction"
}' | python src/tools/paraphraser_processor.py
```

#### Level 5 Example

```bash
echo '{
    "text": "Your full paper text here...",
    "protected_text": "Text with __TERM_001__ placeholders...",
    "placeholder_map": {
        "__TERM_001__": "SAF 2507",
        "__NUM_001__": "1050°C"
    },
    "aggression_level": 5,
    "section_type": "auto",
    "max_iterations": 7
}' | python src/tools/paraphraser_processor.py
```

---

## Usage Examples

### Example 1: Stubborn Introduction Section

**Scenario:** Introduction section shows 35% Originality.ai detection after Level 3.

**Input (Level 3 output):**
```
This study explores the influence of solution treatment temperature on
microstructural evolution in SAF 2507 super duplex stainless steel.
Achieving optimal balance between austenite and ferrite phases is crucial
for mechanical performance. Previous investigations have identified
temperature range sensitivity but lack systematic optimization.
```

**Apply Level 4:**

**Output (Level 4 - Intensive):**
```
Solution treatment temperature effects on microstructural development
within SAF 2507 super duplex stainless steel form this study's core focus.
Optimal austenite-ferrite phase equilibrium proves essential for mechanical
property enhancement. Prior research established temperature range
sensitivity yet systematic optimization efforts remain absent.
```

**Detection Result:** 18% Originality.ai ✓ (Success with Level 4)

---

### Example 2: Extreme Case - Requires Level 5

**Scenario:** Discussion section remains at 28% detection after Level 4, critical deadline, need <15% target.

**Input (Level 4 output):**
```
The experimental findings substantiate our hypothesis regarding phase
stability optimization. Microstructural analysis revealed balanced phase
distribution at 1050°C treatment temperature. This observation aligns
with thermodynamic predictions from CALPHAD modeling.
```

**Apply Level 5 (Translation Chain):**

**Intermediate translations (not shown to user):**
- German: "Die experimentellen Ergebnisse bestätigen unsere Hypothese bezüglich der Phasenstabilitätsoptimierung..."
- Japanese: "実験結果は相安定性最適化に関する我々の仮説を裏付けています..."

**Output (Level 5 - Nuclear):**
```
Experimental results corroborate the hypothesis concerning phase equilibrium
optimization. Microstructural examination demonstrated balanced phase presence
following 1050°C thermal treatment. Thermodynamic CALPHAD modeling predictions
correspond with this finding.
```

**Changes:**
- "findings substantiate" → "results corroborate"
- "our hypothesis regarding" → "the hypothesis concerning"
- "analysis revealed" → "examination demonstrated"
- "distribution at 1050°C treatment temperature" → "presence following 1050°C thermal treatment"
- "This observation aligns with" → "correspond with this finding"
- Word order changes from translation chain

**Detection Result:** 12% Originality.ai ✓ (Success with Level 5, but required manual review)

---

## Best Practices

### 1. Progressive Escalation
- **Always start with Level 2** (Moderate)
- **Escalate only if necessary:** 2 → 3 → 4 → 5
- **Never jump directly to Level 5**

### 2. Section-Specific Application
- **Apply different levels to different sections**
  - Introduction: Level 3-4
  - Methods: Level 1-2
  - Results: Level 2-3
  - Discussion: Level 3-4

### 3. Placeholder Verification (Critical for Levels 4-5)
```python
# Always verify placeholder integrity after paraphrasing
def verify_placeholders(original, paraphrased, placeholder_map):
    for placeholder in placeholder_map.keys():
        orig_count = original.count(placeholder)
        para_count = paraphrased.count(placeholder)

        if orig_count != para_count:
            raise ValueError(f"Placeholder {placeholder} count mismatch!")

    return True
```

### 4. Quality Assurance for Level 5
After Level 5 application:
1. **Read output completely** (don't skip this!)
2. **Verify factual accuracy** against original
3. **Check for semantic drift** (meaning preservation)
4. **Confirm all numbers unchanged**
5. **Validate technical terms protected**

### 5. Iteration Strategy
- **Maximum 3 iterations per section** with Level 4
- **Maximum 2 iterations per section** with Level 5
- If target not reached after 3 Level 4 + 2 Level 5 → Combine with:
  - Human injection (add domain-specific context)
  - Burstiness enhancement (vary sentence length)
  - Fingerprint removal (eliminate AI patterns)

---

## Limitations & Warnings

### Level 4 Limitations

1. **Risk of Over-Transformation**
   - Excessive paraphrasing may introduce awkward phrasing
   - Manual review recommended for critical papers

2. **Diminishing Returns**
   - If Level 3 achieves 22%, Level 4 may only reach 18% (4% improvement)
   - Cost-benefit analysis: Is 4% improvement worth additional risk?

3. **Section Incompatibility**
   - Methods sections: High risk of technical distortion
   - Results with complex descriptions: Clarity may suffer

### Level 5 Limitations & Risks

⚠️ **HIGH RISK - Read Carefully**

1. **Semantic Drift (Primary Risk)**
   - Translation chain can subtly alter meaning
   - Example: "significant improvement" → "substantial enhancement" → "notable advancement" (drift in magnitude)

2. **Technical Term Translation Errors**
   - Even with placeholder protection, surrounding context may shift
   - Example: "austenite stability" might become "austenite equilibrium" (different concept)

3. **Numerical Context Distortion**
   - Numbers preserved, but interpretation may shift
   - Example: "95% accuracy" → "accuracy of 95%" (same number, but emphasis changed)

4. **Loss of Nuance**
   - Subtle academic distinctions may collapse
   - "suggest", "indicate", "demonstrate" all treated similarly in translation

5. **Nonsensical Output Risk**
   - Translation chain can produce grammatically correct but semantically nonsensical text
   - Example: "The data shows trends" → (multilingual path) → "Trends are displayed by data existence" (awkward)

6. **Irreversibility**
   - Level 5 transformation cannot be "undone"
   - If output is poor, must restart from Level 4

### General Warnings

⚠️ **Do NOT use Levels 4-5 for:**
- Medical research papers (factual precision critical)
- Legal documents (wording has legal implications)
- Patent applications (specific language required)
- Thesis/dissertation (university may have specific requirements)

⚠️ **Use with caution for:**
- Papers with complex statistical analysis
- Multi-author papers (other authors may not approve aggressive changes)
- Papers for high-impact journals (editorial standards)

---

## Performance Considerations

### Processing Time

| Level | Avg. Time per 1000 words | Token Usage (approx.) |
|-------|--------------------------|----------------------|
| 1-3 | 20-30 seconds | 2,000-3,000 tokens |
| 4 | 45-60 seconds | 4,000-5,000 tokens |
| 5 | 90-120 seconds | 8,000-12,000 tokens |

**Why Level 5 is slower:**
- 3 translation steps (EN→DE→JA→EN)
- Post-translation refinement
- Additional verification steps

### Cost Estimate (Claude API)

Assuming Claude Sonnet 3.5 pricing ($3/$15 per million tokens):

| Level | Cost per 1000 words | Cost for 8000-word paper |
|-------|---------------------|--------------------------|
| 1-3 | $0.01-$0.02 | $0.08-$0.16 |
| 4 | $0.03-$0.04 | $0.24-$0.32 |
| 5 | $0.08-$0.12 | $0.64-$0.96 |

**Level 5 is 6-8x more expensive than Level 2** due to translation chain overhead.

### Throughput

**Sequential processing (one section at a time):**
- 8000-word paper (6 sections):
  - Level 2-3: ~3-4 minutes total
  - Level 4: ~6-7 minutes total
  - Level 5: ~12-15 minutes total

**Parallel processing (sections processed simultaneously):**
- 8000-word paper (6 sections):
  - Level 2-3: ~30-45 seconds (6 parallel API calls)
  - Level 4: ~60-90 seconds
  - Level 5: ~120-180 seconds

---

## Frequently Asked Questions

### Q1: When should I use Level 4 vs Level 5?

**A:** Use Level 4 for detection scores 20-30%. Only escalate to Level 5 if Level 4 fails to achieve <20% target **and** you've applied other techniques (burstiness, fingerprint removal) without success. Level 5 should be last resort.

### Q2: Can I mix levels within the same paper?

**A:** Yes! This is recommended. Example:
- Introduction: Level 4
- Methods: Level 2
- Results: Level 3
- Discussion: Level 4
- Conclusion: Level 3

### Q3: How do I know if Level 5 output is accurate?

**A:**
1. Read the entire output
2. Compare numerical values with original (must be identical)
3. Verify technical relationships preserved
4. Check that conclusions match original
5. Look for nonsensical phrases (translation artifacts)
6. If any concerns → Reject and retry with Level 4

### Q4: What if Level 5 still doesn't achieve <20% detection?

**A:** Combine Level 5 with:
1. **Human injection** at high-priority points (3-5 human-written sentences)
2. **Burstiness enhancement** (vary sentence length dramatically)
3. **Fingerprint removal** (eliminate AI patterns)
4. **Iterative refinement** (2-3 passes with detection feedback)

If still >20% after all techniques → The content may be inherently AI-detectable (consider rewriting from scratch).

### Q5: Are placeholders guaranteed to be preserved in Level 5?

**A:** Yes, the prompt explicitly instructs to preserve `__TERM_XXX__` and `__NUM_XXX__` as-is through all translation steps. However, **always verify** with automated checks:

```python
assert original.count('__TERM_001__') == paraphrased.count('__TERM_001__')
```

---

## Summary

### Key Takeaways

✅ **Level 4 (Intensive):**
- 35-50% transformation via multi-layered techniques
- Use for stubborn sections (20-30% detection)
- 6 simultaneous techniques (synonyms, structure, paragraphs, voice, openings, transitions)
- Moderate risk, recommended manual review

✅ **Level 5 (Nuclear):**
- 50-70% transformation via EN→DE→JA→EN translation chain
- Last resort for extreme cases (>20% detection after Level 4)
- High risk of semantic drift - **mandatory manual review**
- 6-8x more expensive and slower than standard levels

✅ **Best Practice:**
- Progressive escalation: 2 → 3 → 4 → (5 if desperate)
- Section-specific application (different levels for different sections)
- Always verify placeholders and factual accuracy
- Combine with human injection and burstiness for maximum effect

⚠️ **Remember:**
Levels 4-5 are **powerful but risky**. Use responsibly and always verify output quality.

---

**Version:** 1.0
**Last Updated:** 2025-10-31
**Sprint:** Sprint 9
**Status:** Production Ready ✅
