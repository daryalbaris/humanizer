# Quick Reference Guide: AI Paper Humanization
## Condensed Implementation Guide for Metallurgy Domain

---

## ONE-PAGE SUMMARY

### Most Effective Techniques (Ranked by Impact)

| Rank | Technique | Detection Reduction | Time (500w) | Difficulty |
|------|-----------|-------------------|------------|-----------|
| 1 | Adversarial Paraphrasing | 87.88% | 20s | ⭐⭐⭐ |
| 2 | Human Editing (Transitions) | 15-25% | 2min | ⭐ |
| 3 | Fingerprint Removal | 20-30% | 3min | ⭐⭐ |
| 4 | Back-Translation | 45-65% | 2s | ⭐ |
| 5 | Burstiness Enhancement | 20-35% | 3min | ⭐⭐ |
| 6 | Synonym Replacement | 25-40% | 5min | ⭐⭐ |
| 7 | Sentence Restructuring | 20-35% | 5min | ⭐⭐ |

**Best Combination**: Techniques 1 + 2 + 3 = 85-95% total reduction

---

## QUICK START (15 MINUTES)

### Step 1: Back-Translation (2 minutes)
```python
import deepl

translator = deepl.Translator("your-api-key")
text1 = translator.translate_text(ai_text, target_lang="DE")
result = translator.translate_text(text1, source_lang="DE", target_lang="EN")
```

### Step 2: Replace Transition Words (1 minute)
```python
replacements = {
    "however": "but",
    "furthermore": "moreover",
    "therefore": "thus",
    "in conclusion": "in summary"
}

for original, new in replacements.items():
    result = result.replace(original, new, 1)
```

### Step 3: Quick Human Review (10 minutes)
- Read aloud for awkward phrasing
- Vary first sentence of each paragraph (short → long pattern)
- Add 2-3 specific details (equipment model, error bounds, conditions)

### Step 4: Test Detection
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("openai/openai-roberta-large-detector")
model = AutoModelForSequenceClassification.from_pretrained("openai/openai-roberta-large-detector")

inputs = tokenizer(result, return_tensors="pt", truncation=True, max_length=512)
outputs = model(**inputs)
ai_prob = torch.softmax(outputs.logits, dim=1)[0, 1].item()

