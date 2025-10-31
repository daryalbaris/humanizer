# Adaptive Aggression Design Document

**Sprint**: Sprint 9
**Feature**: Adaptive Aggression Level Selection
**Author**: BMAD Development Team
**Date**: 2025-10-31
**Status**: Design Phase

---

## 1. Executive Summary

The Adaptive Aggression system automatically selects the optimal paraphrasing aggression level (1-5) based on analyzing input text for AI detection risk factors. This eliminates manual level selection and ensures efficient, cost-effective humanization.

**Goals:**
- Automatically detect AI-generated text patterns
- Calculate risk score (0-100) based on multiple factors
- Select appropriate aggression level based on risk
- Provide transparent justification for selection
- Reduce unnecessary use of expensive high-level paraphrasing

**Success Metrics:**
- Accuracy: >85% correct level selection
- Cost reduction: 30-40% fewer Level 4-5 invocations
- Detection success: Maintain <20% detection rate
- User satisfaction: Reduced need for manual escalation

---

## 2. System Architecture

### 2.1 Component Overview

```
Input Text
    ↓
┌─────────────────────────────────────────┐
│  AdaptiveAggressionAnalyzer             │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Text Analysis Engine           │   │
│  │  - Sentence parsing             │   │
│  │  - Token analysis               │   │
│  │  - Pattern detection            │   │
│  └─────────────────────────────────┘   │
│                ↓                        │
│  ┌─────────────────────────────────┐   │
│  │  Risk Factor Calculators        │   │
│  │  - 8 independent analyzers      │   │
│  │  - Weighted scoring             │   │
│  └─────────────────────────────────┘   │
│                ↓                        │
│  ┌─────────────────────────────────┐   │
│  │  Risk Score Aggregator          │   │
│  │  - Combine factor scores        │   │
│  │  - Apply weights                │   │
│  │  - Normalize to 0-100           │   │
│  └─────────────────────────────────┘   │
│                ↓                        │
│  ┌─────────────────────────────────┐   │
│  │  Level Selector                 │   │
│  │  - Map score → level            │   │
│  │  - Generate justification       │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
    ↓
Output: {level, score, justification, factors}
```

### 2.2 Module Structure

**New File**: `src/tools/adaptive_aggression.py`

```python
class AdaptiveAggressionAnalyzer:
    """Analyzes text and selects optimal aggression level."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize with optional custom factor weights."""
        pass

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return risk assessment.

        Returns:
            {
                'risk_score': 0-100,
                'recommended_level': 1-5,
                'justification': str,
                'factors': {...},
                'confidence': 0.0-1.0
            }
        """
        pass

    # Individual risk factor analyzers (8 methods)
    def _analyze_sentence_uniformity(self, sentences: List[str]) -> float
    def _analyze_vocabulary_diversity(self, tokens: List[str]) -> float
    def _analyze_transition_patterns(self, sentences: List[str]) -> float
    def _analyze_burstiness(self, sentence_lengths: List[int]) -> float
    def _analyze_academic_phrases(self, text: str) -> float
    def _analyze_opening_diversity(self, sentences: List[str]) -> float
    def _analyze_passive_voice(self, sentences: List[str]) -> float
    def _analyze_sentence_complexity(self, sentences: List[str]) -> float
```

---

## 3. Risk Factors & Algorithms

### 3.1 Factor 1: Sentence Structure Uniformity (Weight: 15%)

**Indicator**: AI-generated text often has uniform sentence patterns.

