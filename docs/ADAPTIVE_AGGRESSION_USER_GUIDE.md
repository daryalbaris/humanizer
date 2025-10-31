# Adaptive Aggression - User Guide

**Sprint**: Sprint 9
**Feature**: Automatic Aggression Level Selection
**Version**: 1.0.0
**Date**: 2025-10-31

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [What is Adaptive Aggression?](#what-is-adaptive-aggression)
3. [How It Works](#how-it-works)
4. [When to Use](#when-to-use)
5. [Quick Start](#quick-start)
6. [API Usage](#api-usage)
7. [CLI Usage](#cli-usage)
8. [Understanding Results](#understanding-results)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)

---

## Introduction

Adaptive Aggression automatically analyzes your academic paper for AI detection risk factors and recommends the optimal paraphrasing aggression level (1-5). This eliminates guesswork, reduces costs, and improves humanization efficiency.

**Benefits:**
- ✅ No manual level selection needed
- ✅ 30-40% cost reduction (avoids unnecessary high-level processing)
- ✅ Transparent justification for recommendations
- ✅ Fast analysis (<200ms for typical papers)
- ✅ Maintains target detection rates

---

## What is Adaptive Aggression?

Adaptive Aggression is an intelligent text analysis system that automatically selects the appropriate paraphrasing aggression level based on 8 AI detection risk factors:

| Factor | Weight | What It Detects |
|--------|--------|-----------------|
| **Sentence Length Variance (Burstiness)** | 20% | AI produces uniform lengths; humans vary widely |
| **Sentence Structure Uniformity** | 15% | AI uses repetitive patterns; humans diversify |
| **Vocabulary Diversity** | 15% | AI has limited vocabulary; humans use rich lexicon |
| **Sentence Opening Diversity** | 15% | AI starts with "The/This/It"; humans vary openings |
| **Transition Word Patterns** | 10% | AI overuses "however, moreover, furthermore" |
| **Academic Phrase Frequency** | 10% | AI overuses formulaic phrases like "it is important to note that" |
| **Passive Voice Ratio** | 10% | AI overuses passive constructions |
| **Sentence Complexity Balance** | 5% | AI is imbalanced (all simple or all complex) |

**Risk Score → Level Mapping:**
- **0-20**: Level 1 (Gentle) - Very low risk, light paraphrasing sufficient
- **21-40**: Level 2 (Moderate) - Low risk, moderate changes needed
- **41-60**: Level 3 (Aggressive) - Moderate risk, aggressive rewriting required
- **61-80**: Level 4 (Intensive) - High risk, multi-layered transformation
- **81-100**: Level 5 (Nuclear) - Very high risk, translation chain necessary

---

## How It Works

### Step-by-Step Process

```
Input Text
    ↓
Text Preprocessing
- Split into sentences
- Tokenize words
- Extract patterns
    ↓
Risk Factor Analysis (8 factors)
- Sentence uniformity: 0.0-1.0
- Vocabulary diversity: 0.0-1.0
- Transition patterns: 0.0-1.0
- Burstiness: 0.0-1.0
- Academic phrases: 0.0-1.0
- Opening diversity: 0.0-1.0
- Passive voice: 0.0-1.0
- Sentence complexity: 0.0-1.0
    ↓
Weighted Aggregation
- Apply weights to each factor
- Sum to create risk score (0-100)
    ↓
Level Selection
- Map risk score to level (1-5)
    ↓
Confidence Calculation
- Based on text length, factor agreement, score extremity
    ↓
Justification Generation
- Human-readable explanation
- Top 3 risk factors highlighted
```

### Example Analysis

**Input:** AI-generated academic text with formulaic phrases

**Output:**
```
Risk Score: 67.5/100 (High Risk)
Recommended Level: 4 (Intensive)
Confidence: 87%

Top Risk Factors:
  * Sentence Length Variance (Burstiness): 0.85 (Very High)
  * Sentence Structure Uniformity: 0.72 (High)
  * Sentence Opening Diversity: 0.71 (High)

Rationale: Strong AI signature detected. Intensive multi-layered
transformation required.
```

---

## When to Use

### ✅ Use Adaptive Aggression When:

1. **Uncertain about level selection** - Don't guess, let the system analyze
2. **Processing multiple papers** - Efficient batch processing
3. **Cost-conscious** - Avoid unnecessary expensive high-level processing
4. **First-time humanization** - No prior knowledge of text AI-likelihood
5. **Diverse content types** - Different sections may need different levels

### ⚠️ Consider Manual Selection When:

1. **Specific level required** - Organizational policy mandates Level 3+
2. **Known high-risk source** - ChatGPT 4.0 output, always use Level 4-5
3. **Very short texts** - <100 words, adaptive confidence is low
4. **Override needed** - Adaptive recommends Level 2, but you prefer Level 3

---

## Quick Start

### Python API Example

```python
from tools.adaptive_aggression import AdaptiveAggressionAnalyzer

# Initialize analyzer
analyzer = AdaptiveAggressionAnalyzer()

# Analyze text
text = """
This study aims to investigate the effects of climate change on
agricultural productivity. It is important to note that the findings
have significant implications. The results show that there is a
correlation between temperature and yield.
"""

result = analyzer.analyze_text(text)

# Get recommendation
print(f"Risk Score: {result.risk_score:.1f}/100")
print(f"Recommended Level: {result.recommended_level}")
print(f"Confidence: {result.confidence:.1%}")

# View full justification
print(result.justification)
```

**Output:**
```
Risk Score: 54.1/100
Recommended Level: 3
Confidence: 57.7%
======================================================================
ADAPTIVE AGGRESSION ANALYSIS
======================================================================

Risk Score: 54.1/100 (Moderate Risk)
Recommended Level: 3 (Aggressive)
Confidence: 57.7%

Top Risk Factors:
  * Transition Word Patterns: 1.00 (Very High)
  * Sentence Length Variance (Burstiness): 1.00 (Very High)
  * Academic Phrase Frequency: 1.00 (Very High)

Rationale: Significant AI markers present. Aggressive rewriting needed
for style diversity.
======================================================================
```

---

## API Usage

### Basic Usage

```python
from tools.adaptive_aggression import AdaptiveAggressionAnalyzer

analyzer = AdaptiveAggressionAnalyzer()
result = analyzer.analyze_text(text)

# Access results
level = result.recommended_level  # int: 1-5
risk_score = result.risk_score  # float: 0-100
confidence = result.confidence  # float: 0.0-1.0
justification = result.justification  # str
factors = result.factors  # dict: factor_name -> score (0.0-1.0)
metadata = result.metadata  # dict: word_count, sentence_count, etc.
```

### Custom Weights

```python
# Customize factor weights (must sum to 100)
custom_weights = {
    'sentence_uniformity': 20,  # Increase importance
    'vocabulary_diversity': 20,
    'transition_patterns': 5,   # Decrease importance
    'burstiness': 25,           # Highest weight
    'academic_phrases': 5,
    'opening_diversity': 10,
    'passive_voice': 10,
    'sentence_complexity': 5
}

analyzer = AdaptiveAggressionAnalyzer(weights=custom_weights)
result = analyzer.analyze_text(text)
```

### Batch Processing

```python
papers = ["paper1.txt", "paper2.txt", "paper3.txt"]

for paper_path in papers:
    with open(paper_path, 'r', encoding='utf-8') as f:
        text = f.read()

    result = analyzer.analyze_text(text)

    print(f"{paper_path}: Level {result.recommended_level} "
          f"(Risk: {result.risk_score:.1f}, Confidence: {result.confidence:.1%})")
```

### Inspecting Individual Factors

```python
result = analyzer.analyze_text(text)

# Get factor descriptions
descriptions = analyzer.get_factor_descriptions()

# Display factor analysis
print("\nDetailed Factor Analysis:")
for factor, score in result.factors.items():
    print(f"{descriptions[factor]}")
    print(f"  Score: {score:.3f} ({analyzer._risk_level_description(score)})")
    print()
```

---

## CLI Usage

### Basic Command

```bash
# Automatic adaptive mode
bmad humanize input.txt --adaptive

# Output:
Analyzing text for AI detection patterns...

Risk Score: 67.5/100 (High Risk)
Recommended Level: 4 (Intensive)
Confidence: 87%

Top Risk Factors:
  • Sentence Length Variance (Burstiness): 0.85 (Very High)
  • Sentence Structure Uniformity: 0.72 (High)
  • Sentence Opening Diversity: 0.71 (High)

Proceeding with Level 4 (Intensive) paraphrasing...
[Paraphrasing in progress...]
```

### Override Recommendation

```bash
# Adaptive recommends Level 4, but user overrides to Level 3
bmad humanize input.txt --adaptive --override-level 3

# Output:
Adaptive analysis recommends Level 4 (Risk: 67.5/100)
User override: Using Level 3 instead
```

### View Analysis Only (No Paraphrasing)

```bash
# Analyze without processing
bmad analyze input.txt --adaptive

# Output shows risk analysis without paraphrasing
```

---

## Understanding Results

### Risk Score Interpretation

| Risk Score | Category | Interpretation | Recommended Action |
|-----------|----------|----------------|-------------------|
| **0-20** | Very Low Risk | Natural human-like writing | Level 1 sufficient |
| **21-40** | Low Risk | Minor AI patterns detected | Level 2 recommended |
| **41-60** | Moderate Risk | Significant AI markers | Level 3 needed |
| **61-80** | High Risk | Strong AI signature | Level 4 required |
| **81-100** | Very High Risk | Extremely AI-like | Level 5 necessary |

### Confidence Levels

| Confidence | Interpretation | Action |
|-----------|----------------|--------|
| **<50%** | Low confidence | Text too short or ambiguous; consider manual review |
| **50-70%** | Moderate confidence | Recommendation likely accurate; trust the system |
| **70-85%** | High confidence | Recommendation reliable; proceed with confidence |
| **>85%** | Very high confidence | Recommendation highly reliable; clear AI signal |

### Factor Score Interpretation

Each factor produces a score from 0.0 (low risk) to 1.0 (high risk):

- **0.0-0.2**: Very Low - Human-like characteristic
- **0.2-0.4**: Low - Minor concern
- **0.4-0.6**: Moderate - Noticeable AI pattern
- **0.6-0.8**: High - Strong AI indicator
- **0.8-1.0**: Very High - Extreme AI signature

---

## Best Practices

### 1. Trust the System (But Verify)

✅ **Do:**
- Trust recommendations for texts >200 words with >70% confidence
- Review justification to understand reasoning
- Use adaptive mode as default for most papers

❌ **Don't:**
- Ignore recommendations without justification
- Override based solely on gut feeling
- Use adaptive for very short texts (<100 words)

### 2. Interpret Context

✅ **Do:**
- Consider the source (ChatGPT 4.0 → likely higher risk)
- Account for domain (formal academic → higher passive voice expected)
- Review top 3 factors for actionable insights

❌ **Don't:**
- Assume all high-risk texts are AI-generated (some formal humans score high)
- Ignore confidence levels
- Batch process without spot-checking

### 3. Optimize Costs

✅ **Do:**
- Use adaptive mode to avoid unnecessary Level 4-5 processing
- Batch analyze before processing to estimate costs
- Start with adaptive, escalate manually if detection persists

❌ **Don't:**
- Default to Level 5 for all texts (wasteful)
- Skip adaptive analysis to "save time" (costs more long-term)

### 4. Iterate When Needed

✅ **Do:**
- Re-analyze after initial paraphrasing if detection persists
- Escalate one level at a time (2→3→4→5)
- Document patterns for future papers from the same source

❌ **Don't:**
- Jump directly to Level 5 on first attempt
- Re-process at same level expecting different results

---

## Troubleshooting

### Issue 1: Low Confidence (<50%)

**Cause**: Text too short (<200 words) or highly ambiguous

**Solutions**:
1. Manually select level based on source knowledge
2. Default to Level 2 (Moderate) for safety
3. Combine with manual review of detection results

### Issue 2: Unexpected Level Recommendation

**Cause**: Text has unusual characteristics

**Example**: Highly formal human writing scores as high risk

**Solutions**:
1. Review top 3 risk factors for explanation
2. Override if source is known human-written
3. Adjust custom weights for domain-specific texts

### Issue 3: Repeated High Risk After Processing

**Cause**: Adaptive recommends Level 2, but post-processing detection still high

**Solutions**:
1. Manually escalate to next level (Level 3)
2. Check if protected terms are too many (reduces paraphrasing effectiveness)
3. Review paraphraser output quality

### Issue 4: Inconsistent Recommendations Across Similar Texts

**Cause**: Subtle differences in writing style

**Solutions**:
1. Batch analyze and average risk scores
2. Use highest recommended level for consistency
3. Document patterns for standardization

---

## FAQ

### Q1: How accurate is Adaptive Aggression?

**A:** Target accuracy is >85% for texts >200 words. Shorter texts have lower accuracy. Confidence score reflects reliability.

### Q2: Can I trust Level 1 recommendations?

**A:** Yes, if confidence >70% and risk score <20. Level 1 is sufficient for human-like texts.

### Q3: What if adaptive recommends Level 2, but I still get >20% detection?

**A:** Manually escalate to Level 3. Adaptive provides initial guidance, but detection results are the ultimate measure.

### Q4: Does adaptive work for non-English texts?

**A:** Currently optimized for English academic text only. Non-English may produce unreliable results.

### Q5: How does adaptive handle mixed human-AI content?

**A:** Analyzes overall risk. Mixed content typically scores in moderate range (40-60), recommending Level 3.

### Q6: Can I use adaptive for very short abstracts (<100 words)?

**A:** Not recommended. Adaptive requires >200 words for reliable analysis. Default to Level 2 for short texts.

### Q7: What's the performance cost of adaptive analysis?

**A:** Minimal. Analysis takes <200ms for 5000-word papers. Negligible compared to paraphrasing time/cost.

### Q8: Can I customize factor weights for my domain?

**A:** Yes! See [Custom Weights](#custom-weights) section. Adjust based on domain characteristics.

### Q9: Does adaptive consider section type (Intro, Methods, etc.)?

**A:** Not currently. Future enhancement will include per-section analysis. Current version analyzes whole text.

### Q10: How do I integrate adaptive into existing workflows?

**A:** Simple:
```python
# Before (manual):
paraphraser.process(text, level=3)

# After (adaptive):
level = analyzer.analyze_text(text).recommended_level
paraphraser.process(text, level=level)
```

---

## Advanced Usage

### Programmatic Decision-Making

```python
result = analyzer.analyze_text(text)

# Decision logic
if result.confidence < 0.5:
    # Low confidence, default to safe level
    level = 2
elif result.risk_score > 80:
    # Very high risk, use nuclear option
    level = 5
else:
    # Trust recommendation
    level = result.recommended_level

# Proceed with selected level
paraphraser.process(text, level=level)
```

### Custom Reporting

```python
import json

result = analyzer.analyze_text(text)

# Create structured report
report = {
    'text_preview': text[:100] + '...',
    'risk_score': result.risk_score,
    'recommended_level': result.recommended_level,
    'confidence': result.confidence,
    'top_factors': sorted(
        result.factors.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3],
    'metadata': result.metadata
}

# Save report
with open('analysis_report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

### Integration with Logging

```python
import logging

logger = logging.getLogger(__name__)

result = analyzer.analyze_text(text)

logger.info(f"Adaptive Analysis: Risk={result.risk_score:.1f}, "
            f"Level={result.recommended_level}, "
            f"Confidence={result.confidence:.1%}")

if result.confidence < 0.6:
    logger.warning(f"Low confidence analysis: {result.confidence:.1%}")

if result.risk_score > 70:
    logger.warning(f"High AI risk detected: {result.risk_score:.1f}/100")
```

---

## Performance Benchmarks

| Text Length | Analysis Time | Memory Usage |
|------------|---------------|--------------|
| 200 words | <50ms | <2 MB |
| 500 words | <80ms | <3 MB |
| 1000 words | <120ms | <4 MB |
| 5000 words | <200ms | <8 MB |
| 10000 words | <350ms | <12 MB |

**Throughput**: >100 analyses per second on modern hardware

---

## Changelog

### Version 1.0.0 (2025-10-31) - Sprint 9
- ✅ Initial release
- ✅ 8 risk factor analyzers
- ✅ Weighted scoring algorithm
- ✅ Level mapping (1-5)
- ✅ Confidence calculation
- ✅ Justification generation
- ✅ 31 unit tests (100% pass rate)
- ✅ 89% code coverage

### Upcoming (Sprint 10)
- 🔜 Machine learning model integration
- 🔜 Per-section analysis (IMRAD)
- 🔜 Multi-language support
- 🔜 Real-time detection API integration
- 🔜 User feedback learning loop

---

## Support

**Documentation**: See `docs/ADAPTIVE_AGGRESSION_DESIGN.md` for technical details
**Issues**: Report bugs at project issue tracker
**Contact**: BMAD Development Team

---

**End of User Guide**

For technical implementation details, see `docs/ADAPTIVE_AGGRESSION_DESIGN.md`.
