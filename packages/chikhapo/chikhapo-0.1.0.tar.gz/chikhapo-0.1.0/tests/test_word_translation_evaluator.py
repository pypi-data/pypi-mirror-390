# import json
# from unittest.mock import patch
# import pprint
# import pytest

# from chikhapo import Evaluator

# @pytest.fixture
# def evaluator_instance():
#     return Evaluator()

# # should try to read invalid files
# def test_improper_file_extension(evaluator_instance, fs):
#     fs.create_file("tmp/wrong_file_extension.txt", contents="lorem ipsum")
#     with pytest.raises(Exception, match="not a JSON file"):
#         evaluator_instance.read_prediction_file("tmp/wrong_file_extension.txt")

# def test_missing_source_language(evaluator_instance, fs):
#     fs.create_file("tmp/missing_source_language.json", contents=json.dumps({
#         'tgt_lang': 'eng',
#         'data': [{'word': 'a', 'prediction': 'a'}]})
#     )
#     with pytest.raises(Exception, match="The key \"src_lang\" is not specified."):
#         evaluator_instance.read_prediction_file("tmp/missing_source_language.json")

# #################### if i have time i will finish out the unit tests for edge cases ###################
# def test_exact_match_spa_eng(evaluator_instance, fs):
#     fs.create_file("tmp/exact_match.json", contents=json.dumps({
#         'src_lang': 'spa',
#         'tgt_lang': 'eng',
#         'data': [{'word': 'gatos', 'prediction': 'cat.'}]})
#     )
#     fake_lexicon = [
#         {"source_word": "escribieron", "target_translations": ["write"], "src_lang":"spa", "tgt_lang": "eng"},
#         {"source_word": "feliz", "target_translations": ["happy"], "src_lang":"spa", "tgt_lang": "eng"},
#         {"source_word": "gatos", "target_translations": ["cat"], "src_lang":"spa", "tgt_lang": "eng"},
#         {"source_word": "perro", "target_translations": ["dog"], "src_lang":"spa", "tgt_lang": "eng"},
#         {"source_word": "libro", "target_translations": ["book"], "src_lang":"spa", "tgt_lang": "eng"},
#         {"source_word": "ventana", "target_translations": ["window"], "src_lang":"spa", "tgt_lang": "eng"}
#     ]
#     with patch.object(evaluator_instance.loader, "get_omnis_lexicon_subset", return_value=fake_lexicon):
#         evaluator_instance.evaluate_word_translation("tmp/exact_match.json")
#     assert evaluator_instance.xword_class_pred["gatos"]["exact_match"] == ["cat"]
#     assert evaluator_instance.word_scores["gatos"] == 1
#     assert evaluator_instance.lang_score == 100

# def test_equivalence_spa_eng(evaluator_instance, fs):
#     fs.create_file(
#         "tmp/equivalence.json", contents=json.dumps({
#         'src_lang': 'spa',
#         'tgt_lang': 'eng',
#         'data': [
#             {'word': 'feliz', 'prediction': 'qwerty.'},
#             {'word': 'perro', 'prediction': 'hound.'},
#             {'word': 'escribieron', 'prediction': 'wrote.'},
#             {'word': 'libro', 'prediction': 'libro.'},
#             {'word': 'gatos', 'prediction': 'a cat.'},
#             {'word': 'ventana', 'prediction': 'window.'}
#         ]
#     }))
#     fake_lexicon = [
#         {"source_word": "escribieron", "target_translations": ["write"]},
#         {"source_word": "feliz", "target_translations": ["happy"]},
#         {"source_word": "gatos", "target_translations": ["cat"]},
#         {"source_word": "perro", "target_translations": ["dog"]},
#         {"source_word": "libro", "target_translations": ["book"]},
#         {"source_word": "ventana", "target_translations": ["window"]}
#     ]
#     with patch.object(evaluator_instance.loader, "get_omnis_lexicon_subset", return_value=fake_lexicon):
#         evaluator_instance.evaluate_word_translation("tmp/equivalence.json")
#     assert len(evaluator_instance.xword_class_pred) == 6
#     assert evaluator_instance.lang_score == 66.66667

# def test_inflection_eng_spa(evaluator_instance, fs):
#     fs.create_file("tmp/inflection.json", contents=json.dumps({
#         'src_lang': 'eng',
#         'tgt_lang': 'spa',
#         'data': [{'word': 'Egyptian', 'prediction': 'Egipto.'}]})
#     )
#     fake_lexicon = [
#         {"source_word": "egyptian", "target_translations": ["egipcio", "de egipto", "egipcia", "egipciaco", "egipcíaco", "egipciano", "lengua egipcia"], "src_lang": "eng", "tgt_lang": "spa"},
#     ]
#     with patch.object(evaluator_instance.loader, "get_omnis_lexicon_subset", return_value=fake_lexicon):
#         evaluator_instance.evaluate_word_translation("tmp/inflection.json")
#     assert evaluator_instance.xword_class_pred["egipcia"]["inflection"] == ["egipto"]
#     assert evaluator_instance.word_scores["egipcia"] == 1
#     assert evaluator_instance.lang_score == 100

import json
import os
import tempfile
import unittest
from unittest.mock import patch
from chikhapo import Evaluator


