from .loader import Loader
from .evaluator import Evaluator, WordTranslationEvaluator
from .task_feeders import TaskFeeder, WordTranslationFeeder, WordTranslationWithContextFeeder

__version__ = "0.1.0"

__all__ = [
    'Loader',
    'Evaluator',
    'WordTranslationEvaluator'
    'TaskFeeder',
    'WordTranslationFeeder',
    'WordTranslationWithContextFeeder',
]