**Algorithm**:
```python
def _analyze_sentence_uniformity(self, sentences: List[str]) -> float:
    """
    Calculate uniformity score based on sentence structure patterns.

    Metrics:
    - Parse tree similarity (if spaCy available)
    - Word count patterns (mean vs median)
    - Punctuation diversity

    Returns: 0.0 (diverse) to 1.0 (uniform)
    """
    # 1. Calculate word count variance
    lengths = [len(s.split()) for s in sentences]
    mean_length = np.mean(lengths)
    std_length = np.std(lengths)

    # Coefficient of variation (CV)
    cv = std_length / mean_length if mean_length > 0 else 0

    # 2. Sentence opening patterns
    openings = [s.split()[0] if s.split() else "" for s in sentences]
    unique_openings = len(set(openings))
    opening_diversity = unique_openings / len(sentences) if sentences else 1.0

    # 3. Combine metrics
    uniformity_score = (1 - cv) * 0.6 + (1 - opening_diversity) * 0.4

    return max(0.0, min(1.0, uniformity_score))
```

**Risk Contribution**: `uniformity_score * 15`

---

### 3.2 Factor 2: Vocabulary Diversity (Weight: 15%)

**Indicator**: AI text often uses limited vocabulary with predictable word choices.

**Algorithm**:
```python
def _analyze_vocabulary_diversity(self, tokens: List[str]) -> float:
    """
    Calculate Type-Token Ratio (TTR) and lexical sophistication.

    Metrics:
    - TTR = unique_words / total_words
    - Hapax legomena ratio (words appearing once)
    - Content word ratio (nouns, verbs, adjectives, adverbs)

    Returns: 0.0 (diverse) to 1.0 (repetitive)
    """
    # 1. Type-Token Ratio
    unique_tokens = len(set(tokens))
    total_tokens = len(tokens)
    ttr = unique_tokens / total_tokens if total_tokens > 0 else 0

    # 2. Hapax legomena (words appearing exactly once)
    word_freq = Counter(tokens)
    hapax_count = sum(1 for count in word_freq.values() if count == 1)
    hapax_ratio = hapax_count / unique_tokens if unique_tokens > 0 else 0

    # 3. Normalize and invert (high diversity = low risk)
    # Expected TTR for academic text: 0.5-0.7
    # Expected hapax ratio: 0.4-0.6
    ttr_risk = 1 - min(ttr / 0.7, 1.0)  # Invert and normalize
    hapax_risk = 1 - min(hapax_ratio / 0.6, 1.0)

    diversity_risk = (ttr_risk * 0.6 + hapax_risk * 0.4)

    return max(0.0, min(1.0, diversity_risk))
```

**Risk Contribution**: `diversity_risk * 15`

---

### 3.3 Factor 3: Transition Word Patterns (Weight: 10%)

**Indicator**: AI overuses formal transitions (however, moreover, furthermore).

**Algorithm**:
```python
def _analyze_transition_patterns(self, sentences: List[str]) -> float:
    """
    Detect overuse of formal transition words.

    Common AI transitions:
    - Additive: furthermore, moreover, additionally
    - Contrastive: however, nevertheless, nonetheless
    - Causal: therefore, thus, consequently
    - Sequential: firstly, secondly, finally

    Returns: 0.0 (natural) to 1.0 (overused)
    """
    formal_transitions = {
        'however', 'moreover', 'furthermore', 'additionally',
        'nevertheless', 'nonetheless', 'therefore', 'thus',
        'consequently', 'firstly', 'secondly', 'thirdly',
        'finally', 'in conclusion', 'to summarize'
    }

    # Count transition occurrences
    text_lower = ' '.join(sentences).lower()
    transition_count = sum(text_lower.count(trans) for trans in formal_transitions)

    # Expected rate: 1-2 per 10 sentences in natural academic writing
    sentence_count = len(sentences)
    expected_rate = sentence_count / 10 * 1.5

    if transition_count <= expected_rate:
        overuse_score = 0.0
    else:
        # Excess transitions (above expected)
        excess = transition_count - expected_rate
        overuse_score = min(excess / expected_rate, 1.0)

    return overuse_score
```

**Risk Contribution**: `overuse_score * 10`

---

### 3.4 Factor 4: Burstiness (Sentence Length Variance) (Weight: 20%)

**Indicator**: AI produces uniform sentence lengths; humans vary significantly.

