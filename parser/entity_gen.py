import spacy


class EntityGenerator(object):
    _slots__ = ["text"]

    def __init__(self, text=None):
        self.text = text

    def get(self):
        """
        Return a Json
        """
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.text)
        text = [ent.text for ent in doc.ents]
        entity = [ent.label_ for ent in doc.ents]

        from collections import Counter

        data = Counter(zip(entity))
        unique_entity = list(data.keys())
        unique_entity = [x[0] for x in unique_entity]

        d = {}
        for val in unique_entity:
            d[val] = []

        for key, val in dict(zip(text, entity)).items():
            if val in unique_entity:
                d[val].append(key)
        return d
