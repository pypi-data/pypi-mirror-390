from huggingface_hub import login
from datasets import load_dataset, get_dataset_config_names
import os
# from languages import get_language_from_pair

login(token=os.environ.get("HF_TOKEN"))

class Loader:
    def __init__(self):
        self.flores_plus_hf_path = "openlanguagedata/flores_plus"
        self.glotlid_hf_path = "cis-lmu/glotlid-corpus"
        self.omnis_lexicons_hf_path = "ec5ug/chikhapo"

    def get_flores_subset_names(self):
        return get_dataset_config_names(self.flores_plus_hf_path)

    def get_flores_subset(self, name, split):
        if name not in self.get_flores_subset_names():
            raise Exception("Language not found in FLORES+")
        return load_dataset(self.flores_plus_hf_path, name=name, split=split)

    def get_glotlid_subset_names(self):
        return get_dataset_config_names(self.glotlid_hf_path)
    
    def get_glotlid_subset(self, name):
        if name not in self.get_glotlid_subset_names():
            raise Exception("Laguage not found in GLOTLID")
        return load_dataset(self.glotlid_hf_path, name=name, split="train")
    
    def get_omnis_lexicon_subset_names(self):
        return get_dataset_config_names(self.omnis_lexicons_hf_path)

    # def get_omnis_lexicon_isos(self):
    #     lang_pairs = self.get_omnis_lexicon_subset_names()
    #     isos = set()
    #     for lang_pair in lang_pairs:
    #         isos.add(get_language_from_pair(lang_pair))
    #     return isos

    def get_omnis_lexicon_subset(self, name):
        if name not in self.get_omnis_lexicon_subset_names():
            raise Exception("Language pair not found in lexicons")
        return load_dataset(self.omnis_lexicons_hf_path, name=name, split="train")
    