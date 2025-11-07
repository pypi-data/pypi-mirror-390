# TRAligner Documentation

**TRAligner** (Text Reuse Aligner) is a sophisticated Python package designed for detecting and analyzing text reuse, particularly optimized for Hebrew and other Semitic languages. The package implements advanced sequence alignment algorithms, including the Smith-Waterman algorithm, to identify similarities between suspect and source texts.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Components](#core-components)
6. [API Reference](#api-reference)
7. [Understanding Results](#understanding-results)
8. [Advanced Usage](#advanced-usage)
9. [Examples](#examples)
10. [Dependencies](#dependencies)
11. [Performance Considerations](#performance-considerations)

---

## Overview

TRAligner is particularly powerful for academic research in text reuse detection, plagiarism detection, and comparative textual analysis. It provides multiple matching methods and can handle complex linguistic features including:

- **Hebrew text processing** with support for gematria, abbreviations, and number conversion
- **Multiple alignment algorithms** including Smith-Waterman and custom matching methods
- **Flexible scoring systems** with customizable parameters
- **Comprehensive output formats** including DataFrames and HTML visualizations

---

## Features

### Core Alignment Features
- **Smith-Waterman Algorithm**: Optimal local sequence alignment
- **Multi-method Matching**: Combines multiple matching strategies
- **Gap Handling**: Sophisticated gap penalty systems
- **Internal Word Swapping**: Detects transpositions within alignment spans

### Hebrew Language Support
- **Gematria Matching**: Numerical value-based word comparison
- **Hebrew Number Conversion**: Convert Hebrew text numbers to integers
- **Abbreviation Detection**: Identify and expand Hebrew abbreviations
- **Orthographic Variations**: Handle different spelling conventions
- **Final Letters (Sofiot)**: Manage Hebrew final letter variations

### Advanced Matching Methods
- **Edit Distance**: Levenshtein distance-based similarity
- **Stemming**: Support for multiple languages including Greek
- **Embedding Similarity**: Vector-based word similarity
- **LLM Integration**: Large language model-based comparisons
- **Synonym Detection**: Semantic similarity matching

### Output and Visualization
- **DataFrame Integration**: Pandas-compatible result structures
- **HTML Visualization**: Rich web-based alignment display
- **Scoring Metrics**: Comprehensive alignment quality assessment
- **Alignment Matrices**: Detailed position-based analysis

---

## Installation

### Prerequisites
```bash
pip install numpy pandas python-Levenshtein hebrew-numbers
```

### Package Structure
```
TRAligner/
├── __init__.py
├── text_alignment_clean.py    # Main alignment algorithms
├── alignment_tools.py         # Hebrew analysis tools
└── README.md                  # This documentation
```

### Import
```python
import TRAligner.text_alignment_clean as ta
from TRAligner import alignment_tools
```

---

## Quick Start

### Basic Alignment Example

```python
import TRAligner.text_alignment_clean as ta

# Simple Hebrew text alignment
suspect_tokens = ["בראשית", "ברא", "אלהים"]
source_tokens = ["בראשית", "ברא", "אלוהים"]

alignment_sequences, df_alignment, suspect_matrix, source_matrix = ta.alignment(
    suspect_tokens,
    source_tokens,
    match_score=3,
    mismatch_score=1,
    methods={}
)

# Score the alignment
score, sequences = ta.alignmentScore(alignment_sequences)
print(f"Alignment score: {score}")
```

**The Results:**
```python
# alignment_sequences will look like this:
[[(0, 0, 1, 'exact_match'),
  (1, 1, 1, 'exact_match'),
  (2, 2, 1, 'exact_match')]]
```

The `alignment_sequences` variable is a list of lists, where each inner list represents a local alignment between the two texts. Each local alignment is a list of tuples containing four elements:
- **Position in suspect text** (0-indexed)
- **Position in source text** (0-indexed)  
- **Alignment score** assigned to these tokens
- **Reason for alignment** (matching method used)

---

## Core Components

### 1. Main Alignment Function

**`alignment(suspect_t, src_t, match_score=3, mismatch_score=1, methods={}, gap_score=1, minimum_alignment_size=2)`**

The primary function for performing text alignment between two token sequences.

**Parameters:**
- `suspect_t`: List of tokens from the suspect text
- `src_t`: List of tokens from the source text
- `match_score`: Score for matching tokens (default: 3)
- `mismatch_score`: Penalty for mismatching tokens (default: 1)
- `methods`: Dictionary of matching methods and their parameters
- `gap_score`: Penalty for gaps in alignment (default: 1)
- `minimum_alignment_size`: Minimum length of valid alignments (default: 2)

**Returns:**
- `alignment_sequences`: List of alignment sequences
- `df_alignment`: Pandas DataFrame with detailed alignment information
- `suspect_matrix`: Binary matrix indicating aligned positions in suspect text
- `source_matrix`: Binary matrix indicating aligned positions in source text

### 2. Smith-Waterman Algorithm

**`smith_waterman(suspect_t, src_t, match_score=10, mismatch_score=1, methods={}, swap=False, gap_score=1, minimum_alignment_size=2)`**

Implements the classic Smith-Waterman algorithm for local sequence alignment.

### 3. Word Comparison Engine

**`compare_words(sus_t, src_t, loc_sus, loc_src, methods={})`**

Compares individual words using multiple matching strategies.

**Supported Methods:**
- `exact`: Exact string matching
- `edit_distance`: Levenshtein distance threshold
- `gematria`: Hebrew numerical value matching
- `stemming`: Root word comparison
- `embedding`: Vector similarity
- `orthography`: Spelling variation handling
- `sofiot`: Hebrew final letter normalization

---

## API Reference

### Hebrew Text Processing Functions

#### `hebtext2num(txt)`
Converts Hebrew text numbers to integers.

```python
# Examples
ta.hebtext2num("שלושה")  # Returns: 3
ta.hebtext2num("עשרים")  # Returns: 20
ta.hebtext2num("מאה")    # Returns: 100
```

#### `is_abbreviation(token, get_spliter=False, indicator="'")`
Detects Hebrew abbreviations and optionally splits them.

```python
# Examples
is_abbrev, tokens = ta.is_abbreviation("ר'משה", get_spliter=True)
# Returns: (True, ["ר", "משה"])
```

#### `replace_chars(exchange, replacables, s)`
Replaces characters in a string based on mapping rules.

### Scoring and Analysis Functions

#### `alignmentScore(alignment_sequences, increment2one=0.3, decrement_gap=0.1, verbose=False, prune=0.0)`
Calculates comprehensive scores for alignment sequences.

**Parameters:**
- `increment2one`: Bonus for consecutive alignments
- `decrement_gap`: Penalty for gaps between alignments
- `prune`: Minimum score threshold for inclusion

#### `word_edit_distance(tokens1, tokens2, mode='distance')`
Calculates edit distance between token sequences.

**Modes:**
- `'distance'`: Raw edit distance
- `'ratio'`: Normalized similarity ratio

### Visualization Functions

#### `synopsis_2_html(src_t, df_suspect_alignment)`
Generates HTML visualization of alignments.

```python
suspect_html, source_html = ta.synopsis_2_html(source_tokens, df_alignment)
```

#### `synopsis2htmlTable(text1_t, text2_t, align_sequenses)`
Creates HTML table representation of alignments.

---

## Understanding Results

TRAligner provides multiple output formats that offer different perspectives on the alignment analysis. Understanding these results is crucial for effective text reuse detection and analysis.

### 1. Alignment Sequences

**Structure:** List of alignment sequences, where each sequence contains tuples of matched positions.

```python
alignment_sequences = [
    [(sus_pos1, src_pos1, score1, method1), (sus_pos2, src_pos2, score2, method2), ...],
    [(sus_pos3, src_pos3, score3, method3), ...]
]
```

**Real Example from TRAligner:**
```python
# Simple case:
[[(0, 0, 1, 'exact_match'),
  (1, 1, 1, 'exact_match'),
  (2, 2, 1, 'exact_match')]]

# Complex case with multiple matching methods:
[[(0, 0, 1, 'exact_match'),                    # Perfect match
  (1, 1, 0.8, 'ocr_replacables'),             # OCR correction: כרא → ברא
  (2, 2, 1.0, 'synonym_simple_match'),        # Abbreviation: ה' → אלוהים
  (3, 3, 0.75, 'single_gematria_match'),      # Gematria: ח (8) → שמונה
  (4, 4, 0.828, 'morphology_embeding_match'), # Morphological similarity
  (5, 5, 0.8, 'missing_spaces_match'),        # Missing space handling
  (6, 5, 0.8, 'missing_spaces_match')]]       # Continuation of missing space
```

**Interpretation:**
- Each **sequence** represents a continuous alignment span
- Each **tuple** represents a matched word pair:
  - `sus_pos`: Position in suspect text (0-indexed)
  - `src_pos`: Position in source text (0-indexed)  
  - `score`: Match confidence (0.0-1.0)
  - `method`: Matching method used

**Key Matching Methods:**
- `'exact_match'`: Perfect string match (score = 1.0)
- `'ocr_replacables'`: OCR error correction (score ~0.8)
- `'synonym_simple_match'`: Synonym or abbreviation expansion (score = 1.0)
- `'single_gematria_match'`: Hebrew numerical value match (score ~0.75)
- `'morphology_embeding_match'`: Embedding-based similarity (score variable)
- `'missing_spaces_match'`: Word boundary error correction (score ~0.8)

### 2. Alignment DataFrame

**Structure:** Pandas DataFrame with detailed token-level information.

| Column | Type | Description |
|--------|------|-------------|
| `token` | str | The actual token text |
| `position` | int | Position in the suspect text sequence |
| `match` | float | Match score (0.0 = no match, 1.0 = perfect match) |
| `match_procesure` | str | Method used for matching |
| `suspect_pos` | int | Position in suspect text (-1 if unmatched) |
| `source_pos` | int | Position in source text (-1 if unmatched) |

**Example DataFrame:**
```
    token  position  match match_procesure  suspect_pos  source_pos
0  בראשית         0   1.00           exact            0           0
1     ברא         1   1.00           exact            1           1
2   אלהים         2   1.00           exact            2           2
3      את         3   0.00            none           -1          -1
4   השמים         4   1.00           exact            4           4
5      את         5   0.00            none           -1          -1
6    הארץ         6   1.00           exact            6           6
7   והארץ         7   0.85    edit_distance            7           8
8    היתה         8   0.92        gematria            8          10
```

**Key Insights from DataFrame:**
- **High match scores (0.8-1.0)**: Strong evidence of text reuse
- **Medium scores (0.5-0.8)**: Possible paraphrasing or variations
- **Zero scores**: Unique content or significant modifications
- **Method distribution**: Shows which matching strategies were most effective

### 3. Position Matrices

**Structure:** Binary numpy arrays indicating aligned positions.

```python
suspect_matrix = [1, 1, 1, 0, 1, 0, 1, 1, 1, 0]  # 1 = aligned, 0 = unaligned
source_matrix  = [1, 1, 1, 0, 1, 0, 1, 0, 1, 1]
```

**Interpretation:**
- **Index**: Position in the token sequence
- **Value 1**: Token participates in an alignment
- **Value 0**: Token is unaligned (unique content)

**Usage Examples:**
```python
# Calculate alignment coverage
suspect_coverage = sum(suspect_matrix) / len(suspect_matrix)
source_coverage = sum(source_matrix) / len(source_matrix)

print(f"Suspect text alignment coverage: {suspect_coverage:.2%}")
print(f"Source text alignment coverage: {source_coverage:.2%}")

# Find unaligned regions
unaligned_suspect = [i for i, val in enumerate(suspect_matrix) if val == 0]
unaligned_source = [i for i, val in enumerate(source_matrix) if val == 0]
```

### 4. Scoring Results

**Structure:** Dictionary with detailed scoring information.

```python
max_score, scored_sequences = ta.alignmentScore(alignment_sequences)

# scored_sequences structure:
{
    'sequence_0': {
        'score': 8.75,
        'subsequences': [
            {'start': 0, 'end': 4, 'score': 6.2, 'length': 4},
            {'start': 7, 'end': 9, 'score': 2.55, 'length': 2}
        ],
        'gaps': [{'start': 4, 'end': 7, 'penalty': 0.3}]
    }
}
```

**Score Components:**
- **Base Score**: Sum of individual match scores
- **Consecutive Bonus**: Added for uninterrupted alignments
- **Gap Penalty**: Subtracted for breaks in alignment
- **Length Bonus**: Reward for longer alignment spans

**Interpretation Guidelines:**
- **High scores (>10)**: Strong evidence of direct copying
- **Medium scores (5-10)**: Likely paraphrasing or close similarity  
- **Low scores (1-5)**: Weak similarity or coincidental matches
- **Very low scores (<1)**: Minimal or no meaningful similarity

### 5. HTML Visualization Output

**Structure:** Lists of HTML elements for web display.

```python
suspect_html, source_html = ta.synopsis_2_html(source_tokens, df_alignment)

# Example output:
suspect_html = [
    '<span style="background-color: #90EE90;">בראשית</span>',  # High match
    '<span style="background-color: #FFB6C1;">היתה</span>',   # Medium match
    '<span>והארץ</span>'                                      # No match
]
```

**Color Coding:**
- **Green shades**: Strong matches (score > 0.8)
- **Yellow/Orange**: Medium matches (score 0.5-0.8)
- **Pink/Red**: Weak matches (score 0.3-0.5)
- **No highlighting**: Unmatched text

### 6. Comprehensive Result Analysis

#### Coverage Analysis
```python
def analyze_coverage(suspect_matrix, source_matrix, alignment_sequences):
    # Calculate basic coverage
    suspect_coverage = sum(suspect_matrix) / len(suspect_matrix)
    source_coverage = sum(source_matrix) / len(source_matrix)
    
    # Calculate alignment density
    total_alignments = sum(len(seq) for seq in alignment_sequences)
    avg_alignment_length = total_alignments / len(alignment_sequences) if alignment_sequences else 0
    
    # Find longest continuous alignment
    max_continuous = 0
    current_continuous = 0
    for val in suspect_matrix:
        if val == 1:
            current_continuous += 1
            max_continuous = max(max_continuous, current_continuous)
        else:
            current_continuous = 0
    
    return {
        'suspect_coverage': suspect_coverage,
        'source_coverage': source_coverage,
        'alignment_density': avg_alignment_length,
        'max_continuous_alignment': max_continuous
    }
```

#### Match Quality Distribution
```python
def analyze_match_quality(df_alignment):
    matched_tokens = df_alignment[df_alignment['match'] > 0]
    
    if len(matched_tokens) == 0:
        return "No matches found"
    
    quality_distribution = {
        'perfect_matches': len(matched_tokens[matched_tokens['match'] == 1.0]),
        'strong_matches': len(matched_tokens[matched_tokens['match'] >= 0.8]),
        'medium_matches': len(matched_tokens[(matched_tokens['match'] >= 0.5) & 
                                           (matched_tokens['match'] < 0.8)]),
        'weak_matches': len(matched_tokens[matched_tokens['match'] < 0.5])
    }
    
    return quality_distribution
```

#### Method Effectiveness Analysis
```python
def analyze_methods(df_alignment):
    matched_tokens = df_alignment[df_alignment['match'] > 0]
    method_stats = matched_tokens['match_procesure'].value_counts()
    method_scores = matched_tokens.groupby('match_procesure')['match'].mean()
    
    return {
        'method_frequency': method_stats.to_dict(),
        'method_average_scores': method_scores.to_dict()
    }
```

### 7. Interpretation Guidelines

#### Text Reuse Classification
Based on the combined results, you can classify text reuse as:

**Direct Copying (High Confidence)**
- Coverage > 70%
- Average match score > 0.9
- Multiple perfect matches
- Long continuous alignments

**Close Paraphrasing (Medium-High Confidence)**  
- Coverage 40-70%
- Average match score 0.7-0.9
- Mix of exact and edit-distance matches
- Some gaps but clear structural similarity

**Loose Similarity (Medium Confidence)**
- Coverage 20-40%
- Average match score 0.5-0.7
- Diverse matching methods
- Fragmented alignments

**Minimal Similarity (Low Confidence)**
- Coverage < 20%
- Average match score < 0.5
- Few scattered matches
- May be coincidental

#### Red Flags and Validation
- **Single method dominance**: If only one method produces matches, validate manually
- **Very short alignments**: Multiple 1-2 word matches may be coincidental
- **Extremely high scores**: Verify for potential exact duplicates
- **Inconsistent patterns**: Mixed high/low scores may indicate selective copying

---

## Advanced Usage

### Advanced Matching Methods

```python
# Complex Hebrew text alignment with multiple challenges:
# - Word boundary errors, typographical mistakes
# - Orthographic variations, Gematria differences
# - Use of synonyms and abbreviations

suspect_tokens = ["בראשית", "כרא", "ה'", "ח", "השמים", "ואת", "הארץ"]
source_tokens = ["בראשית", "ברא", "אלוהים", "שמונה", "השמיים", "ואתהארץ"]

# Configure comprehensive matching methods
methods = {
    "ortography": ["י", "ו"],                    # Handle orthographic variations
    "extra_seperators": [""],                    # Handle extra word separators
    "missing_seperators": [""],                  # Handle missing word separators
    "abbreviation": ["'"],                       # Handle Hebrew abbreviations
    "edit_distance": 0.7,                       # Edit distance threshold
    "gematria": True,                           # Hebrew numerical value matching
    "internal_swap": True                        # Allow word transpositions
}

alignment_sequences, df_alignment, suspect_matrix, source_matrix = ta.alignment(
    suspect_tokens,
    source_tokens,
    methods=methods
)
```

**Advanced Results:**
```python
# This complex example produces sophisticated alignments:
[[(0, 0, 1, 'exact_match'),                    # "בראשית" matches exactly
  (1, 1, 0.8, 'ocr_replacables'),             # "כרא" → "ברא" (OCR correction)
  (2, 2, 1.0, 'synonym_simple_match'),        # "ה'" → "אלוהים" (abbreviation expansion)
  (3, 3, 0.75, 'single_gematria_match'),      # "ח" → "שמונה" (gematria: 8)
  (4, 4, 0.828, 'morphology_embeding_match'), # "השמים" → "השמיים" (morphological similarity)
  (5, 5, 0.8, 'missing_spaces_match'),        # "ואת" → "ואתהארץ" (missing space)
  (6, 5, 0.8, 'missing_spaces_match')]]       # "הארץ" → "ואתהארץ" (continuation)
```

### Advanced Scoring

```python
# Perform alignment
alignment_sequences, df_alignment, _, _ = ta.alignment(
    suspect_tokens, source_tokens, methods=methods
)

# Calculate detailed scores
max_score, scored_sequences = ta.alignmentScore(
    alignment_sequences,
    increment2one=0.3,    # Bonus for consecutive matches
    decrement_gap=0.1,    # Gap penalty
    verbose=True,         # Print detailed information
    prune=0.2            # Remove low-scoring sequences
)

print(f"Maximum alignment score: {max_score}")
```

### Hebrew Language Analysis

```python
from TRAligner.alignment_tools import HebAnalysis

# Initialize Hebrew analysis
heb_analyzer = HebAnalysis(
    txt="sample Hebrew text",
    compare_method="base"
)

# Use in alignment
methods = {
    "llm": heb_analyzer,
    "edit_distance": 0.7
}
```

---

## Examples

### Example 1: Basic Hebrew Text Alignment

```python
import TRAligner.text_alignment_clean as ta

# Simple alignment example
suspect_tokens = ["בראשית", "ברא", "אלהים"]
source_tokens = ["בראשית", "ברא", "אלוהים"]

alignment_sequences, df_alignment, suspect_matrix, source_matrix = ta.alignment(
    suspect_tokens, 
    source_tokens, 
    methods={}
)

# Score the alignment
score, sequences = ta.alignmentScore(alignment_sequences)
print(f"Alignment score: {score}")

# Results: 
# [[(0, 0, 1, 'exact_match'),
#   (1, 1, 1, 'exact_match'),
#   (2, 2, 1, 'exact_match')]]
```

### Example 2: Advanced Multi-Method Alignment

```python
# Complex text with multiple Hebrew-specific challenges
suspect_tokens = ["בראשית", "כרא", "ה'", "ח", "השמים", "ואת", "הארץ"]
source_tokens = ["בראשית", "ברא", "אלוהים", "שמונה", "השמיים", "ואתהארץ"]

# Comprehensive method configuration
methods = {
    "ortography": ["י", "ו"],           # Orthographic variations
    "extra_seperators": [""],           # Handle extra separators
    "missing_seperators": [""],         # Handle missing separators
    "abbreviation": ["'"],              # Hebrew abbreviations
    "edit_distance": 0.7,              # Edit distance matching
    "gematria": True,                   # Numerical value matching
    "internal_swap": True               # Word transpositions
}

alignment_sequences, df_alignment, suspect_matrix, source_matrix = ta.alignment(
    suspect_tokens,
    source_tokens,
    methods=methods
)

# Complex results showing different matching methods:
# [[(0, 0, 1, 'exact_match'),
#   (1, 1, 0.8, 'ocr_replacables'),
#   (2, 2, 1.0, 'synonym_simple_match'),
#   (3, 3, 0.75, 'single_gematria_match'),
#   (4, 4, 0.828, 'morphology_embeding_match'),
#   (5, 5, 0.8, 'missing_spaces_match'),
#   (6, 5, 0.8, 'missing_spaces_match')]]
```

### Example 3: Word Embedding Integration

```python
# Using word embeddings for semantic similarity
import fasttext  # or any embedding model

# Initialize embedding model
embedding_model = fasttext.load_model("path/to/fasttext/model.bin")

# Configure methods with embeddings
methods = {
    "morphology-embeding": [(embedding_model, 0.702)],  # Embedding threshold
    "edit_distance": 0.7,
    "gematria": True,
    "orthography": ["י", "ו"]
}

suspect_tokens = ["בראשית", "כרא", "השמים"]
source_tokens = ["בראשית", "ברא", "השמיים"]

alignment_sequences, df_alignment, _, _ = ta.alignment(
    suspect_tokens, source_tokens, methods=methods
)

# Results will include embedding-based matches:
# [[(0, 0, 1, 'exact_match'),
#   (1, 1, 0.8, 'ocr_replacables'),
#   (2, 2, 0.828, 'morphology_embeding_match')]]
```

### Example 4: Hebrew Number and Gematria Processing

```python
# Test Hebrew number conversion
hebrew_numbers = ["אחד", "שנים", "שלושה", "עשרה", "עשרים"]

for heb_num in hebrew_numbers:
    numeric_value = ta.hebtext2num(heb_num)
    print(f"'{heb_num}' = {numeric_value}")

# Test gematria functionality
from hebrew_numbers import gematria_to_int

gematria_examples = ["יג", "כה", "לו"]
for gem in gematria_examples:
    value = gematria_to_int(gem)
    print(f"Gematria '{gem}' = {value}")
```

### Example 4: Hebrew Number and Gematria Processing

```python
# Test Hebrew number conversion
hebrew_numbers = ["אחד", "שנים", "שלושה", "עשרה", "עשרים"]

for heb_num in hebrew_numbers:
    numeric_value = ta.hebtext2num(heb_num)
    print(f"'{heb_num}' = {numeric_value}")

# Test gematria functionality
from hebrew_numbers import gematria_to_int

gematria_examples = ["יג", "כה", "לו"]
for gem in gematria_examples:
    value = gematria_to_int(gem)
    print(f"Gematria '{gem}' = {value}")

# Example of gematria matching in alignment
suspect_tokens = ["ח"]      # Gematria value: 8
source_tokens = ["שמונה"]   # Hebrew word for "eight"

methods = {"gematria": True}
alignment_sequences, _, _, _ = ta.alignment(suspect_tokens, source_tokens, methods=methods)
# Result: [(0, 0, 0.75, 'single_gematria_match')]
```

### Example 5: Abbreviation Detection

```python
# Hebrew abbreviations
abbreviations = ["ר'משה", "ד'ברים", "בעה'ב"]

for abbrev in abbreviations:
    is_abbrev, tokens = ta.is_abbreviation(abbrev, get_spliter=True)
    print(f"'{abbrev}' -> Abbreviation: {is_abbrev}, Tokens: {tokens}")
```

### Example 5: Abbreviation Detection

```python
# Hebrew abbreviations
abbreviations = ["ר'משה", "ד'ברים", "בעה'ב"]

for abbrev in abbreviations:
    is_abbrev, tokens = ta.is_abbreviation(abbrev, get_spliter=True)
    print(f"'{abbrev}' -> Abbreviation: {is_abbrev}, Tokens: {tokens}")

# Example of abbreviation matching in alignment
suspect_tokens = ["ה'"]        # Abbreviation for God
source_tokens = ["אלוהים"]     # Full word for God

methods = {"abbreviation": ["'"]}
alignment_sequences, _, _, _ = ta.alignment(suspect_tokens, source_tokens, methods=methods)
# Result: [(0, 0, 1.0, 'synonym_simple_match')]
```

### Example 6: Complete Result Analysis Pipeline

```python
import TRAligner.text_alignment_clean as ta
import numpy as np
import pandas as pd

# Sample texts for comprehensive analysis
suspect = "בראשית ברא אלהים את השמים ואת הארץ והארץ היתה תהו ובהו"
source = "בראשית ברא אלהים את השמים ואת הארץ והארץ הייתה תהו ובהו וחושך על פני תהום"

suspect_tokens = suspect.split()
source_tokens = source.split()

# Comprehensive method configuration
methods = {
    "edit_distance": 0.7,
    "gematria": True,
    "internal_swap": True,
    "stemming": True,
    "orthography": True
}

# Perform alignment
print("🔍 Performing alignment analysis...")
alignment_sequences, df_alignment, suspect_matrix, source_matrix = ta.alignment(
    suspect_tokens, source_tokens, 
    match_score=4, 
    gap_score=1, 
    methods=methods
)

# 1. Basic Statistics
print(f"\n📊 BASIC ALIGNMENT STATISTICS")
print(f"Alignment sequences found: {len(alignment_sequences)}")
print(f"Total tokens in suspect: {len(suspect_tokens)}")
print(f"Total tokens in source: {len(source_tokens)}")

# 2. Coverage Analysis
suspect_coverage = sum(suspect_matrix) / len(suspect_matrix)
source_coverage = sum(source_matrix) / len(source_matrix)
print(f"\n📈 COVERAGE ANALYSIS")
print(f"Suspect text coverage: {suspect_coverage:.1%} ({sum(suspect_matrix)}/{len(suspect_matrix)} tokens)")
print(f"Source text coverage: {source_coverage:.1%} ({sum(source_matrix)}/{len(source_matrix)} tokens)")

# 3. Match Quality Distribution
if df_alignment is not None and len(df_alignment) > 0:
    matched_tokens = df_alignment[df_alignment['match'] > 0]
    print(f"\n🎯 MATCH QUALITY DISTRIBUTION")
    print(f"Total matched tokens: {len(matched_tokens)}")
    
    if len(matched_tokens) > 0:
        perfect_matches = len(matched_tokens[matched_tokens['match'] == 1.0])
        strong_matches = len(matched_tokens[matched_tokens['match'] >= 0.8])
        medium_matches = len(matched_tokens[(matched_tokens['match'] >= 0.5) & 
                                          (matched_tokens['match'] < 0.8)])
        weak_matches = len(matched_tokens[matched_tokens['match'] < 0.5])
        
        print(f"Perfect matches (1.0): {perfect_matches}")
        print(f"Strong matches (≥0.8): {strong_matches}")
        print(f"Medium matches (0.5-0.8): {medium_matches}")
        print(f"Weak matches (<0.5): {weak_matches}")
        
        avg_score = matched_tokens['match'].mean()
        print(f"Average match score: {avg_score:.3f}")

# 4. Method Effectiveness
if len(matched_tokens) > 0:
    method_stats = matched_tokens['match_procesure'].value_counts()
    method_scores = matched_tokens.groupby('match_procesure')['match'].mean()
    
    print(f"\n🔧 METHOD EFFECTIVENESS")
    for method in method_stats.index:
        count = method_stats[method]
        avg_score = method_scores[method]
        print(f"{method}: {count} matches (avg score: {avg_score:.3f})")

# 5. Alignment Sequence Analysis
print(f"\n🔗 ALIGNMENT SEQUENCE DETAILS")
for i, seq in enumerate(alignment_sequences):
    print(f"\nSequence {i+1}: {len(seq)} token pairs")
    for sus_pos, src_pos, score, method in seq[:3]:  # Show first 3 pairs
        sus_word = suspect_tokens[sus_pos]
        src_word = source_tokens[src_pos]
        print(f"  '{sus_word}' ↔ '{src_word}' (score: {score:.3f}, method: {method})")
    if len(seq) > 3:
        print(f"  ... and {len(seq)-3} more pairs")

# 6. Scoring Analysis
if alignment_sequences:
    max_score, scored_sequences = ta.alignmentScore(
        alignment_sequences, 
        increment2one=0.3, 
        decrement_gap=0.1, 
        verbose=False
    )
    
    print(f"\n🏆 SCORING ANALYSIS")
    print(f"Maximum alignment score: {max_score:.2f}")
    print(f"Number of scored sequences: {len(scored_sequences)}")
    
    for seq_id, seq_data in list(scored_sequences.items())[:2]:  # Show top 2
        print(f"\nSequence {seq_id}:")
        print(f"  Total score: {seq_data['score']:.2f}")
        print(f"  Subsequences: {len(seq_data['subsequences'])}")

# 7. Text Reuse Classification
print(f"\n🎯 TEXT REUSE CLASSIFICATION")
if suspect_coverage >= 0.7 and avg_score >= 0.9:
    classification = "DIRECT COPYING (High Confidence)"
elif suspect_coverage >= 0.4 and avg_score >= 0.7:
    classification = "CLOSE PARAPHRASING (Medium-High Confidence)"
elif suspect_coverage >= 0.2 and avg_score >= 0.5:
    classification = "LOOSE SIMILARITY (Medium Confidence)"
else:
    classification = "MINIMAL SIMILARITY (Low Confidence)"

print(f"Classification: {classification}")

# 8. Detailed Token-by-Token Analysis
print(f"\n📝 DETAILED TOKEN ANALYSIS")
print("Suspect Text with Alignment Status:")
for i, token in enumerate(suspect_tokens):
    status = "✓" if suspect_matrix[i] == 1 else "✗"
    if df_alignment is not None and i < len(df_alignment):
        match_score = df_alignment.iloc[i]['match'] if df_alignment.iloc[i]['match'] > 0 else 0
        print(f"  {status} {i:2d}: '{token}' (score: {match_score:.2f})")
    else:
        print(f"  {status} {i:2d}: '{token}'")

print("\nSource Text with Alignment Status:")
for i, token in enumerate(source_tokens):
    status = "✓" if source_matrix[i] == 1 else "✗"
    print(f"  {status} {i:2d}: '{token}'")

# 9. Generate HTML Visualization
try:
    suspect_html, source_html = ta.synopsis_2_html(source_tokens, df_alignment)
    print(f"\n🎨 HTML VISUALIZATION")
    print("HTML elements generated successfully")
    print(f"Suspect HTML elements: {len(suspect_html)}")
    print(f"Source HTML elements: {len(source_html)}")
    
    # Show sample HTML
    print("\nSample HTML output (first 3 tokens):")
    for i, (sus, src) in enumerate(zip(suspect_html[:3], source_html[:3])):
        print(f"  {i}: Suspect: {sus}")
        print(f"     Source:  {src}")
        
except Exception as e:
    print(f"HTML generation error: {e}")

print(f"\n✅ Analysis complete!")
```

**Expected Output Interpretation:**
- **High coverage + high scores**: Strong evidence of text reuse
- **Method diversity**: Multiple methods confirm matches (more reliable)
- **Continuous alignments**: Better evidence than scattered matches
- **HTML visualization**: Provides intuitive visual confirmation

---

## Dependencies

### Required Packages

```python
# Core dependencies
import numpy as np           # Numerical computations
import pandas as pd          # Data manipulation
import Levenshtein as lev   # Edit distance calculations
import math, re             # Mathematical and regex operations

# Hebrew language support
from hebrew_numbers import gematria_to_int  # Gematria calculations

# Extended functionality
import TRelasticExt as ee   # Elastic search extensions
```

### Optional Dependencies

```python
# For advanced Hebrew analysis
from transformers import AutoModel, AutoTokenizer  # HuggingFace models

# For Greek text processing
from greek_stemmer import GreekStemmer  # Greek language stemming
```

---

## Performance Considerations

### Optimization Tips

1. **Token Preprocessing**: Clean and normalize tokens before alignment
2. **Method Selection**: Choose appropriate matching methods for your use case
3. **Score Thresholds**: Adjust thresholds to balance precision and recall
4. **Sequence Length**: Consider breaking long texts into smaller segments

### Memory Usage

- Large texts may require significant memory for score matrices
- Consider processing in chunks for very long documents
- Use pruning to remove low-scoring alignments

### Speed Optimization

```python
# Fast alignment for large texts
methods = {
    "edit_distance": 0.8,  # Higher threshold = fewer comparisons
    "internal_swap": False,  # Disable for speed
    "gematria": False      # Disable if not needed
}

# Use minimum alignment size to filter short matches
alignment_sequences, _, _, _ = ta.alignment(
    suspect_tokens, source_tokens,
    methods=methods,
    minimum_alignment_size=3  # Only consider alignments of 3+ tokens
)
```

---

## Error Handling

### Common Issues and Solutions

1. **Import Errors**: Ensure all dependencies are installed
```python
try:
    import TRAligner.text_alignment_clean as ta
except ImportError as e:
    print(f"TRAligner import failed: {e}")
```

2. **Hebrew Processing Errors**: Check hebrew_numbers package
```python
try:
    from hebrew_numbers import gematria_to_int
    gematria_available = True
except ImportError:
    gematria_available = False
    print("Hebrew gematria functions not available")
```

3. **Empty Alignment Results**: Adjust matching thresholds
```python
if len(alignment_sequences) == 0:
    print("No alignments found. Try adjusting thresholds:")
    print("- Lower edit_distance threshold")
    print("- Decrease minimum_alignment_size")
    print("- Enable more matching methods")
```

---

## Contributing

TRAligner is designed for research in text reuse detection. For contributions or issues:

1. Ensure compatibility with Hebrew text processing
2. Maintain performance for large-scale analysis
3. Follow the established API patterns
4. Include comprehensive test cases

---

## Citation

If you use TRAligner in your research, please cite our paper:

```bibtex
@article{miller2024text,
  title={Text Alignment in the Service of Text Reuse Detection},
  author={Miller, Hadar and Kuflik, Tsvi and Lavee, Moshe},
  journal={Applied Sciences},
  volume={15},
  number={6},
  pages={3395},
  year={2025},
  publisher={MDPI},
  doi={10.3390/app15063395},
  url={https://www.mdpi.com/2076-3417/15/6/3395}
}
```

Miller, H.; Kuflik, T.; Lavee, M. Text Alignment in the Service of Text Reuse Detection. *Applied Sciences* 2025, 15(6), 3395. [https://doi.org/10.3390/app15063395](https://doi.org/10.3390/app15063395)

---

## License

This package is developed for academic research purposes. Please cite appropriately when using in publications.

---

## Version History

- **Current**: Advanced Hebrew text alignment with multiple matching methods
- **Features**: Smith-Waterman algorithm, gematria support, HTML visualization
- **Optimization**: Performance improvements for large-scale text analysis

---

*For more examples and advanced usage, see the accompanying Jupyter notebook: `TRAligner_test.ipynb`*