**Algorithm**:
```python
def _analyze_burstiness(self, sentence_lengths: List[int]) -> float:
    """
    Calculate burstiness score based on sentence length variance.

    Human writing: High variance (10-50 words)
    AI writing: Low variance (15-25 words clustered)

    Returns: 0.0 (high burstiness) to 1.0 (low burstiness = AI-like)
    """
    if len(sentence_lengths) < 3:
        return 0.0  # Insufficient data

    mean_length = np.mean(sentence_lengths)
    std_length = np.std(sentence_lengths)

    # Coefficient of Variation (CV)
    cv = std_length / mean_length if mean_length > 0 else 0

    # Human academic writing CV: 0.4-0.6
    # AI writing CV: 0.1-0.3
    if cv >= 0.4:
        burstiness_risk = 0.0  # Human-like variance
    elif cv <= 0.15:
        burstiness_risk = 1.0  # AI-like uniformity
    else:
        # Linear interpolation between 0.15 and 0.4
        burstiness_risk = (0.4 - cv) / (0.4 - 0.15)

    return max(0.0, min(1.0, burstiness_risk))
```

**Risk Contribution**: `burstiness_risk * 20`

---

### 3.5 Factor 5: Academic Phrase Frequency (Weight: 10%)

**Indicator**: AI overuses formulaic academic phrases.

**Algorithm**:
```python
def _analyze_academic_phrases(self, text: str) -> float:
    """
    Detect formulaic academic phrases common in AI-generated text.

    Examples:
    - "it is important to note that"
    - "it can be seen that"
    - "this study aims to"
    - "in the context of"
    - "with respect to"

    Returns: 0.0 (natural) to 1.0 (formulaic)
    """
    formulaic_phrases = [
        'it is important to note that',
        'it is worth noting that',
        'it can be seen that',
        'it should be noted that',
        'this study aims to',
        'the purpose of this study',
        'in the context of',
        'with respect to',
        'in terms of',
        'as a result of',
        'due to the fact that',
        'in order to',
        'it has been found that',
        'it has been shown that',
        'research has shown that'
    ]

    text_lower = text.lower()
    phrase_count = sum(text_lower.count(phrase) for phrase in formulaic_phrases)

    # Expected rate: 0-2 per 1000 words in natural writing
    word_count = len(text.split())
    expected_rate = (word_count / 1000) * 1.0

    if phrase_count <= expected_rate:
        formulaic_score = 0.0
    else:
        excess = phrase_count - expected_rate
        formulaic_score = min(excess / max(expected_rate, 1), 1.0)

    return formulaic_score
```

**Risk Contribution**: `formulaic_score * 10`

---

### 3.6 Factor 6: Sentence Opening Diversity (Weight: 15%)

**Indicator**: AI often starts sentences with the same words (The, This, It).

**Algorithm**:
```python
def _analyze_opening_diversity(self, sentences: List[str]) -> float:
    """
    Analyze how varied sentence openings are.

    AI tendency: Starts many sentences with:
    - The (40%+)
    - This/These (20%+)
    - It/They (15%+)

    Returns: 0.0 (diverse) to 1.0 (repetitive)
    """
    if len(sentences) < 5:
        return 0.0

    # Extract first word of each sentence (lowercase)
    openings = []
    for sent in sentences:
        words = sent.strip().split()
        if words:
            openings.append(words[0].lower())

    # Calculate frequency distribution
    opening_freq = Counter(openings)
    total_openings = len(openings)

    # Check for overuse of common AI patterns
    the_ratio = opening_freq.get('the', 0) / total_openings
    this_these_ratio = (opening_freq.get('this', 0) + opening_freq.get('these', 0)) / total_openings
    it_they_ratio = (opening_freq.get('it', 0) + opening_freq.get('they', 0)) / total_openings

    # Calculate diversity score (Simpson's Diversity Index)
    diversity_index = 1 - sum((count / total_openings) ** 2 for count in opening_freq.values())

    # Risk factors
    pattern_risk = (the_ratio > 0.3) * 0.3 + (this_these_ratio > 0.2) * 0.2 + (it_they_ratio > 0.15) * 0.15
    diversity_risk = 1 - diversity_index

    opening_risk = (pattern_risk * 0.6 + diversity_risk * 0.4)

    return max(0.0, min(1.0, opening_risk))
```

