#This modification adds the parent directory to the Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
# import Levenshtein as lev
import math, re
import TRelasticExt as ee
from hebrew_numbers import gematria_to_int
from rapidfuzz import distance

class LocalDistance:
    def __init__(self):
        pass
    def distance(self, s1, s2):
        dist = distance.Levenshtein.distance(s1, s2)
        return dist

    def ratio(self, s1, s2):
        dist = self.distance(s1, s2)
        length = len(s1) + len(s2)
        ratio = (length - dist) / length
        return ratio

lev = LocalDistance()


class LocalGreekStemmer():
    def __init__(self, verbose=False):
        self.local_stemmer = None
        self.verbose = verbose
    def _load_module(self):
        from greek_stemmer import GreekStemmer
        if self.verbose:
            print(f"Greek stemer is loaded")
        self.local_stemmer = GreekStemmer()
    def stem(self, param, verbose=False):

        if self.local_stemmer is None:
            self._load_module()

        try:
            tmp = self.local_stemmer.stem(param)
        except Exception:
            if verbose or self.verbose:
                print(f"Stemming error")
            tmp = param

        return tmp


stemmer = LocalGreekStemmer(verbose=False)


def hebtext2num(txt):
    number_dict = {"אחד": 1,
                   "אחת": 1,
                   "שנים": 2,
                   "שניים": 2,
                   "שתים": 2,
                   "שתיים": 2,
                   "שתי": 2,
                   "שלש": 3,
                   "שלוש":3,
                   "שלשה": 3,
                   "שלושה": 3,
                   "ארבע": 4,
                   "ארבעה": 4,
                   "חמש": 5,
                   "חמשה": 5,
                   "חמישה": 5,
                   "שש": 6,
                   "ששה": 6,
                   "שישה": 6,
                   "שבע": 7,
                   "שבעה": 7,
                   "שיבעה": 7,
                   "שמונה": 8,
                   "שמנה": 8,
                   "תשע": 9,
                   "תשעה": 9,
                   "תישעה": 9,
                   "עשר": 10,
                   "עשרה": 10,
                   "עשרת": 10,
                   "עשרים": 20,
                   "שלשים": 30,
                   "שלושים": 30,
                   "ארבעים": 40,
                   "חמישים": 50,
                   "חמשים": 50,
                   "שישים": 60,
                   "ששים": 60,
                   "שבעים": 70,
                   "שיבעים": 70,
                   "שמונים": 80,
                   "שמנים": 80,
                   "תשעים": 90,
                   "מאה": 100,
                   "מאתים": 200,
                   "מאות": -100,
                   "אלף": -1000,
                   "אלפים": -1000,
                   "רבבה": 10000,
                   "ריבוא": 10000,
                   "ריבא": 10000,
                   "רבבות": -10000,
                   "תריסר": 12,
                   "מניין": 10}

    if type(txt) != str:
        return -1
    if len(txt) > 1 and txt[0] =="ו":
        txt= txt[1:]
    tnum = txt.split(" ")
    if len(tnum) == 0 or tnum[0] not in number_dict:
        return -1
    counter = abs(number_dict[tnum[0]])
    for n in tnum[1:]:
        if n[0] == "ו":
            n = n[1:]
        if n in number_dict:
            next_num = number_dict[n]

            if next_num > 0:
                counter += next_num
            else:
                counter = counter * -1 * next_num
        else:
            pass

    return counter

def replace_chars(exchange, replacables, s):
    if type(exchange) != list:
        return -1
    if type(replacables) == str:
        try:
            pattern = str([x for x in exchange])
            return re.sub(pattern, replacables, s)
        except Exception:
            return s
    elif type(replacables) == list:
        if len(exchange) != len(replacables):
            -1
        for c in range(len(exchange)):
            s = re.sub(exchange[c], replacables[c], s)
        return s
    return -1

def similarity(w1, w2, model):
    '''

    :param w1: token a
    :param w2: token b
    :param model: word embedding model (fasText)
    :return: the cosin similarity between the tokens
    '''

    def cosin(v, w):
        return np.dot(v, w) / (np.linalg.norm(v) * np.linalg.norm(w))

    try:
        if type(model.__class__.__name__) == str:
            vw1 = model.get_word_vector(w1) # FastText package model
        else:
            vw1 = model.wv[w1] # Gensim model
    except Exception:
        # print("{} missing in dictionary".format(w1))
        return -1, "{} missing in dictionary".format(w1)
    try:
        if type(model.__class__.__name__) == str:
            vw2 = model.get_word_vector(w2) # FastText package model
        else:
            vw2 = model.wv[w2]  # Gensim model
    except Exception:
        # print("{} missing in dictionary".format(w2))
        return -1, "{} missing in dictionary".format(w2)

    return cosin(vw1, vw2), "OK"

