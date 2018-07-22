from model.lexicon import Lexicon


def test_init():
    lex = Lexicon()


def test_contains():
    lex = Lexicon()
    assert lex.contains('Cat')
    assert lex.contains('eifwij') == False


def test_starts_with():
    lex = Lexicon()
    assert len(lex.starts_with("abomin")) == 6


def test_contains_prefix():
    lex = Lexicon()
    assert lex.contains_prefix('catas')


def test_contains_word_or_prefix():
    lex = Lexicon()
    assert lex.contains_word_or_prefix('catas')
    assert lex.contains_word_or_prefix('blimp')


def test_list_words():
    lex = Lexicon()
    assert len(lex.list_words()) == 197888


def test_contains():
    lex = Lexicon()
    assert 'CAT' in lex