**Risk Contribution**: `opening_risk * 15`

---

### 3.7 Factor 7: Passive Voice Ratio (Weight: 10%)

**Indicator**: AI tends to overuse passive voice in academic writing.

**Algorithm**:
```python
def _analyze_passive_voice(self, sentences: List[str]) -> float:
    """
    Detect excessive passive voice constructions.

    Passive markers:
    - "was/were [past participle]"
    - "is/are being [past participle]"
    - "has/have been [past participle]"

    Natural academic: 20-40% passive
    AI academic: 50-70% passive

    Returns: 0.0 (balanced) to 1.0 (excessive passive)
    """
    passive_count = 0
    total_sentences = len(sentences)

    # Simple passive detection patterns
    passive_patterns = [
        r'\b(is|are|was|were)\s+\w+ed\b',
        r'\b(is|are|was|were)\s+being\s+\w+ed\b',
        r'\b(has|have|had)\s+been\s+\w+ed\b'
    ]

    for sent in sentences:
        sent_lower = sent.lower()
        for pattern in passive_patterns:
            if re.search(pattern, sent_lower):
                passive_count += 1
                break  # Count once per sentence

    passive_ratio = passive_count / total_sentences if total_sentences > 0 else 0

    # Expected range: 0.2-0.4 (20-40%)
    if passive_ratio <= 0.4:
        passive_risk = 0.0
    elif passive_ratio >= 0.65:
        passive_risk = 1.0
    else:
        # Linear interpolation
        passive_risk = (passive_ratio - 0.4) / (0.65 - 0.4)

    return max(0.0, min(1.0, passive_risk))
```

**Risk Contribution**: `passive_risk * 10`

---

### 3.8 Factor 8: Sentence Complexity Balance (Weight: 5%)

**Indicator**: AI tends toward either all-simple or all-complex sentences.

**Algorithm**:
```python
def _analyze_sentence_complexity(self, sentences: List[str]) -> float:
    """
    Analyze balance between simple, compound, and complex sentences.

    Simple: <15 words, 0-1 commas
    Compound: 15-30 words, 2-3 commas
    Complex: >30 words, 4+ commas

    Ideal balance: 40% simple, 40% compound, 20% complex
    AI imbalance: >60% in any single category

    Returns: 0.0 (balanced) to 1.0 (imbalanced)
    """
    simple_count = 0
    compound_count = 0
    complex_count = 0

    for sent in sentences:
        word_count = len(sent.split())
        comma_count = sent.count(',')

        if word_count < 15 and comma_count <= 1:
            simple_count += 1
        elif word_count < 30 and comma_count <= 3:
            compound_count += 1
        else:
            complex_count += 1

    total = len(sentences)
    if total == 0:
        return 0.0

    simple_ratio = simple_count / total
    compound_ratio = compound_count / total
    complex_ratio = complex_count / total

    # Check for imbalance (any category >60%)
    max_ratio = max(simple_ratio, compound_ratio, complex_ratio)

    if max_ratio <= 0.5:
        complexity_risk = 0.0  # Well-balanced
    elif max_ratio >= 0.75:
        complexity_risk = 1.0  # Severely imbalanced
    else:
        # Linear interpolation
        complexity_risk = (max_ratio - 0.5) / (0.75 - 0.5)

    return max(0.0, min(1.0, complexity_risk))
```

**Risk Contribution**: `complexity_risk * 5`

---

## 4. Risk Score Aggregation

### 4.1 Weighted Sum Formula

