import re
from typing import Tuple
from dataclasses import dataclass

import spacy
from spacy.tokens import Token


Token.set_extension("modifiers", default=[])
Token.set_extension("negated", default=False)


def freezing_level_to_numeric(text) -> int:
    numbers = re.findall("\d{3,4}", text)

    if re.search("above the summits", text, flags=re.IGNORECASE):
        numbers.append(1500)

    if re.search("terrain frozen|terrain widely frozen", text, flags=re.IGNORECASE):
        numbers.extend([0, 100])

    if re.search("thaw slowly setting in", text, flags=re.IGNORECASE):
        numbers.extend([700, 1200])

    if numbers == []:
        print(f"No number found for freezing level: {text}")
        return (1500, 1500)
    else:
        numbers = [int(x) for x in numbers]
        return (min(numbers), max(numbers))


def wind_to_numeric(text) -> (int, int):
    numbers = re.findall("\d+", text)
    if numbers == []:
        return (0, 0)
    else:
        numbers = [int(x) for x in numbers]
        return (min(numbers), max(numbers))


def get_wind_direction(text) -> set:
    text = text.lower()
    keywords_to_direction = {"southerly": "S",
            "southerlies": "S",
            "south": "S",
            "southeasterly": "SE",
            "southeasterlies": "SE",
            "southeast": "SE",
            "easterly": "E",
            "easterlies": "E",
            "east": "E",
            "northeast": "NE",
            "northeasterly": "NE",
            "northeasterlies": "NE",
            "north": "N",
            "northerly": "N",
            "northerlies": "N",
            "northwest": "NW",
            "northwesterly": "NW",
            "northwesterlies": "NW",
            "west": "W",
            "westerly": "W",
            "westerlies": "W",
            "southwest": "SW",
            "southwesterly": "SW",
            "southwesterlies": "SW"}

    dirs = set()

    for k in keywords_to_direction:
        if re.search(r"\b" + k + "(?!ern corries)", text) is not None:
            dirs.add(keywords_to_direction[k])

    return dirs



def cloud_to_numeric(text) -> Tuple[int, int]:
    numbers = re.findall(r"\d+(?=%)", text)
    if numbers == []:
        return (0, 0)
    else:
        numbers = [int(x) for x in numbers]

        if re.search("nil", text):
            numbers.append(0)

        return (min(numbers), max(numbers))


@dataclass
class RainResult:
    term: str
    modifiers: list
    negated: bool


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

nlp = spacy.load("en_core_web_md")

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

def how_wet_to_numeric(text) -> int:
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

    assert len(found_precip_tokens) > 0

    # Get numerical score

    max_score = 0

    print("\n", text)

    for precip_token in found_precip_tokens:
        if precip_token.term == "dry" or \
                (precip_token.term == "rain" and precip_token.negated):
            max_score = 0
        elif precip_token.term == "rain":
            if precip_token.modifiers:
                for mod in precip_token.modifiers:
                    assert mod in quantity_adjs
                    max_score = max(quantity_adjs[mod], max_score)
            else:
                max_score = max(3, max_score)

        print("\t", precip_token, "->", max_score)

    return max_score
            

    

    


def how_snowy_to_numeric(text) -> int:
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

    assert len(found_precip_tokens) > 0

    # Get numerical score

    max_score = 0

    print("\n", text)

    for precip_token in found_precip_tokens:
        if precip_token.term == "dry" or \
                (precip_token.term == "snow" and precip_token.negated):
            max_score = 0
        elif precip_token.term == "snow":
            if precip_token.modifiers:
                for mod in precip_token.modifiers:
                    assert mod in quantity_adjs
                    max_score = max(quantity_adjs[mod], max_score)
            else:
                max_score = max(3, max_score)

        print("\t", precip_token, "->", max_score)

    return max_score

