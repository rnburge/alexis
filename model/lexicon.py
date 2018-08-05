from dawg import CompletionDAWG
import os
import sys


class Lexicon:
    """ Represents the lexicon of allowed words, as a DAWG.
    See <a href = http://en.wikipedia.org/wiki/Directed_acyclic_word_graph>
    Named 'Lexicon' to avoid confusion with Python's inbuilt
    dictionary data structure. """

    def __init__(self):
        """ Create a new lexicon """
        self.word_list = CompletionDAWG()
        self.word_list.load(os.path.join(sys.path[0], 'csw.dawg'))
        self.reverse_list = CompletionDAWG(sorted([word[::-1] for word in self.list_words()]))

    def contains(self, word: str):
        """ Returns True if the supplied word is in the lexicon """
        return word.upper() in self.word_list

    def starts_with(self, prefix: str):
        """ Returns a list of all valid words in the lexicon starting with the supplied prefix """
        return self.word_list.keys(prefix.upper())

    def contains_prefix(self, prefix: str):
        return len(self.starts_with(prefix)) > 1

    def contains_suffix(self, suffix: str):
        # see if the reverse of the suffix is a prefix in the reversed wordlist:
        return len(self.reverse_list.keys(suffix[::-1].upper())) > 1

    def contains_word_or_prefix(self, prefix):
        return len(self.starts_with(prefix)) > 0

    def list_words(self):
        """ Returns a list of all valid words in the lexicon """
        return self.starts_with('')

    def __contains__(self, item):
        return self.contains(item)
