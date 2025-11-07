
import numpy as np


class HebAnalysis():
    '''
    Class to send to the TRAigner as llm parameter.
    The alignment algorithm will call the compare method to either convert a token to base form or to 
    remove prefixes from token.
    
    '''
    def __init__(self, txt=None, mpath=None, compare_method="base"):
        if mpath:
            self.model_path = mpath
        else:
            self.model_path = ""
        self.seg_model = None
        self.seg_tokenizer = None
        self.lex_model = None
        self.lex_tokenizer = None
        self.compare_method = compare_method
        self.resources = {}
        if txt:
            self._prepare_resources(txt)

    def _prepare_resources(self,txt):
        
        if txt:
            res = self.compare(txt)
            tmp = {x:y for x,y in zip(txt.split(" "), res.split(" "))}
            self.resources = self.resources | tmp
        else:
            self.resources = {}
        
    
    def _load_segmodel(self):
        
        from transformers import AutoModel, AutoTokenizer
        
        self.seg_tokenizer = AutoTokenizer.from_pretrained(f"{self.model_path}/dseg/")
        self.seg_model = AutoModel.from_pretrained(f"{self.model_path}/dseg/",
                                                   trust_remote_code=True)

    def _load_lexmodel(self):
        from transformers import AutoModel, AutoTokenizer

        self.lex_tokenizer = AutoTokenizer.from_pretrained(f"{self.model_path}/dlex/")
        self.lex_model = AutoModel.from_pretrained(f"{self.model_path}/dlex/",
                                                   trust_remote_code=True)

    def prefix_detection(self, sentence):
        if self.seg_model is None:
            self._load_segmodel()
        pred = self.seg_model.predict([sentence], self.seg_tokenizer)
        tmp = [x[-1] for x in pred[0] if x[0] not in ['[CLS]', '[SEP]']]
        return " ".join(tmp)

    def base_form(self, sentence, parsed=True):
        if self.lex_model is None:
            self._load_lexmodel()
        nf = self.lex_model.predict([sentence], self.lex_tokenizer)
        if parsed:
            res = []
            for t in nf[0]:
                if t[1] == '[BLANK]':
                    res.append(t[0])
                else:
                    res.append(t[1])
            nf = " ".join(res)

        return nf

    def compare(self, sentence, parsed=True):
        if sentence in self.resources:
            return self.resources[sentence]
        if self.compare_method == "base":
            ret =  self.base_form(sentence)
        else:
            ret =  self.prefix_detection(sentence)
        #self.resources[sentence] = ret
        return ret



class EmbeddingRapper():
    def __init__(self, model_path=None):
        self.models = {}
        if model_path:
            self._load_model(model_path)

    def _load_model(self,path, name='default'):
        if path.endswith("kv"):
            from gensim.models import KeyedVectors
            self.models[name] = {"type": "gensim_kv", "model": KeyedVectors.load(path, mmap='r')}
            
        elif path.endswith("ft"):
            from gensim.models import FastText
            self.models[name] = {"type": "gensim", "model": FastText.load(path)}
    
        elif path.endswith("bin"):
            import fasttext
            self.models[name] = {"type": "fasttext", "model": fasttext.load_model(path)}

    def get_vector(self, text, model_name= 'default'):
        
        model = self.models.get(model_name, None)
        if model is None:
            return -100
        if model['type']=="gensim_kv":
            return model['model'].get_vector(text)
        elif model['type']=="gensim":
            return model['model'].wv[text]
        elif model['type'] == "fasttext":
            return model['model'].get_word_vector(text)
        else:
            return -1

    def similarity(self,w1,w2, model_name= 'default'):

        def cosin(v,w):
            return np.dot(v,w)/(np.linalg.norm(v)*np.linalg.norm(w))
        
        if model_name not in self.models:
            return -1 , "Models were not initiated"
        try:
            vw1= self.get_vector(w1, model_name= model_name)
            
        except Exception as e:
            print(e)
            return -1, "{} missing in dictionary".format(w1)
        try:
            vw2= self.get_vector(w2, model_name= model_name)
        except Exception:
            print(e)
            return -1, "{} missing in dictionary".format(w2)
        
        return cosin(vw1,vw2), "OK"


