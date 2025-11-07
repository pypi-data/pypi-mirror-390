# TRAligner API Reference

## Function Documentation

### Core Alignment Functions

---

#### `alignment(suspect_t, src_t, match_score=3, mismatch_score=1, methods={}, gap_score=1, minimum_alignment_size=2)`

**Description:** Main function for performing text alignment between two token sequences using the Smith-Waterman algorithm with customizable matching methods.

**Parameters:**
- `suspect_t` (list): List of tokens from the suspect text
- `src_t` (list): List of tokens from the source text  
- `match_score` (int, default=3): Score awarded for matching tokens
- `mismatch_score` (int, default=1): Penalty for mismatching tokens
- `methods` (dict, default={}): Dictionary of matching methods and parameters
- `gap_score` (int, default=1): Penalty for gaps in alignment
- `minimum_alignment_size` (int, default=2): Minimum length of valid alignments

**Returns:**
- `alignment_sequences` (list): List of alignment sequences, each containing tuples of (suspect_pos, source_pos, score, method)
- `df_alignment` (pandas.DataFrame): DataFrame with detailed alignment information
- `suspect_matrix` (numpy.array): Binary matrix indicating aligned positions in suspect text
- `source_matrix` (numpy.array): Binary matrix indicating aligned positions in source text

**Example:**
```python
alignment_sequences, df_alignment, suspect_matrix, source_matrix = ta.alignment(
    ["hello", "world"], 
    ["hello", "beautiful", "world"], 
    methods={"edit_distance": 0.8}
)
```

---

#### `smith_waterman(suspect_t, src_t, match_score=10, mismatch_score=1, methods={}, swap=False, gap_score=1, minimum_alignment_size=2)`

**Description:** Implements the Smith-Waterman algorithm for local sequence alignment.

**Parameters:**
- `suspect_t` (list): Suspect token sequence
- `src_t` (list): Source token sequence
- `match_score` (int, default=10): Match score
- `mismatch_score` (int, default=1): Mismatch penalty
- `methods` (dict, default={}): Matching methods
- `swap` (bool, default=False): Whether sequences were swapped
- `gap_score` (int, default=1): Gap penalty
- `minimum_alignment_size` (int, default=2): Minimum alignment length

**Returns:**
- `alignment_sequences` (list): List of alignment sequences

---

#### `compare_words(sus_t, src_t, loc_sus, loc_src, methods={})`

**Description:** Compares two words using specified matching methods.

**Parameters:**
- `sus_t` (list): Suspect token list
- `src_t` (list): Source token list
- `loc_sus` (int): Position in suspect text
- `loc_src` (int): Position in source text
- `methods` (dict): Matching methods configuration

**Returns:**
- `score` (float): Similarity score (0-1)
- `method` (str): Method used for matching

**Supported Methods:**
- `"exact"`: Exact string matching
- `"edit_distance"`: Levenshtein distance (threshold as value)
- `"gematria"`: Hebrew numerical value matching
- `"stemming"`: Root word comparison
- `"embedding"`: Vector similarity
- `"orthography"`: Spelling variation handling
- `"sofiot"`: Hebrew final letter normalization
- `"llm"`: Large language model comparison

---

### Hebrew Text Processing Functions

#### `hebtext2num(txt)`

**Description:** Converts Hebrew text numbers to integers.

**Parameters:**
- `txt` (str): Hebrew text number

**Returns:**
- `int`: Numeric value, or -1 if conversion fails

**Supported Hebrew Numbers:**
- Units: אחד, שנים, שלושה, ארבעה, חמישה, ששה, שבעה, שמונה, תשעה
- Tens: עשרה, עשרים, שלושים, ארבעים, חמישים, ששים, שבעים, שמונים, תשעים
- Hundreds: מאה, מאתים
- Thousands: אלף, אלפים

**Example:**
```python
ta.hebtext2num("שלושה")  # Returns: 3
ta.hebtext2num("עשרים")  # Returns: 20
```

---

#### `is_abbreviation(token, get_spliter=False, indicator="'")`

**Description:** Detects Hebrew abbreviations and optionally splits them.

**Parameters:**
- `token` (str): Token to check
- `get_spliter` (bool, default=False): Whether to return split tokens
- `indicator` (str, default="'"): Abbreviation indicator character

**Returns:**
- `bool`: Whether token is an abbreviation
- `list` (if get_spliter=True): Split tokens

**Example:**
```python
is_abbrev, tokens = ta.is_abbreviation("ר'משה", get_spliter=True)
# Returns: (True, ["ר", "משה"])
```

---

#### `replace_chars(exchange, replacables, s)`

**Description:** Replaces characters in a string based on mapping rules.

**Parameters:**
- `exchange` (list): Characters to find
- `replacables` (list): Characters to replace with
- `s` (str): String to process

**Returns:**
- `str`: Processed string

---

### Scoring and Analysis Functions

#### `alignmentScore(alignment_sequences, increment2one=0.3, decrement_gap=0.1, verbose=False, prune=0.0)`

**Description:** Calculates comprehensive scores for alignment sequences.

**Parameters:**
- `alignment_sequences` (list): List of alignment sequences
- `increment2one` (float, default=0.3): Bonus for consecutive alignments
- `decrement_gap` (float, default=0.1): Penalty for gaps between alignments
- `verbose` (bool, default=False): Print detailed scoring information
- `prune` (float, default=0.0): Minimum score threshold for inclusion

**Returns:**
- `max_score` (float): Maximum alignment score
- `scored_sequences` (dict): Dictionary of scored alignment sequences

