import re

def beautify_value(v: str) -> str:
    v = v.replace("_", " ")
    v = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", v)
    v = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", v)

    words = []
    for word in v.split():
        if word.isupper(): words.append(word)
        else: words.append(word.capitalize())
    return " ".join(words)