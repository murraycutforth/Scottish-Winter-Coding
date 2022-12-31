import sqlite3
from pprint import pprint
import re
import string
from collections import Counter
from itertools import chain
from pathlib import Path
from dataclasses import dataclass

from src.database_functions import execute_query
from src.utils import database_cache_path

import spacy
from spacy import displacy
from spacy.tokens import Token


Token.set_extension("modifiers", default=[])
Token.set_extension("negated", default=False)


@dataclass
class RainResult:
    term: string
    modifiers: list
    negated: bool


def word_preprocess(word):
    word = word.lower()
    word = word.strip()
    word = word.strip(string.punctuation)
    return word


precip_tokens = {"wet", "dry", "rain", "snow", "snowfall", "rainfall", "precipitation", "hail", "sleet", "drizzle"}


possible_modifiers = {"flurry", "shower", "drizzle"}


quantity_adjs = {
        "risk": 1,
        "rare": 1,
        "drizzle": 2,
        "local": 2,
        "little": 2,
        "light": 2,
        "occasional": 2,
        "occasionally": 2,
        "possible": 2,
        "patchy": 2,
        "isolated": 2,
        "intermittent": 2,
        "unlikely": 2,
        "few": 2,
        "brief": 2,
        "shower": 3,
        "flurry": 3,
        "frequent": 4,
        "common":4,
        "heavy": 4,
        "persistent": 4,
        "widespread": 5,
        "incessant": 5,
        "torrential": 5,
}


synonyms = {"flurry": "snow", 
            "shower": "rain",
            "snowfall": "snow",
            "rainfall": "rain",
            "wet": "rain",
            "precipitation": "rain",
            "hail": "snow",
            "sleet": "rain",
            "drizzle": "rain"}



