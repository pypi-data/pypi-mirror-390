"""
TRAligner - Text Reuse Alignment for Hebrew and Multi-language Texts

This package provides sophisticated text alignment algorithms specifically designed
for Hebrew and other ancient languages, with support for fuzzy matching, 
morphological analysis, and multi-language tokenization.
"""

# Import main alignment functions
from .text_alignment_clean import (
    alignment,
    smith_waterman,
    alignmentScore,
    seqScore,
    alignment_to_df,
    compare_words,
    create_score_matrix,
    intra_span_alignment,
    inter_span_alignment,
    word_edit_distance,
    seqDensity,
    twoSeqDensity,
    merge_sequences,
    validate_sequence,
    synopsis_2_html,
    synopsis2htmlNew,
    synopsis2htmlTable,
    alignmentScore2HTML,
)

# Import alignment tools
from .alignment_tools import HebAnalysis

__version__ = "0.2.0"
__author__ = "Hadar Miller"

__all__ = [
    "alignment",
    "smith_waterman",
    "alignmentScore",
    "seqScore",
    "alignment_to_df",
    "compare_words",
    "create_score_matrix",
    "intra_span_alignment",
    "inter_span_alignment",
    "word_edit_distance",
    "seqDensity",
    "twoSeqDensity",
    "merge_sequences",
    "validate_sequence",
    "synopsis_2_html",
    "synopsis2htmlNew",
    "synopsis2htmlTable",
    "alignmentScore2HTML",
    "HebAnalysis",
]