```python
def calculate_risk_score(self, factors: Dict[str, float]) -> float:
    """
    Aggregate individual factor scores into overall risk score.

    Args:
        factors: Dict of factor_name -> score (0.0-1.0)

    Returns:
        risk_score: 0-100
    """
    weights = {
        'sentence_uniformity': 15,
        'vocabulary_diversity': 15,
        'transition_patterns': 10,
        'burstiness': 20,
        'academic_phrases': 10,
        'opening_diversity': 15,
        'passive_voice': 10,
        'sentence_complexity': 5
    }

    # Weighted sum
    weighted_score = sum(
        factors[factor] * weight
        for factor, weight in weights.items()
    )

    # Normalize to 0-100
    risk_score = weighted_score  # Already weighted to sum to 100

    return max(0, min(100, risk_score))
```

### 4.2 Confidence Calculation

```python
def calculate_confidence(self, text: str, factors: Dict[str, float]) -> float:
    """
    Calculate confidence in the risk assessment.

    Factors affecting confidence:
    - Text length (longer = more confident)
    - Factor agreement (similar scores = more confident)
    - Extreme values (very high/low = more confident)

    Returns: 0.0-1.0 (confidence level)
    """
    word_count = len(text.split())

    # 1. Length-based confidence
    if word_count < 200:
        length_confidence = 0.5
    elif word_count < 500:
        length_confidence = 0.7
    elif word_count < 1000:
        length_confidence = 0.85
    else:
        length_confidence = 1.0

    # 2. Factor agreement (low standard deviation = high agreement)
    factor_values = list(factors.values())
    factor_std = np.std(factor_values)
    agreement_confidence = 1 - min(factor_std, 1.0)

    # 3. Extremity (clear signal = high confidence)
    mean_factor = np.mean(factor_values)
    if mean_factor < 0.2 or mean_factor > 0.8:
        extremity_confidence = 1.0
    else:
        extremity_confidence = 0.7

    # Combine confidences
    overall_confidence = (
        length_confidence * 0.4 +
        agreement_confidence * 0.3 +
        extremity_confidence * 0.3
    )

    return max(0.0, min(1.0, overall_confidence))
```

---

## 5. Level Selection Logic

### 5.1 Risk Score to Level Mapping

```python
def select_aggression_level(self, risk_score: float) -> int:
    """
    Map risk score to aggression level.

    Thresholds:
    - 0-20:   Level 1 (Gentle)
    - 21-40:  Level 2 (Moderate)
    - 41-60:  Level 3 (Aggressive)
    - 61-80:  Level 4 (Intensive)
    - 81-100: Level 5 (Nuclear)

    Returns: 1-5
    """
    if risk_score <= 20:
        return 1
    elif risk_score <= 40:
        return 2
    elif risk_score <= 60:
        return 3
    elif risk_score <= 80:
        return 4
    else:
        return 5
```

### 5.2 Justification Generation

```python
def generate_justification(
    self,
    risk_score: float,
    level: int,
    factors: Dict[str, float],
    confidence: float
) -> str:
    """
    Generate human-readable justification for level selection.

    Returns: Multi-line explanation string
    """
    # Identify top 3 risk factors
    sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
    top_factors = sorted_factors[:3]

    justification = f"""
Adaptive Aggression Analysis:

Risk Score: {risk_score:.1f}/100 ({_risk_category(risk_score)})
Recommended Level: {level} ({_level_name(level)})
Confidence: {confidence:.1%}

Top Risk Factors:
"""

    for factor, score in top_factors:
        factor_name = _format_factor_name(factor)
        risk_level = _risk_level_description(score)
        justification += f"  • {factor_name}: {score:.2f} ({risk_level})\n"

    justification += f"\nRationale: {_generate_rationale(risk_score, top_factors)}"

    return justification
```

---

## 6. API Design

### 6.1 Main Interface