def main():
    conn = sqlite3.connect(str(database_cache_path()))
    cur = conn.cursor()

    execute_query("SELECT how_wet FROM MWIS", cur)
    all_rain_fc = [x[0].lower() for x in cur.fetchall()]


    words = list(chain.from_iterable(x.split() for x in all_rain_fc))


    nlp = spacy.load("en_core_web_md")

    noun_counts = Counter()
    adj_counts = Counter()
    verb_counts = Counter()

    outdir = Path("dependency_parse/how_wet")
    outdir.mkdir(exist_ok=True, parents=True)

    for text in all_rain_fc:
        doc = nlp(text)

        # Write out svg image of dependecy parse
        #outfile = outdir / ("_".join(re.sub(r"[\W]", "", x.text) for x in doc if re.match(r"\w", x.text)) + ".svg")
        #svg = displacy.render(doc, style="dep", jupyter=False)
        #outfile.open("w").write(svg)

        for token in doc:
            if token.pos_ == "NOUN" or token.pos_ == "PROPN":
                noun_counts[token.lemma_] += 1
            elif token.pos_ == "ADJ":
                adj_counts[token.lemma_] += 1
            elif token.pos_ == "VERB":
                verb_counts[token.lemma_] += 1

    pprint(noun_counts)
    pprint(adj_counts)
    pprint(verb_counts)


    # Encode some rules
    
    def detect_negated_noun(token):
        negated = False

        # Check for "no" determiner attached to this noun
        # e.g. No (DET) rain (NOUN) expected (VERB)
        for child in token.children:
            if child.dep_ == "det":
                if child.text == "no":
                    negated = True

        # Check for a negated nsubj dependency
        # e.g. Rain (NOUN) not (ADVERB) expected (VERB)
        # Note: this assumes the verb is positive, e.g. would break if verb was "unexpected"
        if token.dep_ == "nsubj":
            head = token.head
            if head.pos_ == "VERB":
                for child in head.children:
                    if child.dep_ == "neg":
                        negated = True

        return negated




    def find_noun_modifiers_list(head_token, doc, multiple_precip_tokens: bool):
        """Hardcode the adjectives which we're looking for. Alternative to above.
        """

        modifiers = set()

        if multiple_precip_tokens:
            # Use an overly-sophisticated approach based on parse tree to match modifiers to precip tokens
            for token in doc:
                if token.lemma_ in quantity_adjs.keys():
                    if token.dep_ in {"amod", "advmod", "conj"} and token.head == head_token:
                        modifiers.add(token.lemma_)
                    else:
                        #print(token, token.dep_, token.head, "head token=", head_token, "doc=", doc)
        else:
            # Just look for any modifier and add to token
            for token in doc:
                if token.lemma_ in quantity_adjs.keys():
                    modifiers.add(token.lemma_)

        return list(modifiers)



    def merge_precip_synonyms(found_precip_tokens):
        """This function takes a list of spacy.Token objects, and changes possible modifiers for rain or
        snow (such as shower or flurry) to actual RainResult objects.
        """

        result = []

        for token in found_precip_tokens:

            if token.lemma_.lower() in synonyms:
                new_text = synonyms[token.lemma_.lower()]

                if token.lemma_.lower() in possible_modifiers:
                    new_mod = [token.lemma_]
                else:
                    new_mod = []

                r = RainResult(term=new_text, modifiers=token._.modifiers + new_mod, negated=token._.negated)

                already_present = any(t.term == new_text for t in result)

                if already_present:
                    continue
                else:
                    result.append(r)
            else:
                r = RainResult(term=token.lemma_, modifiers=token._.modifiers, negated=token._.negated)
                result.append(r)

        return result







    for text in all_rain_fc:
        print()
        print(text)

        # Sometimes the forecast text has a main section, followed by extra comments after a semicolon
        # For simplicity just use the first statement
        if ";" in text:
            text = re.match(".*(?=;)", text)[0]

        doc = nlp(text)
        #for token in doc:
        #    print(f"{token.text}, {token.lemma_}, {token.pos_} ({spacy.explain(token.pos_)}), {token.tag_} ({spacy.explain(token.tag_)}), {token.dep_} ({spacy.explain(token.dep_)}) <- {token.head.text}")

        found_precip_tokens = [token for token in doc if token.lemma_.lower() in precip_tokens]

        if not found_precip_tokens:
            found_precip_tokens = [token for token in doc if token.lemma_.lower() in possible_modifiers]

        #print(found_precip_tokens)

        for token in found_precip_tokens:
            token._.modifiers = find_noun_modifiers_list(token, doc, len(found_precip_tokens) > 1)
            token._.negated = detect_negated_noun(token)

        #merge_conjunction_modifiers(found_precip_tokens)

        found_precip_tokens = merge_precip_synonyms(found_precip_tokens)

        for token in found_precip_tokens:
            print(token)

        """TODO: get a numerical score for rain and snow from each token. Then we can refactor into functions to convert rain text into numerical, and then plot on graphs
        - this includes checking for negation, checking for "dry", and taking score from any modifiers and taking max.
        """




            



    # We can see POS tags for each word. But we want to detect negation, so we need to use a grammar 
    # Probably need to switch to using spacy instead, as this has built-in dep parsing

    


main()



#    def merge_conjunction_modifiers(tokens):
#        # e.g. persistant upload rain and snow
#        for token in tokens:
#            if token.dep_ == "conj":
#                token._.modifiers = list(set(token._.modifiers) | set(token.head._.modifiers))
#                token.head._.modifiers = token._.modifiers





#    def find_noun_modifiers(token):
#        """Currently not used...
#        """
#        modifiers = []
#        
#        # First look for other parts of a compound noun
#        # e.g. snow flurries
#        if token.dep_ == "compound":
#            modifiers.append(token.head)
#
#        # e.g. summit snow
#        for child in token.children:
#            if child.dep_ == "compound":
#                modifiers.append(child)
#
#        # Look for a verb or adjective acting on this noun
#        # e.g. rain expected
#        if token.dep_ == "nsubj":
#            if token.head.pos_ in {"VERB", "ADJ"}:
#                modifiers.append(token.head)
#
#        # Also check for case where the noun is the root of the tree
#        # e.g. drizzly rain
#        for child in token.children:
#            if child.dep_ == "amod":
#                modifiers.append(child)
#
#                for child_2 in child.children:
#                    if child_2.dep_ == "compound":
#                        modifiers.append(child_2)
#
#        # e.g. rare if any showers
#        if token.dep_ == "pobj":
#            preposition = token.head
#            if preposition.dep_ == "prep":
#                prep_head = preposition.head
#                if prep_head.pos_ in {"ADJ", "NOUN"}:
#                    modifiers.append(prep_head)
#
#        return modifiers
