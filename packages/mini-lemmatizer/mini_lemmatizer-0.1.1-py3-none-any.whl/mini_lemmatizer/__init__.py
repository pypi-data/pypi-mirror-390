"""
mini_lemmatizer - A simple, lightweight lemmatization utility.
--------------------------------------------------------------
Performs basic lemmatization using NLTK's WordNetLemmatizer.
Handles tokenization and POS-tagging automatically.

Author: Sania Jain
Version: 0.1.1
"""

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# -----------------------------
# Auto-download required data
# -----------------------------
def ensure_nltk_resources():
    """Download required NLTK resources safely (including punkt_tab)."""
    resources = [
        "punkt",
        "punkt_tab",           # Fixes newer NLTK tokenization issue
        "averaged_perceptron_tagger",
        "wordnet",
        "omw-1.4"
    ]
    for r in resources:
        try:
            nltk.data.find(f"tokenizers/{r}") if "punkt" in r else nltk.data.find(f"corpora/{r}")
        except LookupError:
            nltk.download(r, quiet=True)

# Run on import
ensure_nltk_resources()


class MiniLemmatizer:
    """
    A simple lemmatizer class.
    Example:
        >>> lemm = MiniLemmatizer()
        >>> lemm.lemmatize_sentence("The cats are running in the gardens")
        ['The', 'cat', 'be', 'run', 'in', 'the', 'garden']
    """

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def get_wordnet_pos(self, treebank_tag):
        """
        Map POS tag to WordNet POS tag.
        """
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def lemmatize_sentence(self, sentence):
        """
        Lemmatize all tokens in a sentence.
        """
        tokens = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(tokens)
        lemmatized = [
            self.lemmatizer.lemmatize(token, self.get_wordnet_pos(pos))
            for token, pos in pos_tags
        ]
        return lemmatized

    def lemmatize_text(self, text):
        """
        Lemmatize multi-sentence text.
        """
        sentences = nltk.sent_tokenize(text)
        return [" ".join(self.lemmatize_sentence(s)) for s in sentences]


# -----------------------------
# Self-test when run directly
# -----------------------------
if __name__ == "__main__":
    lemm = MiniLemmatizer()
    print(lemm.lemmatize_sentence("The dogs are chasing the cars"))