```python
# Example usage
analyzer = AdaptiveAggressionAnalyzer()

result = analyzer.analyze_text(text)

# Output:
{
    'risk_score': 67.5,
    'recommended_level': 4,
    'justification': "Risk Score: 67.5/100 (High Risk)...",
    'factors': {
        'sentence_uniformity': 0.72,
        'vocabulary_diversity': 0.45,
        'transition_patterns': 0.68,
        'burstiness': 0.85,
        'academic_phrases': 0.34,
        'opening_diversity': 0.71,
        'passive_voice': 0.62,
        'sentence_complexity': 0.29
    },
    'confidence': 0.87,
    'metadata': {
        'word_count': 1523,
        'sentence_count': 42,
        'analysis_time_ms': 156
    }
}
```

### 6.2 CLI Integration

```bash
# Automatic mode (uses adaptive aggression)
bmad humanize input.txt --adaptive

# Output shows analysis:
Analyzing text for AI detection patterns...

Risk Score: 67.5/100 (High Risk)
Recommended Level: 4 (Intensive)
Confidence: 87%

Top Risk Factors:
  • Sentence Length Variance (Burstiness): 0.85 (Very High)
  • Sentence Structure Uniformity: 0.72 (High)
  • Sentence Opening Diversity: 0.71 (High)

Proceeding with Level 4 (Intensive) paraphrasing...
```

### 6.3 Override Option

```bash
# User can override adaptive selection
bmad humanize input.txt --adaptive --override-level 3

# Output:
Adaptive analysis recommends Level 4, but user override to Level 3.
```

---

## 7. Performance Considerations

### 7.1 Computational Complexity

- **Sentence uniformity**: O(n) - single pass through sentences
- **Vocabulary diversity**: O(n) - single pass through tokens
- **Transition patterns**: O(n*m) - n sentences, m transitions to check
- **Burstiness**: O(n) - numpy operations
- **Academic phrases**: O(n*m) - n words, m phrases
- **Opening diversity**: O(n) - single pass
- **Passive voice**: O(n*m) - n sentences, m regex patterns
- **Sentence complexity**: O(n) - single pass

**Overall**: O(n) for reasonable constant factors (m << n)

**Estimated Time**: 50-200ms for 1000-5000 word papers

### 7.2 Memory Usage

- Text storage: O(n) - original text
- Token lists: O(n) - word tokenization
- Factor scores: O(1) - 8 floats
- Counter objects: O(k) - k unique words/patterns

**Peak Memory**: <5 MB for 10,000 word papers

---

## 8. Testing Strategy

### 8.1 Unit Tests (10 tests required)

1. **test_adaptive_aggression_initialization**
   - Verify default weights
   - Custom weight initialization

2. **test_sentence_uniformity_detection**
   - Uniform sentences → high risk
   - Diverse sentences → low risk

3. **test_vocabulary_diversity_calculation**
   - Low TTR → high risk
   - High TTR → low risk

4. **test_transition_pattern_overuse**
   - Excessive transitions → high risk
   - Natural transitions → low risk

5. **test_burstiness_analysis**
   - Uniform lengths → high risk
   - Varied lengths → low risk

6. **test_academic_phrase_detection**
   - Formulaic phrases → high risk
   - Natural phrasing → low risk

7. **test_opening_diversity_check**
   - Repetitive openings → high risk
   - Diverse openings → low risk

8. **test_risk_score_aggregation**
   - Verify weighted sum
   - Normalization to 0-100

9. **test_level_selection_mapping**
   - Verify threshold boundaries
   - Edge cases (0, 100)

10. **test_justification_generation**
    - Non-empty output
    - Includes top factors

### 8.2 Integration Tests

- **test_adaptive_with_known_ai_text**: Known AI samples → Levels 4-5
- **test_adaptive_with_human_text**: Human-written samples → Levels 1-2
- **test_adaptive_end_to_end**: Full pipeline with adaptive selection

---

## 9. Edge Cases & Limitations

### 9.1 Edge Cases

1. **Very short text (<100 words)**
   - Solution: Return default Level 2, low confidence

2. **Non-English text**
   - Solution: Language detection, fallback to Level 2

3. **Heavily technical text**
   - Solution: Adjust weights, higher tolerance for passive voice

