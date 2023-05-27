import pandas as pd
import spacy
from string import punctuation


def clean_text(string):
    punctuation_minimal = "!(),-.:;?%"
    cyrillic_letters = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "
    allowed_symbols = cyrillic_letters + punctuation_minimal
    getVals = list(filter(lambda x: x in allowed_symbols, string))
    result = "".join(getVals)

    return result

def exclude_empty_vals(list):
    result = [item for item in list if item!=None]
    return result

# def lst_to_str_lemmas(list):
#     result = ''
#     for bigram in list:
#         result += ' '.join([word.lemma_ for word in bigram]) + ', '
#     return result.strip(', ')

def lst_to_str(list):
    result = ''
    for bigram in list:
        result += ' '.join([word.text for word in bigram]) + ', '
    return result.strip(', ')


nlp = spacy.load("ru_core_news_sm") # load Russian language model
flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))

def collect_core(sent):
    doc = nlp(clean_text(sent))
    core_list = []
    dicts = [{'token':token, 'pos':token.pos_, 'text':token.text, 'dep':token.dep_, 'lemma':token.lemma_} for token in doc]
    nsubj_list = [item['token'] for item in dicts if item["dep"] == "nsubj"]
    head_verb_list = []
    for nsubj in nsubj_list:
        core_list.append([nsubj, nsubj.head])
        head_verb_list.append(nsubj.head)

    for core_pair in core_list: # check if there are any conj and cross-check that they are not head for other nsubj
        for v_child in core_pair[1].children:
            if (v_child.dep_=='conj') and v_child not in head_verb_list:
                core_list.append([core_pair[0], v_child])


    for core_pair in core_list:

        for v_child in core_pair[1].children:
            advmod = None
            ccomp = None
            xcomp = None
            if v_child.dep_=='advmod':
                advmod = v_child
            elif v_child.dep_=='ccomp':
                ccomp = v_child
            elif v_child.dep_=='xcomp':
                xcomp = v_child

            if any([advmod,ccomp,xcomp]):
                core_pair[1] = [advmod, core_pair[1], ccomp, xcomp]
                core_pair[1] = [item for item in core_pair[1] if item!=None]
                core_pair[1] = list(flatten(core_pair[1]))


    core_list = [list(flatten(item)) for item in core_list]

    return core_list


def collect_verb_obl_obj(sentence):
    doc = nlp(clean_text(sentence))
    result = []
    dicts = [{'token':token, 'pos':token.pos_, 'text':token.text, 'dep':token.dep_, 'lemma':token.lemma_} for token in doc]
    verbs = [item['token'] for item in dicts if item["pos"] == "VERB"]
    for verb in verbs:
        advmod = None
        for v_ch in verb.children:
            if (v_ch.dep_=='advmod') and (sum(1 for _ in v_ch.children)==0):
                advmod = v_ch
                # print(advmod, verb)
                # result.append([advmod, verb])

        for v_child in verb.children:

            # find obl and case
            if v_child.dep_=='obl':
                case = None
                for g_child in v_child.children:
                    if g_child.dep_=='case':
                        case = g_child
                if case:
                    result.append(exclude_empty_vals([advmod, verb, case, v_child]))
                else:
                    result.append(exclude_empty_vals([advmod, verb, v_child]))

            if v_child.dep_=='obj':
                case = None
                for g_child in v_child.children:
                    if g_child.dep_=='case':
                        case = g_child
                if case:
                    result.append(exclude_empty_vals([advmod, verb, case, v_child]))
                else:
                    result.append(exclude_empty_vals([advmod, verb, v_child]))

            # find obj
            if (v_child.dep_=='xcomp') or (v_child.dep_=='ccomp'):
                for grand_child in v_child.children:
                    obj = None
                    if grand_child.dep_=='obj':
                        obj = grand_child
                        for g_child in v_child.children:
                            if g_child.dep_=='case':
                                case = g_child
                        if obj:
                            result.append(exclude_empty_vals([advmod, verb, obj, v_child]))
                        else:
                            result.append(exclude_empty_vals([advmod, verb, v_child]))


    return result

def collect_appos(sent):
    doc = nlp(clean_text(sent))
    dicts = [{'token':token, 'pos':token.pos_, 'text':token.text, 'dep':token.dep_, 'lemma':token.lemma_} for token in doc]
    appos_list = [item['token'] for item in dicts if item["dep"] == "appos"]
    result = []

    for appos in appos_list:
        flat_name = None
        for child in appos.children:
            if child.dep_=='flat:name':
                flat_name = child

        if flat_name:
            result.append([appos.head, appos, flat_name])
        else:
            result.append([appos.head, appos])

    return result

def collect_amod(sent):
    doc = nlp(clean_text(sent))
    nouns_phrases = []
    dicts = [{'token':token, 'pos':token.pos_, 'text':token.text, 'dep':token.dep_, 'lemma':token.lemma_} for token in doc]
    nouns = [item['token'] for item in dicts if item["pos"] == "NOUN"]

    for noun in nouns:
        for child in noun.children:
            if child.dep_=='amod':
               nouns_phrases.append([child, noun])

    return nouns_phrases

def collect_nmod(sent):
    doc = nlp(clean_text(sent))
    nouns_phrases = []
    dicts = [{'token':token, 'pos':token.pos_, 'text':token.text, 'dep':token.dep_, 'lemma':token.lemma_} for token in doc]
    nouns_list = [item['token'] for item in dicts if item["pos"] == "NOUN"]

    for noun in nouns_list:
        for child in noun.children:
            if child.dep_=='nmod':

                case = None
                for g_child in child.children:
                    if g_child.dep_=='case':
                        case = g_child

                n_case = None
                for child_ in noun.children:
                    if child.dep_=='case':
                        n_case = child_

                if case and n_case:
                    nouns_phrases.append([n_case, noun, g_child, child])
                elif case and (not(n_case)) :
                    nouns_phrases.append([noun, g_child, child])
                elif (not(case)) and n_case:
                    nouns_phrases.append([n_case, noun, child])
                elif (not(case and n_case)):
                    nouns_phrases.append([noun, child])

    return nouns_phrases

def collect_comp(sent):
    doc = nlp(clean_text(sent))
    nouns_phrases = []
    dicts = [{'token':token, 'pos':token.pos_, 'text':token.text, 'dep':token.dep_, 'lemma':token.lemma_} for token in doc]
    nouns_list = [item['token'] for item in dicts if item["pos"] == "NOUN"]

    for noun in nouns_list:
        for child in noun.children:
            if child.dep_=='compound':
                nouns_phrases.append([noun, child])

    return nouns_phrases

# nlp function returns an object with individual token information,
# linguistic features and relationships


def show_dependency(sent):
    from spacy import displacy
    doc = nlp(sent)

    print ("{:<15} | {:<8} | {:<15} | {:<20}".format('Token','Relation','Head', 'Children'))
    print ("-" * 70)

    for token in doc:
      print ("{:<15} | {:<8} | {:<15} | {:<20}".format(str(token.text), str(token.dep_), str(token.head.text), str([child for child in token.children])))

    # Use displayCy to visualize the dependency
    displacy.render(doc, style='dep', jupyter=True, options={'distance': 70})