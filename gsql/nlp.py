import spacy
from typing import List, Dict, Any

class NLPProcessor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Model '{model_name}' not found. Please run: python -m spacy download {model_name}")
            raise

    def process(self, text: str) -> List[Dict[str, Any]]:
        doc = self.nlp(text)
        tokens_info = []
        for token in doc:
            tokens_info.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "head": token.head.text,
                "head_i": token.head.i,
                "i": token.i,
                "ent_type": token.ent_type_,
                "is_stop": token.is_stop
            })
        return tokens_info

    def get_noun_chunks(self, text: str) -> List[str]:
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]