class TestWordTranslationEvaluator(unittest.TestCase):
    """Unit tests for the Evaluator class."""

    def setUp(self):
        """Set up a temporary directory and Evaluator instance."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = self.tmp_dir.name
        self.evaluator = Evaluator("word_translation")

    def tearDown(self):
        """Clean up the temporary directory after tests."""
        self.tmp_dir.cleanup()

    def create_file(self, filename, contents):
        """Helper to write JSON or text files in the temporary directory."""
        path = os.path.join(self.tmp_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)
        return path

    def test_improper_file_extension(self):
        """Should raise an Exception when file is not a JSON file."""
        path = self.create_file("wrong_file_extension.txt", "lorem ipsum")
        with self.assertRaises(Exception) as ctx:
            self.evaluator.read_prediction_file(path)
        self.assertIn("not a JSON file", str(ctx.exception))

    def test_missing_source_language(self):
        """Should raise an Exception when src_lang is missing."""
        path = self.create_file(
            "missing_source_language.json",
            json.dumps({
                "tgt_lang": "eng",
                "data": [{"word": "a", "prediction": "a"}],
            }),
        )
        with self.assertRaises(Exception) as ctx:
            self.evaluator.read_prediction_file(path)
        self.assertIn('The key "src_lang" is not specified.', str(ctx.exception))

    def test_no_prediction(self):
        path = self.create_file(
            "missing_prediction_in_entry.json",
            json.dumps({
                "src_lang": "spa",
                "tgt_lang": "eng",
                "data": [{"word": "a", "prediction": "a"},
                         {"word": "b"}],
            }),
        )
        with self.assertRaises(Exception) as ctx:
            self.evaluator.read_prediction_file(path)
        self.assertIn("prediction was not specified in", str(ctx.exception))

    def test_exact_match_spa_eng(self):
        """Should correctly classify an exact match between spa and eng."""
        path = self.create_file(
            "exact_match.json",
            json.dumps({
                "src_lang": "spa",
                "tgt_lang": "eng",
                "data": [{"word": "gatos", "prediction": "cat."}],
            }),
        )
        fake_lexicon = [
            {"source_word": "escribieron", "target_translations": ["write"], "src_lang": "spa", "tgt_lang": "eng"},
            {"source_word": "feliz", "target_translations": ["happy"], "src_lang": "spa", "tgt_lang": "eng"},
            {"source_word": "gatos", "target_translations": ["cat"], "src_lang": "spa", "tgt_lang": "eng"},
            {"source_word": "perro", "target_translations": ["dog"], "src_lang": "spa", "tgt_lang": "eng"},
            {"source_word": "libro", "target_translations": ["book"], "src_lang": "spa", "tgt_lang": "eng"},
            {"source_word": "ventana", "target_translations": ["window"], "src_lang": "spa", "tgt_lang": "eng"},
        ]
        with patch.object(self.evaluator.loader, "get_omnis_lexicon_subset", return_value=fake_lexicon):
            self.evaluator.evaluate(path)
        self.assertEqual(self.evaluator.xword_class_pred["gatos"]["exact_match"], ["cat"])
        self.assertEqual(self.evaluator.word_scores["gatos"], 1)
        self.assertEqual(self.evaluator.lang_score, 100)

    def test_equivalence_spa_eng(self):
        """Should correctly evaluate partial equivalence between spa and eng."""
        path = self.create_file(
            "equivalence.json",
            json.dumps({
                "src_lang": "spa",
                "tgt_lang": "eng",
                "data": [
                    {"word": "feliz", "prediction": "qwerty."},
                    {"word": "perro", "prediction": "hound."},
                    {"word": "escribieron", "prediction": "wrote."},
                    {"word": "libro", "prediction": "libro."},
                    {"word": "gatos", "prediction": "a cat."},
                    {"word": "ventana", "prediction": "window."},
                ],
            }),
        )
        fake_lexicon = [
            {"source_word": "escribieron", "target_translations": ["write"]},
            {"source_word": "feliz", "target_translations": ["happy"]},
            {"source_word": "gatos", "target_translations": ["cat"]},
            {"source_word": "perro", "target_translations": ["dog"]},
            {"source_word": "libro", "target_translations": ["book"]},
            {"source_word": "ventana", "target_translations": ["window"]},
        ]
        with patch.object(self.evaluator.loader, "get_omnis_lexicon_subset", return_value=fake_lexicon):
            self.evaluator.evaluate(path)
        self.assertEqual(len(self.evaluator.xword_class_pred), 6)
        self.assertAlmostEqual(self.evaluator.lang_score, 66.66667, places=3)

    def test_inflection_eng_spa(self):
        """Should correctly identify inflectional relationships."""
        path = self.create_file(
            "inflection.json",
            json.dumps({
                "src_lang": "eng",
                "tgt_lang": "spa",
                "data": [{"word": "Egyptian", "prediction": "Egipto."}],
            }),
        )

        fake_lexicon = [
            {
                "source_word": "egyptian",
                "target_translations": [
                    "egipcio","de egipto","egipcia","egipciaco","egipcíaco","egipciano","lengua egipcia",
                ],
                "src_lang": "eng",
                "tgt_lang": "spa",
            }
        ]
        with patch.object(self.evaluator.loader, "get_omnis_lexicon_subset", return_value=fake_lexicon):
            self.evaluator.evaluate(path)

        self.assertEqual(self.evaluator.xword_class_pred["egipcia"]["inflection"], ["egipto"])
        self.assertEqual(self.evaluator.word_scores["egipcia"], 1)
        self.assertEqual(self.evaluator.lang_score, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
