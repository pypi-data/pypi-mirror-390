import unittest
from chikhapo import TaskFeeder

class TestWordTranslationWithContextTaskFeeder(unittest.TestCase):
    def setUp(self):
        self.feeder = TaskFeeder("word_translation_with_context")

    def test_get_word_translation_with_context_data_for_lang_pair_more_than_300_word_sentence_lite_true(self):
        words_sentences_translations = self.feeder.get_data_for_lang_pair("avn_Latn_eng")
        self.assertIsInstance(words_sentences_translations, dict)
        self.assertEqual(len(words_sentences_translations), 300)
        self.assertTrue(all(isinstance(k, tuple)) for k in words_sentences_translations.keys())
        self.assertTrue(all(isinstance(v, list) for v in words_sentences_translations.values()))
        # self.assertTrue(all(isinstance(w, tuple) for w in list_of_words_sentences))
        # self.assertEqual(len(list_of_words_sentences[0]), 2)

    def test_get_word_translation_with_context_data_for_lang_pair_more_than_300_word_sentence_lite_false(self):
        words_sentences_translations = self.feeder.get_data_for_lang_pair("avn_Latn_eng", lite=False)
        # self.assertIsInstance(list_of_words_sentences, list)
        self.assertIsInstance(words_sentences_translations, dict)
        self.assertGreater(len(words_sentences_translations), 300)
        self.assertTrue(all(isinstance(k, tuple)) for k in words_sentences_translations.keys())
        self.assertTrue(all(isinstance(v, list) for v in words_sentences_translations.values()))
        # self.assertTrue(all(isinstance(w, tuple) for w in list_of_words_sentences))
        # self.assertEqual(len(list_of_words_sentences[0]), 2)

    def test_get_word_translation_with_context_prompts_for_lang_pair_more_than_300_word_sentence_lite_true(self):
        list_of_prompts = self.feeder.get_prompts_for_lang_pair("avn_Latn_eng")
        self.assertIsInstance(list_of_prompts, list)
        self.assertEqual(len(list_of_prompts), 300)
        self.assertTrue(all(isinstance(w, str) for w in list_of_prompts))

    def test_get_word_translation_with_context_prompts_for_lang_pair_more_than_300_word_sentence_lite_false(self):
        list_of_prompts = self.feeder.get_prompts_for_lang_pair("avn_Latn_eng")
        self.assertIsInstance(list_of_prompts, list)
        self.assertEqual(len(list_of_prompts), 300)
        self.assertTrue(all(isinstance(w, str) for w in list_of_prompts))
    
    def test_get_lang_pairs(self):
        lang_pairs = self.feeder.get_lang_pairs()
        self.assertGreater(len(lang_pairs), 0)
        self.assertIn("spa_Latn_eng", lang_pairs)
        self.assertIn("eng_spa_Latn", lang_pairs)
        self.assertNotIn("eng_all", lang_pairs)
        self.assertNotIn("all_eng", lang_pairs)

    def test_get_lang_pairs_X_to_eng(self):
        lang_pairs = self.feeder.get_lang_pairs("X_to_eng")
        self.assertIn("spa_Latn_eng", lang_pairs)
        self.assertNotIn("eng_spa_Latn", lang_pairs)

    def test_get_lang_pairs_eng_to_X(self):
        lang_pairs = self.feeder.get_lang_pairs("eng_to_X")
        self.assertIn("eng_spa_Latn", lang_pairs)
        self.assertNotIn("spa_Latn_eng", lang_pairs)
        
if __name__ == "__main__":
    unittest.main()