print(f"AI Detection: {ai_prob:.1%}")  # Target: <15%
```

**Result**: 40-50% detection reduction with 15 minutes work

---

## STEP-BY-STEP IMPLEMENTATION PLAN

### WEEK 1: MVP Setup

**Monday**:
- [ ] Install DeepL API key
- [ ] Setup local RoBERTa detector
- [ ] Create basic test script

**Tuesday-Wednesday**:
- [ ] Implement back-translation function
- [ ] Test on 3 sample papers
- [ ] Measure baseline detection scores

**Thursday-Friday**:
- [ ] Build detection testing loop
- [ ] Create metrics dashboard
- [ ] Document results

### WEEK 2-3: Advanced Techniques

**Week 2**:
- [ ] Implement adversarial paraphrasing (Claude API)
- [ ] Build fingerprint removal system
- [ ] Test iterative refinement

**Week 3**:
- [ ] Add metallurgy glossary protection
- [ ] Implement detail enhancement
- [ ] Quality validation framework

### WEEK 4+: Production Ready

- [ ] Human-in-loop editing interface
- [ ] FastAPI detection backend
- [ ] Final testing & documentation

---

## CRITICAL METALLURGY TERMS (DO NOT PARAPHRASE)

**Must Preserve Exactly:**

```
Crystal Structures: austenite, ferrite, martensite, pearlite, cementite
Phases: bainite, graphite, carbide, precipitate
Steel Types: stainless steel, duplex, super duplex, austenitic, ferritic, martensitic
Properties: tensile strength, yield strength, hardness, ductility, toughness
Treatments: heat treatment, annealing, quenching, tempering, aging, carburizing
Analysis: SEM, TEM, XRD, EBSD, EDX, spectroscopy
Alloys: AISI 304, AISI 316, Al 2024, Ti-6Al-4V
Phenomena: dislocation, segregation, grain growth, precipitation hardening
```

---

## AI FINGERPRINT CHECKLIST

### Replace These Immediately:

```
❌ "However,"        → "But"
❌ "Furthermore,"    → "Moreover" or "Also"
❌ "Therefore,"      → "Thus" or "So"
❌ "In conclusion,"  → "In summary" or "To conclude"
❌ "It is important to note that" → "Notably" or "Importantly"
❌ "was analyzed"    → "we analyzed" or "analysis revealed"
❌ "The fact that"   → "Since" or "Because"
```

### Add These Naturally:

```
✓ "The steel hardened" → "The steel hardened—a notable shift"
✓ "Results showed X"   → "Did results show X? Yes—clearly."
✓ "It is"              → "It's" (selective, 1-2 per page max)
✓ "[Data here]"        → "[Data here] (see Table 1)"
✓ New sentence         → Connect with semicolon: "...data; furthermore, ..."
```

---

## DETECTION SCORE TARGETS

**Detection Score Ranges:**

- **0.85-0.95**: Unmodified AI text (VERY BAD)
- **0.50-0.85**: Basic paraphrasing (BAD)
- **0.25-0.50**: Back-translation + fingerprint removal (FAIR)
- **0.10-0.25**: Adversarial paraphrasing (GOOD)
- **<0.10**: Human-in-loop refined (EXCELLENT)

**Success Target**: <0.15 (equivalent to human-written text)

---

## QUALITY PRESERVATION CHECKLIST

**Before submitting humanized paper, verify:**

- [ ] All metallurgical terms unchanged (austenite, martensite, etc.)
- [ ] All numerical data preserved (temperatures, hardness values, etc.)
- [ ] All citations intact (references to "Smith et al., 2024" etc.)
- [ ] IMRAD structure preserved (Intro → Methods → Results → Discussion)
- [ ] Flesch Reading Ease score 50-70 (academic level)
- [ ] No grammatical errors (<3 per 10,000 words)
- [ ] Semantic similarity >0.92 to original (BERTScore)
- [ ] No obvious content loss or distortion

---

## COMMON MISTAKES & HOW TO AVOID

| Mistake | Why Bad | Solution |
|---------|---------|----------|
| Paraphrasing technical terms | Loses accuracy, discipline-specific meaning | Use protected glossary (Section 5.1 of full report) |
| Changing numerical data | Falsifies results | Never modify: 1000°C, 500 HV, 5% composition, etc. |
| Over-using contractions | Becomes too informal for academic | Max 2-3 contractions per 500 words |
| Varying too much from original | Loses core message | Keep semantic similarity >0.92 |
| Single-pass humanization | Insufficient, leaves AI markers | Use multi-step: translation → paraphrase → fingerprint removal |
| Not testing against detectors | Waste effort on ineffective edits | Test every iteration with RoBERTa or Originality.ai |

---

## RECOMMENDED TOOL STACK

### Tier 1: Bare Minimum (Cost: $5/month)
```
- DeepL API (back-translation): $5-15/month
- spaCy (local NLP): Free
- RoBERTa detector (local): Free
- Python environment: Free
```
**Result**: 40-50% detection reduction, 15min/paper

### Tier 2: Good Balance (Cost: $30-50/month)
```
- DeepL API: $10/month
- Claude API: $20-30/month (for adversarial paraphrasing)
- spaCy + NLTK: Free
- FastAPI (testing backend): Free
```
**Result**: 75-85% detection reduction, 45min/paper

### Tier 3: Production (Cost: $50-100/month)
```
- DeepL API: $15/month
- Claude API: $30/month
- Originality.ai API: $25-50/month (optional, for testing)
- FastAPI + hosting: Free-$20/month
- All local NLP tools: Free
```
**Result**: 85-95% detection reduction, 60min/paper (with human review)

---

## IMPLEMENTATION CODE SNIPPETS

### Quickest Start (Single Function)

```python
def quick_humanize(ai_text):
    """One-function humanization (40% reduction in 30 seconds)"""
    import deepl

    # 1. Back-translate
    translator = deepl.Translator("YOUR_API_KEY")
    to_german = translator.translate_text(ai_text, target_lang="DE")
    back_to_english = translator.translate_text(
        to_german, source_lang="DE", target_lang="EN"
    ).text

    # 2. Fix obvious transitions
    replacements = {
        "however": "but", "furthermore": "moreover",
        "therefore": "thus", "in conclusion": "in summary"
    }
    result = back_to_english
    for old, new in replacements.items():
        result = result.replace(old, new, 1)

    return result

# Usage
humanized = quick_humanize(ai_paper_text)
```

### Test Against RoBERTa (30 seconds)

```python
def test_detection(text):
    """Quick detection test"""
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    tokenizer = AutoTokenizer.from_pretrained("openai/openai-roberta-large-detector")
    model = AutoModelForSequenceClassification.from_pretrained("openai/openai-roberta-large-detector")

    inputs = tokenizer(text[:512], return_tensors="pt")  # Limit to 512 tokens
    with torch.no_grad():
        outputs = model(**inputs)

    ai_score = torch.softmax(outputs.logits, dim=1)[0, 1].item()

    print(f"AI Detection: {ai_score:.1%}")
    print(f"Status: {'✓ SAFE' if ai_score < 0.15 else '✗ RISKY'}")

    return ai_score

# Usage
score = test_detection(humanized_text)
```

### Batch Processing Multiple Papers

```python
import os
import json
from pathlib import Path

