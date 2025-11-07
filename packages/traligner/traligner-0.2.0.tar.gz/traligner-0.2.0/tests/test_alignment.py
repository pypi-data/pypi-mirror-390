import text_alignment_clean as ta
import pandas as pd

def test_alignment_and_scoring(suspect_sequence= None, potential_sequence=None):
    # Test case for alignment scoring
    if suspect_sequence is None:
        suspect_sequence = ['Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Writings_Psalms_68_7',
                            'Tanakh_Writings_Psalms_68_7',
                            'Tanakh_Torah_Genesis_44_16',
                            'Tanakh_Writings_Psalms_68_7',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_1_49',
                            'Tanakh_Torah_Exodus_32_26',
                            'Tanakh_Torah_Exodus_32_26',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Genesis_46_27',
                            'Tanakh_Torah_Genesis_46_27',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_3_16']
    if potential_sequence is None:
        potential_sequence = ['Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_1_49',
                            'Tanakh_Torah_Exodus_32_26',
                            'Tanakh_Torah_Exodus_32_26',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Genesis_46_27',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_3_15',
                            'Tanakh_Torah_Numbers_3_16']
   
    #Align thesequences
    als, df_sus_a, sus_m, src_m = ta.alignment(suspect_sequence,
                                               potential_sequence, 
                                               match_score=30,
                                               mismatch_score=1,
                                               methods={"ignore_tokens": ["*"]})

    # Simple Scriingpt to test the alignment scoring functionality
    alignment_score = ta.alignmentScore(als, verbose=False)
    print("Alignment Simple Score:", alignment_score[0])
    
    #with open(b"/Users/hadarmiller/Downloads/tfidf_unigram_Hebrew.pickle","rb") as f:
    #    df_tfidf = pickle.load(f)
    
    df_tfidf = pd.read_pickle("../../lexicons/tfidf_unigram_Hebrew.pickle")
    increment2one = {"src_t": potential_sequence, "sus_t": suspect_sequence, "tfidf": df_tfidf,
                 'default':0.1, "i21": 0.3 }
    sseq = ta.alignmentScore(als, increment2one=increment2one, 
                             decrement_gap=0.2, 
                            verbose=False, prune=0.0)
    
    print("Alignment Incremental Score:", sseq[0])
    

    
    
    
