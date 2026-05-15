#!/usr/bin/python3

import urllib.parse
from deep_translator import GoogleTranslator


def generate_google_translate_link(text, source_lang="auto", target_lang="en"):
    encoded_text = urllib.parse.quote(text)
    return f"https://translate.google.com/?sl={source_lang}&tl={target_lang}&text={encoded_text}&op=translate"


def translate_text_sync(text, source_lang='auto', target_lang='en'):
    '''
    No respeita \foramtação latex
    '''
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    return translator.translate(text)


'''

text = "Hola, ¿cómo estás?"
translated_text = translate_text_sync(text, dest='en')

print(f"Texto original: {text}")
print(f"Tradução: {translated_text}")

'''