def process_papers(input_dir, output_dir):
    """Process all papers in directory"""

    Path(output_dir).mkdir(exist_ok=True)
    results = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            with open(f"{input_dir}/{filename}", 'r') as f:
                ai_text = f.read()

            humanized = quick_humanize(ai_text)
            original_score = test_detection(ai_text)
            final_score = test_detection(humanized)

            # Save humanized version
            with open(f"{output_dir}/{filename}", 'w') as f:
                f.write(humanized)

            results.append({
                "file": filename,
                "original_score": round(original_score, 3),
                "final_score": round(final_score, 3),
                "reduction": round((original_score - final_score) / original_score * 100, 1)
            })

            print(f"✓ {filename}: {original_score:.1%} → {final_score:.1%}")

    # Save summary
    with open(f"{output_dir}/results.json", 'w') as f:
        json.dump(results, f, indent=2)

    return results

# Usage
results = process_papers("./ai_papers", "./humanized_papers")
```

---

## METRICS INTERPRETATION

### What the Numbers Mean

**Detection Score: 0.47** (from RoBERTa detector)
- Interpretation: ~47% chance detector thinks it's AI
- Acceptable: <15% is target
- Action: Need more humanization

**Semantic Similarity: 0.94** (from BERTScore)
- Interpretation: 94% semantically similar to original
- Acceptable: >92% is minimum
- Action: Good, meaning preserved

**Burstiness: 0.38** (sentence length variance)
- Interpretation: Moderate variation in sentence length
- Acceptable: 0.35-0.55 is human-like range
- Action: Acceptable, looks human-written

**Flesch Reading Ease: 62** (readability)
- Interpretation: ~9th grade reading level
- Acceptable: 50-70 for academic papers
- Action: Good, appropriate for college level

---

## WHEN TO USE EACH TECHNIQUE

**Quick Fix (15 min)**
- Back-translation + transition word replacement
- Expected: 40-50% reduction

**Professional Grade (1 hour)**
- Back-translation + adversarial paraphrasing + human review
- Expected: 75-85% reduction

**Maximum Security (2 hours with human review)**
- All techniques + iterative refinement + human editing
- Expected: 85-95% reduction

---

## TROUBLESHOOTING

**Problem**: Detection score still >0.50 after humanization
- Solution 1: Try adversarial paraphrasing instead of just back-translation
- Solution 2: Add 5-10 rhetorical questions, parenthetical asides, contractions
- Solution 3: Increase sentence length variation (check burstiness metric)

**Problem**: Semantic similarity dropped to <0.85 (meaning lost)
- Solution: Only apply paraphrasing to non-critical sections
- Use protected glossary to keep technical content intact
- Manually review and restore any lost technical meaning

**Problem**: Metallurgical terms changed/lost accuracy
- Solution: Add all domain terms to protected glossary
- Never paraphrase technical terms - only surrounding explanatory text
- Verify all critical terms preserved before submission

**Problem**: Readability too high/low (Flesch >80 or <40)
- Solution: Too high (>80) = too simple, add complex sentences
- Too low (<40) = too complex, break up long sentences
- Target: 50-70 for academic metallurgy papers

---

## FINAL CHECKLIST BEFORE SUBMISSION

```
HUMANIZATION COMPLETION CHECKLIST
==================================

Pre-Humanization:
[ ] Original AI detection score: _____ (should be >0.80)
[ ] Paper length: _____ words
[ ] Domain: Metallurgy/Materials Science confirmed

Humanization Process:
[ ] Phase 1 complete (back-translation): ____ score
[ ] Phase 2 complete (fingerprint removal): ____ score
[ ] Phase 3 complete (domain protection): ____ score
[ ] Phase 4 complete (human review): ____ score

Quality Checks:
[ ] Semantic similarity >0.92: _____
[ ] All metallurgical terms preserved: YES / NO
[ ] All numerical data unchanged: YES / NO
[ ] IMRAD structure intact: YES / NO
[ ] Flesch score 50-70: _____
[ ] Grammar errors <3: _____
[ ] Burstiness 0.35-0.55: _____
[ ] Perplexity >75: _____

Final Detection:
[ ] Final AI detection score: _____ (target <0.15)
[ ] Detection reduction: _____ % (target >85%)

Sign-Off:
[ ] Paper ready for submission
[ ] All checks passed
[ ] No quality degradation detected
[ ] Confidence level: HIGH / MEDIUM / LOW
```

---

## ADDITIONAL RESOURCES

**Research Papers**:
- arxiv.org/abs/2506.07001 - Adversarial Paraphrasing
- arxiv.org/abs/2307.03838 - RADAR Detector

**Tools & Libraries**:
- Hugging Face: huggingface.co/models
- DeepL API: developers.deepl.com
- spaCy: spacy.io
- NLTK: nltk.org

**Metallurgy Data Sources**:
- Materials Project: materialsproject.org
- NIST Materials Data: msel.nist.gov
- CALPHAD Database: tdb.rami.edu.pl

---

**For detailed implementation, refer to HUMANIZATION_TECHNIQUES_RESEARCH_REPORT.md**
