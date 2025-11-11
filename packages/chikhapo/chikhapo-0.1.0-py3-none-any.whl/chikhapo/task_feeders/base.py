from abc import abstractmethod
import random
from chikhapo import Loader

class BaseTaskFeeder:
    """
    Base class for all task feeders
    """
    def __init__(self):
        self.loader = Loader()
    
    def get_random_sample(self, d, sample_size=300):
        if len(d) <= sample_size:
            return d
        # random.seed(42)
        # random.shuffle(list_to_sample)
        # return list_to_sample[:sample_size]
        items = list(d.items())
        random.seed(42)
        sampled = random.sample(items, min(sample_size, len(items)))
        return dict(sampled)

    @abstractmethod
    def get_lang_pairs(self, DIRECTION=None):
        pass

    @abstractmethod
    def get_data_for_lang_pair(self, lang_pair, lite=True):
        pass

    @abstractmethod
    def get_prompts_for_lang_pair(self, lang_pair, lite=True):
        pass