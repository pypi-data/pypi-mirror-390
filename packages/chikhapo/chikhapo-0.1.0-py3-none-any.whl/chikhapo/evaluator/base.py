from abc import abstractmethod
from collections import defaultdict
import json
from fuzzywuzzy import fuzz
import re
import statistics

from chikhapo import Loader
from chikhapo.utils.parsing import lemmatize_terms
from chikhapo.utils.constants import min_similarity_score

class BaseEvaluator:
    def __init__(self):
        self.loader = Loader()
        self.DIRECTION = None
        self.xword_class_pred = {} # used to be self.model_alignments
        self.word_scores = {}
        self.lang_score = -1
    
    def get_lang_score(self):
        return self.lang_score
    
    def read_prediction_file(self, file_path):
        if not file_path.endswith("json"):
            raise Exception("The file you provided is not a JSON file. Please input the path to a JSON file")
        with open(file_path, "r") as f:
            model_output_file = json.load(f)
        if "src_lang" not in model_output_file.keys():
            raise Exception("The key \"src_lang\" is not specified. Please specify the key to the source language.")
        if not isinstance(model_output_file["src_lang"], str):
            raise Exception("The source language should be specified as a string.")
        if "tgt_lang" not in model_output_file.keys():
            raise Exception("The key \"tgt_lang\" is not specified. Please specify the key to the target language.")
        if not isinstance(model_output_file["tgt_lang"], str):
            raise Exception("The target language should be specified as a string.")
        if "data" not in model_output_file.keys():
            raise Exception("The key \"data\" is not specified. Please specify the key to data.")
        if not isinstance(model_output_file["data"], list):
            raise Exception("The data you provided does not exist as a list. Please specify the data as a list")
        for entry in model_output_file["data"]:
            if "prediction" not in entry:
                raise Exception(f"A prediction was not specified in {entry}")
        return model_output_file
    
    # def convert_list_of_entries_to_dictionary(self, list_of_entries):
    #     new_dictionary = defaultdict(list)
    #     for entry in list_of_entries:
    #         new_dictionary[entry["source_word"]] = entry["target_translations"]
    #     return new_dictionary

    def score_language(self): # used to be score_each_word_type
        word_scores = list(self.word_scores.values())
        if len(word_scores) == 0:
            self.lang_score = 0
        else:
            self.lang_score = round(statistics.mean(word_scores) * 100, 5)
            
    def is_apologetic(self, text):
        text = text.lower()
        return "i'm sorry" in text or "sorry, i cannot" in text

    def no_translation(self, text):
        text = text.lower()
        return "cannot find a translation" in text or "can't find a translation" in text or "no translation" in text or "cannot answer" in text
    
    def is_uncertain(self, text):
        text = text.lower()
        return "i'm not sure" in text or "i have no idea" in text
        
    def de_facto_no_translation(self, text):
        return self.is_apologetic(text) or self.no_translation(text) or self.is_uncertain(text)
    
    def is_exact_match(self, pred, gt_answers):
        for gt_answer in gt_answers:
            if pred == gt_answer:
                return True
        return False

    def is_inflection(self, prediction, gt_answers):
        # ans: ["preguntos"] | prediction: "preguntas"
        if self.de_facto_no_translation(prediction):
            return False
        for ans in gt_answers:
            similarity_score = fuzz.ratio(prediction, ans)
            if similarity_score >= min_similarity_score:
                return True
        return False

    def findWholeWord(self, w):
        return re.compile(r'\b({0})\b'.format(re.escape(w)), flags=re.IGNORECASE).search

    def is_substring(self, prediction, gt_answers):
        # ans: ['good mornings'] | prediction: 'good morning' <-- pure substring
        if self.de_facto_no_translation(prediction):
            return False
        for ans in gt_answers:
            if self.findWholeWord(ans)(prediction):
                return True
        return False

    def is_inflection_within_substring(self, prediction, gt_answers):
        # ans: ['tooths'] | prediction: 'the answer is tooth' <-- an inflection within a string
        if self.de_facto_no_translation(prediction):
            return False
        words_in_prediction = prediction.split()
        for ans in gt_answers:
            for word in words_in_prediction:
                similarity_score = fuzz.ratio(word, ans)
                if similarity_score >= min_similarity_score:
                    return True
        return False

    def is_synonym(self, prediction, gt_answers):
        # ans: ['tooth'] | prediction: "the answer is incisor" <- a 'synonym' within a string
        # ans: ["dog"] | prediction: "canine"
        if self.DIRECTION != "X_to_eng":
            return False
        if self.de_facto_no_translation(prediction):
            return False
        if len(prediction.split()) > 1:
            list_of_predictions = [prediction] + prediction.split()
        else:
            list_of_predictions = [prediction]
        lemma_names_of_pred = lemmatize_terms(list_of_predictions)
        lemma_names_of_gt = lemmatize_terms(gt_answers)
        # print(prediction, lemma_names_of_gt, lemma_names_of_pred)
        if lemma_names_of_pred & lemma_names_of_gt:
            return True
        return False

    def validate_output(self, elem):
        if "word" not in elem.keys():
            raise Exception(f"One of data points you provided {elem} does not have the word to translate specified. Please take another look at the file you want us to translate and make sure the list elements of the data field are formatted correctly.")
        if "prediction" not in elem.keys():
            raise Exception(f"One of data points you provided {elem} does not have the a (parsed) model prediction to evaluate on. Please take another look at the file you want us to translate and make sure the list elements of the data field are formatted correctly.")
        
    @abstractmethod
    def score_each_word(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass