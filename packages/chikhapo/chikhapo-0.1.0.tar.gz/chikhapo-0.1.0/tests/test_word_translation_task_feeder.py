import unittest
from chikhapo import TaskFeeder

class TestWordTranslationTaskFeeder(unittest.TestCase):
    def setUp(self):
        self.feeder = TaskFeeder("word_translation")

    def test_get_word_translation_data_for_lang_pair_less_than_300_words(self):
        words_translations = self.feeder.get_data_for_lang_pair("aac_eng")
        # self.assertIsInstance(list_of_words, list)
        self.assertIsInstance(words_translations, dict)
        first_word = list(words_translations.keys())[0]
        self.assertIsInstance(first_word, str)
        self.assertIsInstance(words_translations[first_word], list)
        self.assertGreater(len(words_translations), 0)
        self.assertLess(len(words_translations), 300)
        self.assertTrue(all(isinstance(w, str) for w in words_translations))

    def test_get_word_translation_data_for_lang_pair_more_than_300_words_lite_true(self):
        words_translations = self.feeder.get_data_for_lang_pair("aar_eng") # by default is lite set to True
        # self.assertIsInstance(list_of_words, list)
        self.assertIsInstance(words_translations, dict)
        first_word = list(words_translations.keys())[0]
        self.assertIsInstance(first_word, str)
        self.assertIsInstance(words_translations[first_word], list)
        self.assertTrue(len(words_translations) == 300)
        self.assertTrue(all(isinstance(w, str) for w in words_translations))

    def test_get_word_translation_data_for_lang_pair_more_than_300_words_lite_false(self):
        words_translations = self.feeder.get_data_for_lang_pair("aar_eng", lite=False)
        # self.assertIsInstance(list_of_words, list)
        self.assertIsInstance(words_translations, dict)
        first_word = list(words_translations.keys())[0]
        self.assertIsInstance(first_word, str)
        self.assertIsInstance(words_translations[first_word], list)
        self.assertTrue(len(words_translations) >= 300)
        self.assertTrue(all(isinstance(w, str) for w in words_translations))

    def test_get_word_translation_data_for_lang_pair_more_than_300_is_determistically_random(self):
        words_1 = self.feeder.get_data_for_lang_pair("aar_eng")
        words_2 = self.feeder.get_data_for_lang_pair("aar_eng")
        self.assertEqual(words_1, words_2)

    def test_get_word_translation_prompts_for_lang_pair_less_than_300_words(self):
        list_of_prompts = self.feeder.get_prompts_for_lang_pair("aac_eng")
        self.assertIsInstance(list_of_prompts, list)
        self.assertGreater(len(list_of_prompts), 0)
        self.assertLess(len(list_of_prompts), 300)
        self.assertTrue(all(isinstance(w, str) for w in list_of_prompts))

    def test_get_word_tanslation_prompts_for_lang_pair_more_than_300_words_lite_false(self):
        list_of_prompts = self.feeder.get_prompts_for_lang_pair("aar_eng", lite=False)
        self.assertIsInstance(list_of_prompts, list)
        self.assertGreater(len(list_of_prompts), 300)
        self.assertTrue(all(isinstance(w, str) for w in list_of_prompts))

    def test_get_lang_pairs(self):
        lang_pairs = self.feeder.get_lang_pairs()
        self.assertIn("spa_eng", lang_pairs)
        self.assertIn("eng_spa", lang_pairs)
        self.assertNotIn("all_eng", lang_pairs)
        self.assertNotIn("eng_all", lang_pairs)

    def test_get_lang_pairs_X_to_eng(self):
        lang_pairs = self.feeder.get_lang_pairs(DIRECTION="X_to_eng")
        self.assertIn("spa_eng", lang_pairs)
        self.assertNotIn("eng_spa", lang_pairs)
        self.assertEqual(2752, len(lang_pairs))

    def test_get_lang_pairs_eng_to_X(self):
        lang_pairs = self.feeder.get_lang_pairs(DIRECTION="eng_to_X")
        self.assertIn("eng_spa", lang_pairs)
        self.assertNotIn("spa_eng", lang_pairs)
        self.assertEqual(2752, len(lang_pairs))

if __name__ == "__main__":
    unittest.main()
