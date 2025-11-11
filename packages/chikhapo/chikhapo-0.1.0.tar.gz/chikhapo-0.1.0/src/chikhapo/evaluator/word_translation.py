from .base import BaseEvaluator
from chikhapo.utils.parsing import clean_string, convert_list_of_entries_to_dictionary

class WordTranslationEvaluator(BaseEvaluator):
    def score_each_word(self):
        for word in self.xword_class_pred:
            exact_match = len(self.xword_class_pred[word].get("exact_match", []))
            inflection = len(self.xword_class_pred[word].get("inflection", []))
            substring = len(self.xword_class_pred[word].get("substring", []))
            inflection_within_substring = len(self.xword_class_pred[word].get("inflection_within_substring", []))
            synonym = len(self.xword_class_pred[word].get("synonym", []))
            # inflected_synonym = len(word_type_data[word].get("inflected_synonym", []))
            # correct = exact_match + inflection + substring + inflection_within_substring + synonym + inflected_synonym
            correct = exact_match + inflection + substring + inflection_within_substring + synonym
            
            echo = len(self.xword_class_pred[word].get("echo", []))
            outputted_in_source_language = len(self.xword_class_pred[word].get("outputted_in_source_language", []))
            gibberish = len(self.xword_class_pred[word].get("gibberish", []))
            incorrect = echo + outputted_in_source_language + gibberish
            
            total = correct + incorrect
            if total==0:
                self.word_scores[word] = 0
            else:
                self.word_scores[word] = correct / total

    def evaluate(self, file_path):
        model_output_file = self.read_prediction_file(file_path)
        src_lang = model_output_file["src_lang"]
        tgt_lang = model_output_file["tgt_lang"]
        if src_lang == "all" or tgt_lang == "all":
            raise Exception("This function can only evaluate data from one translation. You will have to split your data by language pair and evaluate each split separately.")
        if tgt_lang == "eng":
            self.DIRECTION = "X_to_eng"
        else:
            self.DIRECTION = "eng_to_X"
        data = model_output_file["data"]
        list_of_entries = self.loader.get_omnis_lexicon_subset(f"{src_lang}_{tgt_lang}")
        lexicon = convert_list_of_entries_to_dictionary(list_of_entries)
        for output in data:
            self.validate_output(output)
            word_to_translate = clean_string(output["word"])
            if word_to_translate not in lexicon.keys():
                continue
            gt_answers = lexicon[word_to_translate]
            prediction = clean_string(output["prediction"])
            if self.is_exact_match(prediction, gt_answers):
                classification_type = "exact_match"
            elif self.is_inflection(prediction, gt_answers):
                classification_type = "inflection"
            elif self.is_substring(prediction, gt_answers):
                classification_type = "substring"
            elif self.is_inflection_within_substring(prediction, gt_answers):
                classification_type = "inflection_within_substring"
            elif self.is_synonym(prediction, gt_answers):
                classification_type = "synonym"
            elif word_to_translate == prediction:
                classification_type = "echo"
            elif prediction in lexicon.keys():
                classification_type = "outputted_in_source_language"
            else:
                classification_type = "gibberish"

            if self.DIRECTION=="X_to_eng":
                x_words = [word_to_translate]
            elif self.DIRECTION=="eng_to_X":
                x_words = gt_answers # -> X
            
            for x_word in x_words: # allows for synonymy
                if x_word not in self.xword_class_pred:
                    self.xword_class_pred[x_word] = {}
                if classification_type not in self.xword_class_pred[x_word]:
                    self.xword_class_pred[x_word][classification_type] = []
                self.xword_class_pred[x_word][classification_type].append(prediction)
        self.score_each_word()
        self.score_language() # used to be self.score_each_word_type()