4. **Mixed human-AI content**
   - Solution: Flag as "uncertain", recommend Level 3

### 9.2 Known Limitations

1. **No access to actual detection scores**
   - Cannot directly predict Originality.ai/GPTZero scores
   - Risk factors are proxy indicators

2. **Language-dependent features**
   - Designed for English academic text
   - May not generalize to other languages/styles

3. **False positives/negatives**
   - Formal human writing may trigger high risk
   - Casual AI text may appear low risk

4. **No learning mechanism**
   - Static thresholds, no adaptation over time
   - Future: Add ML model trained on detection results

---

## 10. Future Enhancements

### 10.1 Phase 2 Features (Post-Sprint 9)

1. **Machine Learning Model**
   - Train classifier on detection results
   - Improve accuracy to >90%
   - Adaptive threshold learning

2. **Per-Section Analysis**
   - Different risk profiles for Introduction vs Methods
   - Section-specific level recommendations

3. **Detection API Integration**
   - Real-time feedback from Originality.ai
   - Adjust levels based on actual scores

4. **User Feedback Loop**
   - Learn from user overrides
   - Personalized risk profiles

5. **Multi-Language Support**
   - Extend to Spanish, French, German
   - Language-specific risk factors

---

## 11. Implementation Roadmap

### Sprint 9 Tasks

1. ✅ **Design Phase** (Current)
   - Architecture design
   - Algorithm specification
   - API design

2. **Implementation Phase** (Next)
   - Create `src/tools/adaptive_aggression.py`
   - Implement 8 risk factor analyzers
   - Implement scoring and selection logic

3. **Testing Phase**
   - Write 10 unit tests
   - Create test fixtures (AI vs human samples)
   - Verify accuracy with real papers

4. **Documentation Phase**
   - User guide for adaptive mode
   - API reference
   - Algorithm explanation

5. **Integration Phase**
   - Integrate with orchestrator
   - CLI argument support
   - Progress indicator updates

---

## 12. Success Criteria

### 12.1 Functional Requirements

- ✅ Analyze text in <200ms for 1000-word papers
- ✅ Return risk score (0-100) with confidence level
- ✅ Recommend aggression level (1-5)
- ✅ Generate human-readable justification
- ✅ Support CLI integration
- ✅ Handle edge cases gracefully

### 12.2 Quality Requirements

- **Accuracy**: >85% correct level selection on test set
- **Precision**: <10% false high-risk classifications
- **Recall**: >90% detection of high-risk text
- **Confidence calibration**: 80% confidence → 80% accuracy

### 12.3 Performance Requirements

- Analysis time: <200ms for 5000-word papers
- Memory usage: <10 MB per analysis
- Throughput: >100 analyses per second

---

## 13. Appendix

### A. Risk Factor Weight Justification

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Sentence Uniformity | 15% | Strong indicator; AI struggles with natural variation |
| Vocabulary Diversity | 15% | Critical metric; AI has limited lexical range |
| Transition Patterns | 10% | Moderate indicator; AI overuses formal connectives |
| Burstiness | 20% | **Highest weight**; Most reliable AI detector |
| Academic Phrases | 10% | Moderate indicator; formulaic phrasing is common in AI |
| Opening Diversity | 15% | Strong indicator; AI defaults to "The/This/It" |
| Passive Voice | 10% | Moderate indicator; AI tends toward passive in academic |
| Sentence Complexity | 5% | Weak indicator; both AI and humans vary |

**Total**: 100%

### B. References

- Gehrmann et al. (2019). GLTR: Statistical Detection of Generated Text
- Ippolito et al. (2020). Automatic Detection of Generated Text
- Mitchell et al. (2023). DetectGPT: Zero-Shot Machine-Generated Text Detection
- BMAD Documentation: `docs/AGGRESSION_LEVELS_4_5_GUIDE.md`

---

**End of Design Document**

**Next Step**: Implementation of `src/tools/adaptive_aggression.py` based on this design.
