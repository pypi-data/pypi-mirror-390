
# Introduction

This package contains the Python package to run ChiKhaPo. Our benchmark is described in [ChiKhaPo: A Large-Scale Multilingual Benchmark for Evaluating Lexical Comprehension and Generation in Large Language Models](https://www.arxiv.org/abs/2510.16928).
ChiKhaPo contains 4 word-level tasks, with two directions each (comprehension and generation), intended to benchmark generative models for lexical competence. The processed lexicon data that our tasks rely on can be found on [HuggingFace](https://huggingface.co/datasets/ec5ug/chikhapo) and will be automatically downloaded as needed by this package.

# Setup

**Huggingface Token**
To access our datasets, you will need a HuggingFace token. This can be done by entering the following line in command line

```
export HF_TOKEN="HF_XXXXXXXXXXXXX"
```

This access token will be read in as an environment variable.

For more details, go to this [link](https://medium.com/@manyi.yim/store-your-hugging-face-user-access-token-in-an-environment-variable-fee94fcb58fc)

**Dataset Access**
We draw on [FLORES+](https://huggingface.co/datasets/openlanguagedata/flores_plus) and [GLOTLID](https://huggingface.co/datasets/cis-lmu/glotlid-corpus), Huggingface datasets that require users to apply for access. Please visit both links to apply for access.

**Downloads**
We use WordNet to verify synonymy. You will need to download it. This can be done by:

```
import nltk
nltk.download("wordnet")
```

# Tasks

The 4 tasks (referenced by their task keys) are as follows:

* ```word_translation```: Prompts LLM directly for word translation (2746 languages)
* `word_translation_with_context`: Prompts LLM to translate a word given monolingual context.
* (Coming soon to this package) `translation_conditioned_lm`: Softly measures LLM capability to understand or generate a word in a natural MT setting.
* (Coming soon to this package) `bow_mt`: Word-level MT evaluation.

Each task has two subtasks corresponding to two directions (`X_to_eng` testing comprehension and `eng_to_X` testing generation) that tests the models abilities to comprehend or generate a list of words respectively, in various settings. See more details on the description and evaluation procedure for each task and direction in the paper.  



# Getting data per subtask

Instantiate an object of the `TaskFeeder` class for your task:
```
from chikhapo import TaskFeeder
wt_feeder = TaskFeeder("word_translation")
wtwc_feeder = TaskFeeder("word_translation_with_context")
```

This object allows you to obtain a list of language pairs available per task and direction, and to obtain subtask data for each language pair. 

**Get the set of languages available**:

Our lexicons are English-centric, and may either be `xxx_eng` (used for `comprehension` evaluation) or `eng_xxx` (used for `generation` evaluation). 

Retrieve the set of languages available for a particular task as follows, specifying the direction (`X_to_eng`, `eng_to_X` or `None`).

Setting `DIRECTION=None` retrieves language pairs in both directions.
```
word_translation_language_pairs = wt_feeder.get_lang_pairs(DIRECTION="X_to_eng")
```

**Obtain the task data for each language pair**:

Obtain the task data for a particular language pair as follows. The `lite` version of our task datasets contain at most 300 words per language pair and direction, and can be used for faster evaluation. 

```
word_translation_data = wt_feeder.get_data_for_lang_pair(lang_pair="spa_eng", lite=True)
```
This method returns a dictionary. The dictionary keys are source-language words, and each key’s value is a list of translations in the target language.


**Retrieve default formatted prompts for each task**:

We provide a default prompt per task, and a formatter that returns a list of ready-to-use task prompts (one per input) for the task and language pair.

```
word_translation_prompts = wt_feeder.get_prompts_for_lang_pair(lang_pair="spa_eng", lite=True)
```

You may also use your own custom prompt.


# Evaluation

Broadly, each task evaluation computes word scores for each word for that task and language pair. We compute a language score as an aggregate over the word scores of that language, and the task score as an aggregate over language scores.

You will need to run inference with your LLM on the prompts from the previous step to get its responses. 

Instantiate the task evaluator as follows:

```
from chikhapo import Evaluator
wt_evaluator = Evaluator("word_translation")
```

To compute a language pair score (such as `spa_eng`), specify the path to the output file containing the output file for that language pair. The evaluation requires a particular JSON format for the responses of your model (see **Output File Formats** for more information). The direction is set automatically from the required fields in the JSON. 
```
wt_evaluator.evaluate(file_path="path/to/file/file.json")
lang_score = wt_evaluator.get_lang_score()
```

The benchmark reports aggregate language scores (or language family scores) for each task and direction. 

Features coming soon
* retrieve language family information for languages `get_lang_family`
* Aggregate your language scores and language family scores. 

# Output file formats

We expect model predictions to be placed into a JSON file with a particular format depending on task. 

## Word Translation

This task requires the model to output the translation of single words. For example, we may have:
```
Prompt:
Translate the following word from Magahi to English. Respond with a single word.

Word:निर्णय
Translation:
---
Raw Model Output:
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>Translate the following word from Magahi to English. Respond with a single word.

Word:निर्णय
Translation:<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>decision
---
```
The parsed model output for this source word would be `decision`.

We expect outputs to be placed in a JSON file with the following format:

```
{
    "src_lang": {source_language},
    "tgt_lang": {target_language},
    "data": [
        {
            "word": {word_1_to_translate},
            "prediction": {model_translation_for_word_1}
        },
        {
            "word": {word_2_to_translate},
            "prediction": {model_translation_for_word_2}
        },
        {
            "word": {word_3_to_translate},
            "prediction": {model_translation_for_word_3}
        }
    ]
}
```
For an example, please see [tests/raw_test_data/wt_equivalence_spa_eng.json](tests/raw_test_data/wt_equivalence_spa_eng.json)
## Word Translation with Word Context
The output format is identical to that used in Word Tranlslation.



# Cite
If you use this data or code, please cite
```
@article{chang2025chikhapo,
  title={ChiKhaPo: A Large-Scale Multilingual Benchmark for Evaluating Lexical Comprehension and Generation in Large Language Models},
  author={Chang, Emily and Bafna, Niyati},
  journal={arXiv preprint arXiv:2510.16928},
  year={2025}
}
```
