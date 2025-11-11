import pycountry
import string


def convert_iso_to_name(lang):
    query = pycountry.languages.get(alpha_3=lang)
    if query:
        lang_name = query.name
        lang_name = lang_name.translate(str.maketrans('', '', string.punctuation))
        return lang_name
    return ""

def get_direction_of_lang_pair(lang_pair):
    if lang_pair.endswith("_eng"):
        return "X_to_eng"
    elif lang_pair.startswith("eng_"):
        return "eng_to_X"
    raise Exception(f"{lang_pair} is invalid as it does not start with eng_ or ends with eng_")

def get_language_from_pair(lang_pair):
    direction = get_direction_of_lang_pair(lang_pair)
    if direction == "X_to_eng":
        return lang_pair[:-4]
    elif direction == "eng_to_X":
        return lang_pair[4:]
    else:
        raise Exception("Invalid DIRECTION")

def get_language_pair(lang, DIRECTION):
    if DIRECTION == "X_to_eng":
        return f"{lang}_eng"
    elif DIRECTION == "eng_to_X":
        return f"eng_{lang}"
    else:
        raise Exception("Improper direction")

# import unicodedata
# def remove_accents(text):
#     return ''.join(
#         c for c in unicodedata.normalize("NFD", text)
#         if not unicodedata.combining(c)
#     )
# def get_sanitized_language_name(iso): # follows HuggingFace conventions
#     text = convert_iso_to_name(iso)
#     text = remove_accents(text)
#     text = text.replace(" ", "")
#     text = re.sub(r"[^\w.]", "_", text)
#     return text