def check_morphology_embeding(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        model_name = 'default'
        for tmp in methods["morphology-embeding"]:
            if len(tmp) == 4:
                model, embeding_threshold, alpha, model_name = tmp
            elif len(tmp) == 3:
                model, embeding_threshold, alpha = tmp
            elif len(tmp) == 2:
                model, embeding_threshold = tmp
                alpha = 0.5
            else:
                return None
            
            #print(f"alignment new --> compare_words --> alpha = {alpha}")
            
            if model.__class__.__name__ == "EmbeddingRapper":
                    distance = model.similarity(w1, w2, model_name=model_name)
            else:
                distance = similarity(w1, w2, model)
            
            ratio = lev.ratio(w1, w2)

            weighed_dist = distance[0] * alpha + ratio * (1 - alpha)
            # print(
            #     f"w1: {w1}, w2: {w2}, ratio: {ratio}, distance: {distance}, weighted: {weighed_dist}, Threshould={embeding_threshold}\n{round(distance[0], 2)}*{alpha}+{round(ratio, 2)}*{1 - alpha}={round(weighed_dist, 2)}")
            if weighed_dist >= embeding_threshold: return (weighed_dist, "morphology_embeding_match")
        return None



def is_abbreviation(token, get_spliter = False, indicator="'"):
    token_pos = token.split(indicator)
    if len(token_pos) == 1:
        # Not an abbriviation
        if get_spliter:
            return False, None
        return False
    if get_spliter:
        if len(token_pos) == 1:
            splited_tokens = [token_pos+indicator]
        else:
            splited_tokens = [x+indicator for x in token_pos[:-1] if x != ""]
        if token_pos[-1] != "":
            splited_tokens.append(token_pos[-1])
        return True, splited_tokens
    return True


def alignment_to_df(aligned, suspect_t, src_t):
    '''
    :param aligned: list of lists. the output of "align" function
    :param suspect_t: list of the suspect's tokens.
    :param src_t: list of the source;s tokens.
    :return: dataframe: Convert the output of "align" function into a dataframe for ACT framework
    '''

    def handle_seq(seq, df, suspect_matrix, source_matrix):

        counter = max(df["match_id"])
        for idx,match in enumerate(seq):
            # print(match)
            # Accumulate matrices
            try:
                source_matrix[match[1]] = match[2]
            except Exception:
                print(f"source matrix; {source_matrix}\nmatch: {match}\nseq {seq}")
            try:
                if int(match[0]) == match[0]: suspect_matrix[match[0]] = match[2]
            except Exception:
                print(f"suspect_matrix; {suspect_matrix}\nsource matrix: {source_matrix}\nmatch: {match}\nseq {seq}")
            # Check if the naxt location already available in the df
            # tmp = df[df['location']==match[0]]
            tmp = df.index[df['location'] == match[0]].tolist()
            if len(tmp) > 0:
                location = tmp[0]
            else:
                location = -1

            #if math.ceil(match[0]) == math.floor(match[0]):
            if location > -1:
                df.at[location, "match_id"] = idx +counter + 1
                df.at[location, 'match'] = match[2]
                df.at[location, 'match_procesure'] = match[3]

                df.at[location, "globa_source_loc"] = match[1]

                # Bug fixed 25/2/2024. When aligning two tokens to one, we need to append it.
                #df.at[location, "globa_source_token"] = src_t[match[1]]
                tmp = df.at[location,"globa_source_token"]
                if len(tmp) > 0:
                    tmp = " ".join([tmp, src_t[match[1]]])
                else:
                    tmp = src_t[match[1]]
                df.at[location, "globa_source_token"] = tmp

                tmp = df.at[location, "src_matches"]
                tmp.append(match[1])
            else:
                tmp = {'token': suspect_t[math.floor(match[0])], 'origin': "suspect", 'match': match[2],
                       'match_id': idx+counter + 1, 'location': match[0], 'last_match_location': 0, 'match_procesure': match[3],
                       'new_reading': suspect_t[math.floor(match[0])], 'globa_location': 0, 'local_source_loc': 0,
                       'globa_source_loc': match[1], "globa_source_token": src_t[match[1]],
                       'src_matches': [match[1]], 'index': 0
                    }
                #11/10/2024
                #df = df.append(tmp, ignore_index=True)
                df = pd.concat([df, pd.DataFrame([tmp])], ignore_index=True)

        return df.sort_values(by=['location']), suspect_matrix, source_matrix
        # return df

    # Crreate source & suspect matrices
    suspect_matrix = np.zeros(len(suspect_t))
    source_matrix = np.zeros(len(src_t))

    # Create a simple dataframe. row for each suspect token.
    tmp = [{'token': x, 'origin': "suspect", 'match': 0.0, 'match_id': 0, 'location': idx,
            'last_match_location': 0, 'match_procesure': '', 'new_reading': x,
            'globa_location': 0, 'local_source_loc': 0, 'globa_source_loc': 0, "globa_source_token": "",
            'src_matches': [], 'index': 0
            } for idx, x in enumerate(suspect_t)]
    df_suspect_alignment = pd.DataFrame(tmp)

    # manipulate the rows with the sequences found in the align function.
    for seq in aligned: df_suspect_alignment, suspect_matrix, source_matrix = handle_seq(seq,
                                                                                         df_suspect_alignment,
                                                                                         suspect_matrix,
                                                                                         source_matrix)
    return df_suspect_alignment, suspect_matrix, source_matrix

def compare_words(sus_t, src_t, loc_sus, loc_src, methods={}):


    def check_synonyms(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        if 'vocabulary' not in methods['synonyms']: return None
        tmp = methods['synonyms']['vocabulary']
        if w1 in tmp and w2 in tmp and tmp[w1] == tmp[w2]:
            return (1.0, "synonym_simple_match")
        return None

    def check_stemming(w1,w2,host,index,analyzer, stopwords=None):
        if stopwords and (w1 in stopwords or w2 in stopwords):
            return (0, "")

        # ret = elastic_stemmer(w1 + " " +  w2, index, analyzer, host)
        # ret = ret.split(" ")
        # if len(ret)==2 and ret[0] == ret[1]:
        #     # print(f"check_stemming: {w1} vs {w2}\n{ret}")
        #     return (0.8, "stemmer_match")

        #print(f"Text Alignment New --> compare_words --> check_stemming: {w1} vs {w2}")
        if stemmer.stem(w1.upper()).lower() == stemmer.stem(w2.upper()).lower():
            #print(f"Text Alignment New --> compare_words --> check_stemming: {w1} vs {w2} - SAME")
            return (0.8, "stemmer_match")

        return None

    def check_ortography(w1,w2,sus_t, src_t, loc_sus, loc_src, methods={}):
        remove_chars = methods.get("ortography", None)
        if replace_chars(remove_chars, "", w1) == replace_chars(remove_chars, "", w2):
            return (0.8, "orthography_match")
        return None

    def check_sofiot(w1,w2,sus_t, src_t, loc_sus, loc_src, methods={}):
        for fr,to in [("ם","מ"), ("ן","נ"), ("ץ","צ"), ("ף","פ"), ("ך","כ")]:
            w1 = w1.replace(fr,to)
            w2 = w2.replace(fr,to)
        if w1==w2:
            return (1., "sofiot_match")

        return None



    def check_embeding(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        for model, embeding_threshold in methods["embeding"]:
            distance = similarity(w1, w2, model)
            if distance[0] >= embeding_threshold: return (distance[0], "embeding_match")
        return None

    def check_lemma(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        lemmatizer = methods["lemmatizer"]
        if lemmatizer(w1) == lemmatizer(w2): return (0.8, "lemma_match")
        return None

    def check_llm(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        llm = methods["llm"]
        # print(f"text alignment clean-->compare_words--> {llm.compare(w1)} - {llm.compare(w2)}")
        w1_base = llm.compare(w1)
        w2_base = llm.compare(w2)
        if w1_base == w2_base: return (0.8, "llm_match")
        if "morphology-embeding" in methods:
            ret = check_morphology_embeding(w1_base, w2_base, sus_t, src_t, loc_sus, loc_src, methods=methods)
            if ret: return (ret[0]*0.8, f"llm + {ret[1]}")
        return None


    def check_gematria(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        # Detect Gematria
        # Case I - Token Number (שלש), Next token (עשרה) - Number , lst: gematria (יג מלחמות)
        # Case II - suspect Gematria (יג), Next token (מלחמות) , source: ( שלש עשרה מלחמות ) : "single_gematria_match" , "double_gematria_match"



        # check case I

        sus_number = hebtext2num(w1)
        if sus_number > 0:
            if len(w2) > 1 and w2[0] == "ו":
                src_number = gematria_to_int(w2[1:])
            else:
                src_number = gematria_to_int(w2)
            if loc_sus < len(sus_t) - 1 and hebtext2num(sus_t[loc_sus + 1]) != -1:

                sus_number2 = hebtext2num(w1 + " " + sus_t[loc_sus + 1])
                # print(f"{w1} {sus_t[loc_sus + 1]}, {sus_number2}-{src_number}")
                if sus_number2 == src_number:
                    # print(f"Aligned: {w1} {sus_t[loc_sus + 1]} and {w2}")
                    return (0.75, "double_rev_gematria_match")

            else:
                if sus_number == src_number:
                    # print(f"Aligned: {w1} and {w2}")
                    return (0.75, "single_gematria_match")
        # check case II

        src_number = hebtext2num(w2)
        if src_number > 0:
            if len(w1) > 1 and w1[0] == "ו":
                sus_number = gematria_to_int(w1[1:])
            else:
                sus_number = gematria_to_int(w1)
            if loc_src < len(src_t) - 1 and hebtext2num(src_t[loc_src + 1]) != -1:
                # print(f"w1: {w1} = {sus_number}, src: {w2} {src_t[loc_src + 1]}\n{src_t}")
                src_number2 = hebtext2num(w2 + " " + src_t[loc_src + 1])
                if sus_number == src_number2:
                    # print(f"Aligned: {w2} {src_t[loc_src + 1]} and {w1}")
                    return (0.75, "double_gematria_match")
            else:
                if sus_number == src_number:
                    # print(f"Aligned: {w2} and {w1}")
                    return (0.75, "single_gematria_match")
        return None

    def check_abbreviation(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        for indicator in methods["abbreviation"]:
            # Detect if w1 token has avvriviation
            has_abbv, tokens_list = is_abbreviation(w1, True, indicator=indicator)
            if has_abbv and len(w1) > 2 and tokens_list[0][:-1] == w2[:len(tokens_list[0][:-1])]: return (
            0.75, "abbreviation_match")

            # Detect if w2 token has avvriviation
            has_abbv, tokens_list = is_abbreviation(w2, True, indicator=indicator)
            if has_abbv and len(w2) > 2 and tokens_list[0][:-1] == w1[:len(tokens_list[0][:-1])]: return (
            0.75, "abbreviation_match")
        return None

    def check_edit_dist(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        ratio = lev.ratio(w1, w2)
        if ratio >= methods["edit_distance"]: return (ratio, "edit_distance_match")
        return None

    def check_extra_sep(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        for seperator in methods["extra_seperators"]:
            if loc_sus < len(sus_t) - 1 and w2 == seperator.join([w1, sus_t[loc_sus + 1]]):
                # print(f"SRC: {w2} Suspect: {w1} {sus_t[loc_sus+1]}")
                return (0.8, "extra_spaces_match")
        return None

    def check_missing_sep(w1, w2, sus_t, src_t, loc_sus, loc_src, methods={}):
        for seperator in methods["missing_seperators"]:
            if loc_src < len(src_t) - 1 and w1 == seperator.join([w2, src_t[loc_src + 1]]):
                # print(f"Suspect: {w1} SRC: {w2} {src_t[loc_src + 1]}")
                return (0.8, "missing_spaces_match")
        return None

    def check_ignore_tokens(w1, w2, sus_t, src_t, loc_sus, loc_src, methods):
        '''
        If one of the tokens in the "do not compare" list. return non similar
        '''
        if w1 in methods['ignore_tokens'] or w2 in methods['ignore_tokens']:
            return True
        return False

    w1 = sus_t[loc_sus]
    w2 = src_t[loc_src]

    if "ignore_tokens" in methods:
        ret = check_ignore_tokens(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret:
            #print(f"Text Alignment --> compare_words --> {w1}, {w2} in ignore_tokens ({methods['ignore_tokens']})")
            return (0, "")

    if w1 == w2:
        return (1, "exact_match")

    if "synonyms" in methods:
        ret = check_synonyms(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    # Orthography match (Max two character seperation)
    if "ortography" in methods:
        ret = check_ortography(w1,w2,sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret
        ret = check_sofiot(w1,w2,sus_t, src_t, loc_sus, loc_src, methods={})
        if ret: return ret

    if "stemming" in methods:
        host = methods["stemming"]["host"]
        index = methods["stemming"]["index"]
        analyzer = methods["stemming"]["analyzer"]
        stopwords = methods["stemming"].get("stopwords",None)
        ret = check_stemming(w1, w2, host, index, analyzer, stopwords=stopwords)
        if ret: return ret

    if "lemmatizer" in methods:
        ret = check_lemma(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    # Align extra spaces between the suspect tokens. "הת רחצתי"  must preceed embedings.
    if "extra_seperators" in methods:
        ret = check_extra_sep(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    # Align missing spaces between the suspect tokens. sus:"נבוכדנצרלפני", "מלעיבים" src: "מלעי בים"  "נבוכדנצר לפני" must preceed embedings.
    if "missing_seperators" in methods:
        ret = check_missing_sep(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    # removed condition on 14/2 needs checking
    #if "morphology-embeding" in methods and len(w1) > 2:
    if "morphology-embeding" in methods:
        ret = check_morphology_embeding(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    if "llm" in methods and methods['llm']:
        ret = check_llm(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret



    # Align Close meaning - Embedings (semanticaly close tokens, tokens with 3 chars)
    if "embeding" in methods and len(w1) > 2:
        ret = check_embeding(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    # Check the edit distance ratio. If it exceeds threshold, accept alignment
    if "edit_distance" in methods:
        ret = check_edit_dist(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    if "abbreviation" in methods:
        ret = check_abbreviation(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    if methods.get("gematria", True):
        ret = check_gematria(w1, w2, sus_t, src_t, loc_sus, loc_src, methods=methods)
        if ret: return ret

    # Align tokens that diferent in characters that commonly replaced by OCR like "םס"
    if "ocr_replacables" in methods:
        ocr_patterns = methods.get("ocr_replacables", None)
        w1_r = w1.replace("'", "").replace('"', "")
        w2_r = w2.replace("'", "").replace('"', "")
        for pattern in ocr_patterns:
            w1_r = re.sub("[" + pattern + "]+", pattern[0], w1_r)
            w2_r = re.sub("[" + pattern + "]+", pattern[0], w2_r)
        if w1_r == w2_r: return (0.8, "ocr_replacables")


    return (0, "")


def create_score_matrix(suspect_t, src_t, match_score=2, mismatch_score=1, methods={}, gap_score =1):
    '''The function creates the score_matrix and the path_matrix'''

    def calc_score(score_matrix, x, y):
        '''this function is used during the score_matrix construction,
        it is suitable for affine gap penalties and works with a substitution matrix'''

        def first_pos_max(lst):
            maxi = max(lst)
            return [i for i, j in enumerate(lst) if j == maxi][0]

        def gap_penalty(k, gap_score):
            #return 3 * k
            return gap_score * k

        def substitution_score(x, y):
            # If the previous token detected extra space. This token is irrelevant
            # if x > 0 and Sim[x-1][y][1] == "extra_spaces_match":
            #     print(f"here! {suspect_t[x-1]} - {src_t[y-1]} Score: {Sim[x-1][y][0] * match_score}")
            #     Sim[x][y] = Sim[x-1][y]
            #     return Sim[x][y][0] * match_score

            Sim[x][y] = compare_words(suspect_t, src_t, x-1, y-1, methods = methods)
            if Sim[x ][y][0] > 0: return Sim[x][y][0] * match_score

            return -1 * mismatch_score

        # gap_score = mismatch_score
        similarity = substitution_score(x, y)

        same_row = [(score_matrix[x][y - l] - gap_penalty(l, gap_score)) for l in range(1, x + 1)]
        same_col = [(score_matrix[x - k][y] - gap_penalty(k, gap_score)) for k in range(1, x + 1)]

        up_score = max(same_col)
        left_score = max(same_row)

        diag_score = score_matrix[x - 1][y - 1] + similarity
        pos_max_up = first_pos_max(same_col)
        pos_max_left = first_pos_max(same_row)

        score = max(0, diag_score, up_score, left_score)

        if score == diag_score:
            antecedent = [1, 'DIAG']
            return score, antecedent
        elif score == up_score:
            antecedent = [pos_max_up + 1, 'UP']
            return score, antecedent
        elif score == left_score:
            antecedent = [pos_max_left + 1, 'LEFT']
            return score, antecedent
        else:
            return score, [0, 'NULL']

    rows = len(suspect_t) + 1
    cols = len(src_t) + 1
    score_matrix = [[0 for col in range(cols)] for row in range(rows)]
    path_matrix = [[[0, 'NULL'] for col in range(cols)] for row in range(rows)]
    Sim = [[(0, "") for k in range(cols)] for x in range(rows)]


    for i in range(1, rows):
        for j in range(1, cols):
            score, antecedent = calc_score(score_matrix, i, j)
            score_matrix[i][j], path_matrix[i][j] = score, antecedent


    return score_matrix, path_matrix, Sim

def clear_score_matrix_node(row,col,score_matrix, path_matrix):
    #print(f"clear current pos: {score_matrix[row][col]}")
    score_matrix[row][col] = 0


    if row<len(score_matrix)-1 and path_matrix[row+1][col][1] == 'UP':
        #print(f"Recursive down: {row+1}/{col}")
        clear_score_matrix_node(row+1,col,score_matrix,path_matrix)

    if col<len(score_matrix[0])-1 and path_matrix[row][col+1][1] == 'LEFT':
        #print(f"Recursive right: {row}/{col+1}")
        clear_score_matrix_node(row,col+1,score_matrix,path_matrix)

    if row<len(score_matrix)-1 and col<len(score_matrix[0])-1 and path_matrix[row+1][col+1][1] == 'DIAG':
        #print(f"Recursive diag down: {row+1}/{col}")
        clear_score_matrix_node(row+1,col+1,score_matrix,path_matrix)

def get_next_top_score(score_matrix, used_suspect=[], used_src=[]):
    # get matrix max value positions
    def get_argmax(arr):
        vector = np.array(arr).reshape(len(arr) * len(arr[0]))
        max_val = np.amax(vector)
        if max_val == 0 : return []
        mvector = np.argwhere(vector == max_val)
        max_vector = [divmod(x[0], len(arr[0])) for x in mvector]
        return max_vector
    # counter = 0
    while True:
        # counter += 1
        next_pos = get_argmax(score_matrix)
        ret = [x for x in next_pos if x[0] not in used_suspect and x[1] not in used_src]
        if len(ret) > 0 or len(next_pos) == 0:
            break
        for x in next_pos:
            # old_value = score_matrix[x[0]][x[1]]
            score_matrix[x[0]][x[1]] = 0
            # print(f"Clear Value ({counter}), pos: {x}, old val: {old_value}")
    # print(f"Retun top score: {ret}, len next pos: {len(next_pos)}")
    return ret

def traceback(path_matrix, start_pos, score_matrix, seqA, seqB, Sim, used_suspect=[], used_src=[]):
    '''The function does the traceback based on the starting position
    and on the instructions contained in the path_matrix,
    it also displays the move done at each step '''

    x, y = start_pos
    aligned_seqA = []
    aligned_seqB = []
    aligned_pos_seqA = []
    aligned_pos_seqB = []

    while path_matrix[x][y] != [0, 'NULL']:

        # print(f"path: {x}/{y}, in suspect: {x in used_suspect}, in src: {y in used_src}\n{used_suspect}\n{used_src}")
        if x in used_suspect or y in used_src:
            break
        d, direction = path_matrix[x][y][0], path_matrix[x][y][1]
        if direction == 'DIAG':
            assert d == 1, 'path_matrix wrongly constructed !'
            aligned_seqA.append(seqA[x - 1])
            aligned_pos_seqA.append(x - 1)
            aligned_seqB.append(seqB[y - 1])
            aligned_pos_seqB.append(y - 1)
            x -= 1
            y -= 1
            # print('DIAG',score_matrix[x][y])
        elif direction == 'UP':
            for c in range(d):
                aligned_seqA.append(seqA[x - 1])
                aligned_seqB.append('-')
                x -= 1
                # print('UP',score_matrix[x][y])
        elif direction == 'LEFT':
            for c in range(d):
                aligned_seqA.append('-')
                aligned_seqB.append(seqB[y - 1])
                y -= 1
                # print('LEFT',score_matrix[x][y])
    # print(f"Traceback reached a 0 at : ({x},{y})\naligned_seqA: {aligned_seqA}\naligned_seqB: {aligned_seqB}")
    ret = [(x, y, Sim[x+1][y+1][0], Sim[x+1][y+1][1]) for x, y in zip(sorted(aligned_pos_seqA), sorted(aligned_pos_seqB))]
    ret += [(x, y + 1, z, w) for x, y, z, w in ret if w in ["double_gematria_match", "missing_spaces_match"]]
    ret += [(x +1, y , z, w) for x, y, z, w in ret if w in ["double_rev_gematria_match", "extra_spaces_match"]]
    # print(f"{ret}\nSim: {Sim}")
    return ret

def get_next_top_score(score_matrix, used_suspect=[], used_src=[]):
    # get matrix max value positions
    def get_argmax(arr):
        vector = np.array(arr).reshape(len(arr) * len(arr[0]))
        max_val = np.amax(vector)
        if max_val == 0 : return []
        mvector = np.argwhere(vector == max_val)
        max_vector = [divmod(x[0], len(arr[0])) for x in mvector]
        return max_vector
    # counter = 0
    while True:
        # counter += 1
        next_pos = get_argmax(score_matrix)
        ret = [x for x in next_pos if x[0] not in used_suspect and x[1] not in used_src]
        if len(ret) > 0 or len(next_pos) == 0:
            break
        for x in next_pos:
            # old_value = score_matrix[x[0]][x[1]]
            score_matrix[x[0]][x[1]] = 0
            # print(f"Clear Value ({counter}), pos: {x}, old val: {old_value}")
    # print(f"Retun top score: {ret}, len next pos: {len(next_pos)}")
    return ret

def intra_span_alignment(alignment_sequence, suspect_t, src_t, tokens_gap=4, methods = {}):
    suspect_match = [x[0] for x in alignment_sequence if x[3] != ""]
    src_match = [x[1] for x in alignment_sequence if x[3] != ""]
    if len(suspect_match) == 0 or len(src_match) == 0:
        return alignment_sequence

    # print(f"intra_span_alignment--> alignment_sequence: {alignment_sequence}\n\nsuspect match {suspect_match} source match: {src_match}")
    extend = 1 # extend the alignment from both sides to catch transpositions ajusents to the alignment
    max_sus = min(len(suspect_t), max(suspect_match)+1+extend)
    min_sus= max(0,min(suspect_match)-extend)
    free_suspects = [x for x in range(min_sus, max_sus) if x not in suspect_match ]


    # iterate over the unmatched suspect tokens
    for idx in free_suspects:
        max_src = min(len(src_t), max(src_match) + 1 + extend)
        min_src = max(0, min(src_match) - extend)
        free_srcs = [x for x in range(min_src, max_src) if x not in src_match]

        for src_token in free_srcs:
            cmp = compare_words(suspect_t, src_t, idx, src_token, methods=methods)
            if cmp[0] > 0:
                alignment_sequence.append((idx,src_token,cmp[0],"intra_span_" + cmp[1]))
                #print(f"intra_span_alignment --> Add Alignment ({idx}, {src_token}, {cmp[0]})")
                src_match.append(src_token)
    alignment_sequence = [x for x in alignment_sequence if x[3] != ""]
    # print(f"alignment_sequence: {alignment_sequence}")
    return alignment_sequence

def inter_span_alignment(alignment_sequence, suspect_t, src_t, tokens_gap=4, methods = {}):
    #methods["gematria"] = True
    suspect_match = [x[0] for x in alignment_sequence if x[3] != ""]

    src_match = [x[1] for x in alignment_sequence if x[3] != ""]

    # print(f"alignment_sequence: {alignment_sequence}\n\nsuspect match {suspect_match} source match: {src_match}")

    sus_anchor = -1
    src_anchor = -1
    #for idx in range(min(suspect_match), max(suspect_match)+1):
    for idx in range(len(suspect_t)):

        if idx in suspect_match:
            sus_anchor = idx
            src_anchor = src_match[suspect_match.index(idx)]
            continue

        close_free_tokens = [tidx for tidx,x in enumerate(src_t) if
                            tidx not in src_match and abs(tidx - src_anchor) <= tokens_gap]
        # Sort the list with respect to the src_anchor
        close_free_tokens.sort(key=lambda x: abs(src_anchor - x))

        # print(f"idx: {idx} sus_anchor: {sus_anchor} src_anchor: {src_anchor}\n suspect_token: {suspect_t[idx]}, close free: {close_free_tokens} ")

        for src_token in close_free_tokens:
            if sus_anchor > -1:
                cmp = compare_words(suspect_t, src_t, idx, src_token, methods = methods)
                # print(f"{suspect_t[idx]}, {src_t[src_token]} cmp: {cmp}")
                if cmp[0] > 0:
                    alignment_sequence.append((idx,src_token,cmp[0],"inter_span_" + cmp[1]))
                    src_match.append(src_token)
    alignment_sequence = [x for x in alignment_sequence if x[3] != ""]
    # print(f"alignment_sequence: {alignment_sequence}")
    return alignment_sequence



def smith_waterman(suspect_t, src_t, match_score=10, mismatch_score=1, methods={}, swap=False, gap_score =1,
                   minimum_alignment_size = 2):

    score_matrix, path_matrix, Sim = create_score_matrix(suspect_t, src_t, match_score=match_score,
                                                         mismatch_score=mismatch_score, methods=methods,
                                                         gap_score =gap_score)

    if score_matrix is None: return None
    alignment_sequences = []
    used_suspect = []
    used_src = []
    starts = get_next_top_score(score_matrix, used_suspect=used_suspect, used_src=used_src)

    # print(pd.DataFrame(score_matrix))

    while len(starts) > 0:
        #print(f"starts: {starts}")

        for start_pos in starts:

            alignment_sequence = traceback(path_matrix, start_pos, score_matrix, suspect_t, src_t, Sim, used_suspect, used_src)

            # The SW ignores internal swap in the sequence alignment. This procedure locate and align words transpositions
            # within the spans located for the suspets and sources.
            if methods.get("internal_swap", True):
                alignment_sequence = intra_span_alignment(alignment_sequence, suspect_t, src_t, tokens_gap=5,
                                                      methods=methods)
            #print(f"smith_waterman --> \n{start_pos}\nseq: {alignment_sequence}, Size: {len(alignment_sequence)}")

            if len(alignment_sequence) == 0:
                score_matrix[start_pos[0]][start_pos[1]] = 0
                continue

            clear_score_matrix_node(alignment_sequence[0][0], alignment_sequence[0][1], score_matrix, path_matrix)

            # Added on 18th Feb 2023. Need to be tested.
            #minimum_alignment_size = 2
            if len(alignment_sequence) < minimum_alignment_size:
                continue

            # The two line replaced to include the entire span in the excluded tokens
            tmp = [x[0]+1 for x in alignment_sequence]
            tmp1 = [x[1]+1 for x in alignment_sequence]
            if len(tmp) > 0 and len(tmp1) > 0:
                used_suspect += [x for x in range(min(tmp), max(tmp)+1)]
                used_src += [x for x in range(min(tmp1), max(tmp1)+1)]

            # The SW ignores internal swap in the sequence alignment. This procedure locate and align swaps of words
            # BETWEEN spans located for the suspets and sources.
            if methods.get("external_swap", False):
                alignment_sequence = inter_span_alignment(alignment_sequence, suspect_t,src_t, tokens_gap=5, methods=methods)

            if swap:
                alignment_sequence = [(x[1],x[0],x[2], x[3]) for x in alignment_sequence]

            alignment_sequence = [x for x in alignment_sequence if x[2]> 0]


            alignment_sequences.append(alignment_sequence)

        starts = get_next_top_score(score_matrix, used_suspect=used_suspect, used_src=used_src)
        # print(f"starts: {starts}\nused suspects: {used_suspect}\nused src: {used_src}")
    #print(alignment_sequences)
    return alignment_sequences


def alignment(suspect_t, src_t, match_score=3, mismatch_score=1, methods={}, gap_score=1, minimum_alignment_size = 2):
    '''
     :param suspect_t:
    :param src_t:
    :param match_score:
    :param mismatch_score:
    :param methods:
    :param gap_score:
    :param filter_by_occorences:
    :return:
    '''
    swap = len(suspect_t) > len(src_t)
    if swap:
        l_suspect_t = src_t.copy()
        l_src_t = suspect_t.copy()
    else:
        l_suspect_t = suspect_t.copy()
        l_src_t = src_t.copy()

    if 'llm' in methods and methods['llm']:
        '''
        llm is object of Class which contains methos compare to return the base form of a token
        it is used in the compare_words function.
        To makethis function execute faster, the _prepare_resource function extract base from from all the tokens in the 
        source and suspect in a single API call and store it in the llm object.
        '''
        methods['llm']._prepare_resources(" ".join(suspect_t+src_t))

    alignment_sequences = smith_waterman(l_suspect_t, l_src_t, match_score=match_score, mismatch_score=mismatch_score,
                                        methods=methods, swap=swap, gap_score=gap_score,
                                         minimum_alignment_size = minimum_alignment_size)



    df_suspect_alignment, suspect_matrix, source_matrix = alignment_to_df(alignment_sequences, suspect_t, src_t)
    #return [x for x in alignment_sequences if x[2] > 0]
    return alignment_sequences, df_suspect_alignment, suspect_matrix, source_matrix



def word_edit_distance(source, target, alignment=None, spliter=None, del_cost=1, ins_cost=1, sub_cost=2,
                       mode='distance'):
    '''
    The number of words eed to indest, replace,delete to transform one text to another
    :param source:
    :param target:
    :param alignment:
    :param spliter:
    :param del_cost:
    :param ins_cost:
    :param sub_cost:
    :param mode:
    :return:
    '''
    if type(source) == str:
        if spliter is not None:
            source = spliter(source)
            target = spliter(target)
        else:
            source = source.split(' ')
            target = target.split(' ')

    n = len(source)
    m = len(target)

    if alignment is not None:
        match_value = len([x[2] for x in alignment])
        return 1 - ((m - match_value) + (n - match_value)) / (m + n)

    MED_Matrix = np.zeros((n + 1, m + 1), dtype='int32')

    for i in range(1, n + 1): MED_Matrix[i][0] = MED_Matrix[i - 1][0] + del_cost
    for i in range(1, m + 1): MED_Matrix[0][i] = MED_Matrix[0][i - 1] + del_cost

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if source[i - 1] == target[j - 1]:
                # print(i-1,j-1)
                MED_Matrix[i][j] = min(
                    [MED_Matrix[i - 1][j] + del_cost, MED_Matrix[i - 1][j - 1] + 0, MED_Matrix[i][j - 1] + ins_cost])
            else:
                MED_Matrix[i][j] = min([MED_Matrix[i - 1][j] + del_cost, MED_Matrix[i - 1][j - 1] + sub_cost,
                                        MED_Matrix[i][j - 1] + ins_cost])

    # print(np.matrix(MED_Matrix))
    # print(MED_Matrix[n][m])

    if mode == "distance":
        return MED_Matrix[n][m]
    else:
        return (m + n - MED_Matrix[n][m]) / (m + n)


def seqDensity(seq, text1_t, text2_t, spliter = None):
    '''
    Get as input a single sequence alignment and the two texts that were aligned
    Returns the density ( word edit distance )
    '''
    suspect_tokens = [x[0] for x in seq]
    target_tokens = [x[1] for x in seq]
    sus_first = min(suspect_tokens)
    sus_last = max(suspect_tokens)
    sus_aligned = text1_t[sus_first:sus_last + 1]  # Set of suspect tokens that was aligned

    src_first = min(target_tokens)
    src_last = max(target_tokens)
    src_aligned = text2_t[src_first:src_last + 1]  # Set of source tokens that was aligned

    density = word_edit_distance(sus_aligned, src_aligned, alignment=seq, spliter=spliter, mode="ration")


    return density, sus_aligned, src_aligned


def twoSeqDensity(seq1, seq2, text1_t, text2_t, spliter=None):
    '''
    Recieve two sequences of alignments resulted from the comparison of text 1 and text2
    It calculate the density (word edit distance) when we merge these two sequences
    '''

    sus_first = min(seq1[0][0], seq2[0][0])
    sus_last = max(seq1[-1][0], seq2[-1][0])
    sus_aligned = text1_t[sus_first:sus_last + 1]  # Set of suspect tokens that was aligned
    src_first = min(seq1[0][1], seq2[0][1])
    src_last = max(seq1[-1][1], seq2[-1][1])
    src_aligned = text2_t[src_first:src_last + 1]  # Set of source tokens that was aligned

    ret = word_edit_distance(sus_aligned, src_aligned, alignment=seq1 + seq2, spliter=spliter, mode="ration")

    return ret, sus_aligned, src_aligned


def merge_sequences(align_seq, text1_t, text2_t, merge_threshold, spliter=None):
    if len(align_seq) < 2:
        return align_seq
    for it in range(10):
        # get longest sequence
        longest_seq = max((len(l), i) for i, l in enumerate(align_seq))[1]

        # Try to merge the longest sequence with the rest
        seq2merge = []
        for i in range(len(align_seq)):
            if i != longest_seq:
                # check the density of the merged sequences
                newDensity, sus_aligned, src_aligned = twoSeqDensity(align_seq[longest_seq], align_seq[i], text1_t,
                                                                        text2_t, spliter=spliter)
                if newDensity > merge_threshold:
                    seq2merge.append(i)
        if len(seq2merge) == 0:
            break

        # The sequences left out (not merged to the largest sequence)
        rest = [x for idx, x in enumerate(align_seq) if idx != longest_seq and idx not in seq2merge]

        # Megre the largest sequence with all the sequences that included in the seq2merge
        newSeq = align_seq[longest_seq]
        for j in seq2merge:
            newSeq += align_seq[j]
        rest.append(newSeq)

        if len(rest) == 1:
            return rest

        align_seq = rest

    return align_seq


def validate_sequence(seq, src_t, corpus, oc_ehost, fields, max_occ=8):
    def checkConsecutive(l):
        n = len(l) - 1
        return (sum(np.diff(sorted(l)) == 1) >= n)

    def checkOccurrence(sentence, fields, es_params, efilter=None):
        res = ee.get_sentence_count(sentence, fields, es_params, efilter=efilter, les=None)
        return res['hits']['total']['value']

    if len(seq) > 3:
        return True, "long sequence"

    sus = [x[0] for x in seq]
    src = [x[1] for x in seq]

    if not checkConsecutive(sus):
        return False, "non consecutive suspect citation"

    if not checkConsecutive(src):
        return False, "non consecutive source citation"

    # Check corpus usage
    if corpus:
        efilter = {'must': corpus}
    else:
        efilter = None
    oc = checkOccurrence(" ".join([src_t[x] for x in src]), fields, oc_ehost, efilter=efilter)
    # print(f"{oc} Occurrence of {src}")

    if oc > max_occ:
        return False, f"{oc} occorences exceed {max_occ}"

    return True, ""



"""
==============================
Score the alignment sequences
==============================
"""

def seqScoreOLD(sequsence, pos=0, increment2one=0.3, decrement_gap=0.1, verbose=False):
    '''
    Scoring the alignment sequences.
    Every consecutive aligned token increase the alignment score by distanceToOne * increment2one
    This will always leave the score bellow 1

    For each gap (mismatch i a sequence) the score decreases by gap * decrement_gap

    The score minimum is 0.5, If the gaps causes the score to go bellow zero: a new sub sequence is created

    Minimum score (of a single match) is 0.5


    '''
    def remove_alignment_duplicates(seq, pos=1):
        '''
        The alignment mightinclude duplicate usage of a single token. for example:
        [(63, 62, 0.85830885, 'embeding_match'), (64, 65, 1, 'exact_match'), (65, 66, 0.8, 'missing_spaces_match'), (65, 67, 0.8, 'missing_spaces_match')]
        use twice the 65 token in the zero position ( suspect)

        '''
        seen = set()
        unique_list = []

        for tup in seq:
            if tup[pos] not in seen:
                seen.add(tup[pos])
                unique_list.append(tup)

        return unique_list

    seq = remove_alignment_duplicates(sequsence.copy(), pos=pos)

    seq = sorted(seq, key=lambda x: x[pos])
    gaps = [x[pos] - y[pos] - 1 for x, y in zip(seq[1:], seq[:-1])]

    if verbose:
        print(f"Sorted Sequence by position {pos}:\n{seq}\n\nGaps list: {gaps}\n")

    sub_sequences = []

    value = 0.5
    values = [0.5]
    start = 0
    for idx, i in enumerate(gaps):

        value -= decrement_gap * i
        value = max(value, 0)
        value += (1 - value) * increment2one

        if value < 0.5:
            sub_sequences.append((seq[start:idx + 1], max(values)))
            start = idx + 1
            value = 0.5
            values = [0.5]

        # value = max(value, 0.5)
        values.append(value)

        if verbose:
            print(f"Gap to next token: {i}, total value: {value}")

    if len(values) > 1:
        sub_sequences.append((seq[start:idx + 1], max(values)))

    if verbose:
        print(f"Sub Sequences found:\n{sub_sequences}")
    # tmp = [x[1] for x in sub_sequences]
    #if len(tmp) == 0:
    #    print(f"text aliangment new -->seqScore --> {sequsence}\n{sub_sequences}")
        #raise ValueError("seqScore")
    return (max([x[1] for x in sub_sequences]+[0]), sub_sequences)


def seqScore(sequsence, pos=0, increment2one=0.3, decrement_gap=0.1, verbose=True):
    '''
    Scoring the alignment sequences.
    Every consecutive aligned token increase the alignment score by distanceToOne * increment2one
    This will always leave the score bellow 1

    For each gap (mismatch i a sequence) the score decreases by gap * decrement_gap

    The score minimum is 0.5, If the gaps causes the score to go bellow zero: a new sub sequence is created

    Minimum score (of a single match) is 0.5


    '''

    def remove_alignment_duplicates(seq, pos=1):
        '''
        The alignment mightinclude duplicate usage of a single token. for example:
        [(63, 62, 0.85830885, 'embeding_match'), (64, 65, 1, 'exact_match'), (65, 66, 0.8, 'missing_spaces_match'), (65, 67, 0.8, 'missing_spaces_match')]
        use twice the 65 token in the zero position ( suspect)

        '''
        seen = set()
        unique_list = []

        for tup in seq:
            if tup[pos] not in seen:
                seen.add(tup[pos])
                unique_list.append(tup)

        return unique_list

    def calc_token_value(factor, triplet):
        if type(factor) == float:
            return factor

        tfidf = factor['tfidf']
        token = factor['sus_t'][triplet[0]]

        tmp = tfidf[tfidf['index'] == token]

        if len(tmp) == 0:
            #print(f"Token: {token}, Not in TFIDF")
            val = factor.get('default', 0.0)
        else:
            #val = tmp['all'].iloc[0]
            # 2/8/2025 - claculate Document Frequency Ratio (a.k.a. Document Proportion)
            positiveval = [x for x in tmp.iloc[0].to_list()[:-3] if float(x)>0.0] # tmp.iloc[0].to_list()[:-3] take the value of all columns except: Index, IDF, All
            val = 1-len(positiveval)/(len(tmp.columns)-3)

        #ret = factor.get('i21', 0.0) * (1 - val) ** 4
        ret = factor.get('i21', 0.3) * (1 - val)
        #print(f"Token: {token}, tfifd: {val}, factor: {ret}")

        return ret

    seq = remove_alignment_duplicates(sequsence.copy(), pos=pos)

    seq = sorted(seq, key=lambda x: x[pos])
    _gaps = [x[pos] - y[pos] - 1 for x, y in zip(seq[1:], seq[:-1])]
    gaps = [0] + [x[pos] - y[pos] - 1 for x, y in zip(seq[1:], seq[:-1])]

    if verbose:
        print(f"Sorted Sequence by position {pos}:\n{seq}\n\nGaps list: {gaps}\n")

    ret = (0.0, [])
    value = 0
    max_value = 0
    cur_seq = []
    for g, s in zip(gaps, seq):

        value -= decrement_gap * g
        value = max(value, 0)
        token_value = calc_token_value(increment2one, s)
        value += (1 - value) * token_value

        if value < token_value:
            if max_value > ret[0]:
                ret = (max_value, cur_seq)
            cur_seq = []
            max_value = increment2one
            value = increment2one

        cur_seq.append(s)
        max_value = max(value, max_value)

    if len(cur_seq) > 0 and max_value > ret[0]:
        ret = (max_value, [ (cur_seq,max_value) ])

    return ret


def alignmentScore(alignment_sequences, increment2one=0.3, decrement_gap=0.1, verbose=False, prune=0.0):
    '''
    The input is the smith waterman function data structure
    This function check which of the followinf suspect sequence, source sequence get a better score.
    I takes the best one.

    A single alignment may result multiple sequences in the Smith Waterman function.
    The overall alignment score is the best of all.

    The function recieve a pruning threshold. If a sequence score is bellow the threshold, the sequence is pruned.

    '''
    new_sequences = {}
    scores = [0.0]

    for idx, seq in enumerate(alignment_sequences):
        sus_val, sub_seq_sus = seqScore(seq, pos=0, increment2one=increment2one,
                                        decrement_gap=decrement_gap, verbose=verbose)
        src_val, sub_seq_src = seqScore(seq, pos=1, increment2one=increment2one,
                                        decrement_gap=decrement_gap, verbose=verbose)

        if sus_val < prune and src_val<prune:
            continue

        if sus_val > src_val:
            new_sequences[idx] = {"score": sus_val, "subsequences": sub_seq_sus}
            scores.append(sus_val)
        else:
            new_sequences[idx] = {"score": src_val, "subsequences": sub_seq_src}
            scores.append(src_val)

    return max(scores), new_sequences


def alignmentScore2HTML(sseq, suspect_t, src_t, prune=0.0):
    ''''
    This function visualize the different sequences by creating HTMLs for the source and the suspect
    where each sequence gets a different color.

    '''
    colors = ['a1f0a9', 'a7baf2', 'f2b8f0', 'f5dbb5', '49ab53', '4e6ecc', 'd65cd2', 'd19c4d', '048a12', '022aa1',
              '8c0a88', 'c27604']

    sus_colors = {idx: {"token": x, "html": ta_cstrhex(x)} for idx, x in enumerate(suspect_t)}
    src_colors = {idx: {"token": x, "html": ta_cstrhex(x)} for idx, x in enumerate(src_t)}

    color_idx = 0
    for idx, seq in sseq.items():
        # print(f"Sequence {idx}\n{seq}\n\n")
        if seq['score'] < prune:
            continue
        for subseq in seq['subsequences']:
            # print(f"Sub Sequence: {subseq[0]}\n")
            for triple in subseq[0]:
                sus_colors[triple[0]]['html'] = ta_cstrhex(sus_colors[triple[0]]['token'], colors[color_idx])
                src_colors[triple[1]]['html'] = ta_cstrhex(src_colors[triple[1]]['token'], colors[color_idx])

            color_idx = (color_idx + 1) % len(colors)

    sus_htmp = " ".join([src_colors[x]['html'] for x in src_colors])
    src_html = " ".join([sus_colors[x]['html'] for x in sus_colors])

    return (sus_htmp, src_html)


'''
#-----------------------------------------------------
# Sequences Visualization
#-----------------------------------------------------
'''
def ta_cstr(s, color='black'):
    return "<text style=color:{}>{}</text>".format(color, s)

def ta_cstrhex(s, colorhex='#000000'):
    if str(colorhex[0]) != "#":
        colorhex = f"#{colorhex}"
    return f"<text style=color:{colorhex}>{s}</text>"

def ta_find_color(item, idx, origin, aligned_text):

    at = aligned_text[(aligned_text['match_id'] > 0) & (aligned_text['origin'] == origin)]
    try:
        match = at[at['token'] == item]['match'].iloc[0]
        if match == 1.0:
            return "green"
        elif match >= 0.9:
            return "springgreen"
        elif match > 0:
            return "orange"
        else:
            return "red"
    except Exception:
        return "red"

    return "red"

def ta_find_source_color(idx, aligned_text):
    # at = aligned_text[(aligned_text['globa_source_loc'] == idx)]
    at = [x for x in range(len(aligned_text)) if idx in aligned_text['src_matches'].iloc[x]]

    if len(at) == 0:
        return "red"
    try:
        #match = at['match'].iloc[0]
        match = aligned_text['match'].iloc[at[0]]
        if match == 1.0:
            return "green"
        elif match >= 0.9:
            return "springgreen"
        elif match > 0:
            return "orange"
        else:
            return "red"
    except Exception:
        return "red"
    return "red"


def synopsis_2_html(src_t, df_suspect_alignment):
    suspect_color = {idx: ta_find_color(item, idx, 'suspect', df_suspect_alignment)
                 for idx, item in enumerate(df_suspect_alignment['token'].to_list())}
    suspect_html = [ta_cstr(word, color=suspect_color[idx])
                    for idx, word in enumerate(df_suspect_alignment['token'].to_list())
                    if int(df_suspect_alignment['location'].iloc[idx]) ==df_suspect_alignment['location'].iloc[idx]]
    source_color = {idx: ta_find_source_color(idx, df_suspect_alignment)
                 for idx, item in enumerate(src_t)}
    source_html = [ta_cstr(word, color=source_color.get(idx,"red"))
                for idx, word in enumerate(src_t)]

    return suspect_html, source_html


def synopsis2htmlNew(text1_t, text2_t, align_sequenses):
    def match_color(match):
        if match == 1.0:
            return "green"
        elif match >= 0.9:
            return "springgreen"
        elif match > 0:
            return "orange"
        else:
            return "red"

    suspect_color = {}
    source_color = {}

    for seq in align_sequenses:
        for x in seq: suspect_color[x[0]] = match_color(x[2])
        tmp = [x[0] for x in seq]
        for x in range(min(tmp), max(tmp)):
            if x not in suspect_color: suspect_color[x] = "red"

        for x in seq: source_color[x[1]] = match_color(x[2])
        tmp = [x[1] for x in seq]
        for x in range(min(tmp), max(tmp)):
            if x not in source_color: source_color[x] = "red"

    # for x in range(len(text2_t)):
    #     if x not in source_color: source_color[x] = "gray"

    suspect_html = [ta_cstr(word, color=suspect_color.get(idx, "lightgray")) for idx, word in enumerate(text1_t)]
    source_html = [ta_cstr(word, color=source_color.get(idx, "lightgray")) for idx, word in enumerate(text2_t)]

    return suspect_html, source_html


def synopsis2htmlTable(text1_t, text2_t, align_sequenses):
    def tab_cstr(s, color='black'):
        return f'<font color="{color}">{s}</font>'

    def match_color(match):
        if match == 1.0:
            return "green"
        elif match >= 0.9:
            return "springgreen"
        elif match > 0:
            return "orange"
        else:
            return "red"

    suspect_color = {}
    source_color = {}
    sus_token_belong_2_seq = {}
    scr_token_belong_2_seq = {}

    # Match a color for each token in the suspect and source texts
    # For each token that was aligned between the suspect and source, manage a dictionary
    # which holds which alignemnt sequence that tokens belongs to.
    for idx, seq in enumerate(align_sequenses):
        for x in seq: suspect_color[x[0]] = match_color(x[2])
        tmp = [x[0] for x in seq]
        for x in range(min(tmp), max(tmp) + 1):
            if x not in suspect_color: suspect_color[x] = "red"
            sus_token_belong_2_seq[x] = idx

        for x in seq: source_color[x[1]] = match_color(x[2])
        tmp = [x[1] for x in seq]
        for x in range(min(tmp), max(tmp) + 1):
            if x not in source_color: source_color[x] = "red"
            scr_token_belong_2_seq[x] = idx

    # print(f"sus_token_belong_2_seq: {sus_token_belong_2_seq}")

    # Arange all the suspect's alignment sections in a dictionary: suspect_lines
    # each list element hase two elements: the first is the aligned token of the section with the proper coloring
    # the second is the index of the alignment.
    last_seq = -2
    suspect_line = []
    suspect_lines = []
    for idx, word in enumerate(text1_t):
        if last_seq != sus_token_belong_2_seq.get(idx, -1):
            if last_seq == -1:
                tmp = ""
            else:
                tmp = last_seq
            if suspect_line != []:
                suspect_lines.append((suspect_line, tmp))
            suspect_line = []
            last_seq = sus_token_belong_2_seq.get(idx, -1)
        suspect_line.append(tab_cstr(word, color=suspect_color.get(idx, "lightgray")))
    if len(suspect_line) > 0: suspect_lines.append((suspect_line, sus_token_belong_2_seq.get(idx, "")))

    last_seq = -2
    source_line = []
    source_lines = []
    for idx, word in enumerate(text2_t):
        if last_seq != scr_token_belong_2_seq.get(idx, -1):
            if last_seq == -1:
                tmp = ""

            else:
                tmp = last_seq
            if source_line != []: source_lines.append((source_line, tmp))
            source_line = []
            last_seq = scr_token_belong_2_seq.get(idx, -1)
        source_line.append(tab_cstr(word, color=source_color.get(idx, "lightgray")))
    if len(source_line) > 0: source_lines.append((source_line, scr_token_belong_2_seq.get(idx, "")))

    # print(f"Suspect Lines:\n{suspect_lines}\nSource lines:\n{source_lines}")

    html = '''
            <table style="width:100%; direction: rtl;">
              <tr>
                <th style="width:2%; text-align: center;">#</th>
                <th style="width:48%; text-align: center;"></th>
                <th style="width:2%; text-align: center;">#</th>
                <th style="width:48%; text-align: center;"></th>
              </tr> '''

    suspect_pointer = 0
    src_pointer = 0
    for i in range(len(source_lines) + len(suspect_lines)):
        html += "<tr>"
        sus_tmp = '''<td></td><td ></td>'''
        src_tmp = '''<td></td><td ></td>'''

        # print(f"suspect_pointer: {suspect_pointer} , src_pointer: {src_pointer}")

        if suspect_pointer < len(suspect_lines) and src_pointer < len(source_lines) and suspect_lines[suspect_pointer][
            1] == source_lines[src_pointer][1]:
            sus_tmp = f'''<td>{suspect_lines[suspect_pointer][1]}</td><td>{" ".join(suspect_lines[suspect_pointer][0])}</td>'''
            src_tmp = f'''<td>{source_lines[src_pointer][1]}</td><td>{" ".join(source_lines[src_pointer][0])}</td>'''
            suspect_pointer += 1
            src_pointer += 1


        elif suspect_pointer < len(suspect_lines) and suspect_lines[suspect_pointer][1] == "":
            sus_tmp = f'''<td>{suspect_lines[suspect_pointer][1]}</td><td>{" ".join(suspect_lines[suspect_pointer][0])}</td>'''
            suspect_pointer += 1

        elif src_pointer < len(source_lines) and source_lines[src_pointer][1] == "":
            src_tmp = f'''<td>{source_lines[src_pointer][1]}</td><td>{" ".join(source_lines[src_pointer][0])}</td>'''
            src_pointer += 1

        elif suspect_pointer < len(suspect_lines) and src_pointer < len(source_lines) and \
                suspect_lines[suspect_pointer][1] != "" and source_lines[src_pointer][1] != "":
            sus_tmp = f'''<td>{suspect_lines[suspect_pointer][1]}</td><td>{" ".join(suspect_lines[suspect_pointer][0])}</td><td></td><td ></td></tr>'''
            src_tmp = f'''<tr><td></td><td ></td><td>{source_lines[src_pointer][1]}</td><td>{" ".join(source_lines[src_pointer][0])}</td>'''
            suspect_pointer += 1
            src_pointer += 1

        if sus_tmp != '''<td></td><td ></td>''' or src_tmp != '''<td></td><td ></td>''':
            html += sus_tmp + src_tmp + "</tr>"

    return html