**Example:**
```python
max_score, scored_sequences = ta.alignmentScore(
    alignment_sequences,
    increment2one=0.4,
    decrement_gap=0.15,
    prune=0.2
)
```

---

#### `word_edit_distance(tokens1, tokens2, mode='distance')`

**Description:** Calculates edit distance between token sequences.

**Parameters:**
- `tokens1` (list): First token sequence
- `tokens2` (list): Second token sequence
- `mode` (str, default='distance'): Calculation mode

**Modes:**
- `'distance'`: Raw edit distance
- `'ratio'`: Normalized similarity ratio (0-1)

**Returns:**
- `float`: Edit distance or ratio

---

### Visualization Functions

#### `synopsis_2_html(src_t, df_suspect_alignment)`

**Description:** Generates HTML visualization of alignments.

**Parameters:**
- `src_t` (list): Source token list
- `df_suspect_alignment` (pandas.DataFrame): Alignment DataFrame

**Returns:**
- `suspect_html` (list): HTML elements for suspect text
- `source_html` (list): HTML elements for source text

---

#### `synopsis2htmlNew(text1_t, text2_t, align_sequenses)`

**Description:** Creates enhanced HTML visualization of alignments.

**Parameters:**
- `text1_t` (list): First text tokens
- `text2_t` (list): Second text tokens
- `align_sequenses` (list): Alignment sequences

**Returns:**
- `str`: HTML representation

---

#### `synopsis2htmlTable(text1_t, text2_t, align_sequenses)`

**Description:** Creates HTML table representation of alignments.

**Parameters:**
- `text1_t` (list): First text tokens
- `text2_t` (list): Second text tokens
- `align_sequenses` (list): Alignment sequences

**Returns:**
- `str`: HTML table

---

### Utility Functions

#### `alignment_to_df(aligned, suspect_t, src_t)`

**Description:** Converts alignment sequences to pandas DataFrame.

**Parameters:**
- `aligned` (list): Alignment sequences
- `suspect_t` (list): Suspect tokens
- `src_t` (list): Source tokens

**Returns:**
- `pandas.DataFrame`: Alignment information in tabular format
- `numpy.array`: Suspect position matrix
- `numpy.array`: Source position matrix

---

#### `similarity(w1, w2, model)`

**Description:** Calculates semantic similarity between two words using embeddings.

**Parameters:**
- `w1` (str): First word
- `w2` (str): Second word
- `model`: Embedding model

**Returns:**
- `float`: Similarity score (0-1)

---

## Method Configuration

### Methods Dictionary Structure

The `methods` parameter accepts a dictionary with the following possible keys:

```python
methods = {
    # Edit distance matching
    "edit_distance": 0.8,           # float: similarity threshold (0-1)
    
    # Hebrew-specific methods
    "gematria": True,               # bool: enable gematria matching
    "sofiot": True,                 # bool: handle Hebrew final letters
    "orthography": True,            # bool: handle spelling variations
    
    # Advanced matching
    "stemming": True,               # bool: enable stemming
    "embedding": 0.75,              # float: embedding similarity threshold
    "llm": False,                   # bool or object: LLM-based comparison
    
    # Structural methods
    "internal_swap": True,          # bool: allow word transpositions
    "external_swap": False,         # bool: cross-sequence swapping
    
    # Synonym and semantic methods
    "synonyms": True,               # bool: enable synonym matching
    "lemma": True,                  # bool: lemmatization matching
}
```

### Hebrew Analysis Integration

For advanced Hebrew processing, use the `HebAnalysis` class:

```python
from TRAligner.alignment_tools import HebAnalysis

# Initialize Hebrew analyzer
heb_analyzer = HebAnalysis(
    txt="sample text for preprocessing",
    mpath="/path/to/models",
    compare_method="base"  # or "segment"
)

# Use in methods
methods = {
    "llm": heb_analyzer,
    "edit_distance": 0.7
}
```

---

## DataFrame Structure

The alignment DataFrame contains the following columns:

- `token` (str): The token text
- `position` (int): Position in the sequence
- `match` (float): Match score (0-1)
- `match_procesure` (str): Method used for matching
- `suspect_pos` (int): Position in suspect text (-1 if no match)
- `source_pos` (int): Position in source text (-1 if no match)

---

## Error Codes and Handling

### Common Return Values

- **Score of -1**: Indicates failed comparison or invalid input
- **Empty alignment_sequences**: No valid alignments found
- **None DataFrame**: Alignment process failed

### Error Handling Example

```python
try:
    alignment_sequences, df_alignment, _, _ = ta.alignment(
        suspect_tokens, source_tokens, methods=methods
    )
    
    if not alignment_sequences:
        print("No alignments found - try adjusting thresholds")
    elif df_alignment is None:
        print("Alignment failed - check input tokens")
    else:
        print(f"Success: {len(alignment_sequences)} alignments found")
        
except Exception as e:
    print(f"Alignment error: {e}")
```

---

## Performance Notes

### Computational Complexity

- **Smith-Waterman**: O(m×n) where m, n are sequence lengths
- **Edit Distance**: O(m×n) for each word pair comparison
- **Gematria**: O(1) for each word pair

### Memory Usage

- Score matrices require O(m×n) memory
- Large texts should be processed in segments
- Consider using pruning to reduce memory footprint

### Optimization Tips

1. **Preprocessing**: Clean and normalize tokens before alignment
2. **Method Selection**: Disable unused methods for better performance
3. **Thresholds**: Higher thresholds reduce computation time
4. **Chunking**: Process long texts in smaller segments

---

*This API reference corresponds to the TRAligner package implementation in `text_alignment_clean.py`*
