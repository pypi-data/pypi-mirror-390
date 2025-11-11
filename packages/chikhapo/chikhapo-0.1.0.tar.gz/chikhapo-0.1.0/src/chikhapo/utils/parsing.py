from nltk.corpus import wordnet as wn
import unicodedata
from collections import defaultdict

def is_punctuation(char):
    return unicodedata.category(char).startswith('P')

def strip_punctuation(word):
    chars = list(word)
    while chars and is_punctuation(chars[0]):
        chars.pop(0)
    while chars and is_punctuation(chars[-1]):
        chars.pop()
    return ''.join(chars)

def clean_string(text):
    text = text.lower()
    text = text.strip()
    text = strip_punctuation(text)
    text = text.strip()
    return text

def preprocess_lemma_names(lemmas):
    return [lemma.name() for lemma in lemmas]

def lemmatize_terms(list_of_terms):
    lemma_names = set()
    for term in list_of_terms:
        synsets_of_term = wn.synsets(term)
        for synset_of_term in synsets_of_term:
            lemmas_of_term = synset_of_term.lemmas()
            lemma_names.update(preprocess_lemma_names(lemmas_of_term))
    return lemma_names

def convert_list_of_entries_to_dictionary(list_of_entries):
    new_dictionary = defaultdict(list)
    for entry in list_of_entries:
        new_dictionary[entry["source_word"]] = entry["target_translations"]
    return new_dictionary