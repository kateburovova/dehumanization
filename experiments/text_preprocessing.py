import pandas as pd
import spacy
from string import punctuation

punctuation_minimal = "!(),-.:;?%"
cyrillic_letters = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "
allowed_symbols = cyrillic_letters + punctuation_minimal


def clean_text(string, allowed_symbols):
    getVals = list(filter(lambda x: x in allowed_symbols, string))
    result = "".join(getVals)
    return result


def lemmatize_spacy_fast(text):
    nlp = spacy.load('ru_core_news_md', disable=['ner', 'attribute_ruler'])
    doc = nlp(text)
    result = [token.lemma_ for token in doc]

    return result

def preprocess_df(df, lemmatization_func = lemmatize_spacy_fast, allowed_symbols = allowed_symbols):
    df['text_clean'] = df['text'].apply(lambda x: clean_text(x.lower(), allowed_symbols))
    df['text_lemmatized'] = df['text_clean'].apply(lambda x: lemmatization_func(x))
    df=df[df['text_clean']!='']
    df.reset_index(inplace=True)
    return df

