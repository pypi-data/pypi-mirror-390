from .word_translation import WordTranslationEvaluator

def Evaluator(task_name):
    task_map = {
        "word_translation": WordTranslationEvaluator,
        "word_translation_with_context": WordTranslationEvaluator
    }

    if task_name not in task_map:
        raise ValueError(
            f"Unknown task: {task_name}. "
            f"Available tasks: {list(task_map.keys())}"
        )
    
    return task_map[task_name]()