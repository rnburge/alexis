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
        sll_suffixes = []
        temp_suffixes = self.list_words()
        while temp_suffixes:
            temp_suffixes = list(set([temp_suffixes[i][1:] for i in range(len(temp_suffixes)) if len(temp_suffixes[i]) > 1]))
            sll_suffixes.extend(temp_suffixes)
        sll_suffixes = sorted(list(set(sll_suffixes)))
        self.suffix_list = CompletionDAWG(sll_suffixes)

        self.reverse_list = CompletionDAWG(sorted([word[::-1] for word in self.list_words()]))

    def contains(self, word: str):
        """ Returns True if the supplied word is in the lexicon """
        return word.upper() in self.word_list

    def starts_with(self, prefix: str):
        """ Returns a list of all valid words in the lexicon starting with the supplied prefix """
        return self.word_list.keys(prefix.upper())

    def ends_with(self, suffix: str):
        return self.suffix_list.keys(suffix.upper())

    def contains_prefix(self, prefix: str):
        return len(self.starts_with(prefix.upper())) > 1

    def contains_suffix(self, suffix: str):
        return len(self.ends_with(suffix.upper())) > 1

    def contains_infix(self, infix):
        return len(self.suffix_list.keys(infix.upper())) > 1

    def contains_word_or_prefix(self, prefix):
        return len(self.starts_with(prefix)) > 0

    def words_containing(self, infix: str):
        suffixes_starting_with_infix = self.suffix_list.keys(infix.upper())
        words = []
        [words.extend(self.reverse_list.keys(suffix[::-1])) for suffix in suffixes_starting_with_infix]
        return sorted([word[::-1] for word in words])

    def list_words(self):
        """ Returns a list of all valid words in the lexicon """
        return self.starts_with('')

    def __contains__(self, item):
        return self.contains(item)
