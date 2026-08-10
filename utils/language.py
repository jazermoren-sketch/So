from lang.ar import TEXTS as ar
from lang.en import TEXTS as en

LANGS = {
    "ar": ar,
    "en": en
}


def get_text(lang, key):

    return LANGS.get(
        lang,
        ar
    ).get(
        key,
        key
    )