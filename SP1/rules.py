# EPA alphabet,...
BASIC_RULES = {
    'di': 'Di',
    'dí': 'DI',
    'ti': 'Ti',
    'tí': 'TI',
    'ni': 'Ji',
    'ní': 'JI',

    'dě': 'De',
    'tě': 'Te',
    'ně': 'Je',
    'mě': 'mJe',
    'bě': 'bje',
    'pě': 'pje',
    'vě': 'vje',

    'ě': 'je',

    'js': 's',

    # vocals
    'a': 'a',
    'e': 'e',
    'i': 'i',
    'o': 'o',
    'u': 'u',

    'á': 'A',
    'é': 'E',
    'í': 'I',
    'ó': 'O',
    'ú': 'U',
    'ů': 'U',

    'y': 'i',
    'ý': 'I',

    # diphtongs
    'ou': 'y',
    'au': 'Y',
    'eu': 'F',

    'x': 'ks',

    # fricatives
    'f': 'f',
    'v': 'v',
    's': 's',
    'z': 'z',
    'š': 'S',
    'ž': 'Z',
    'ch': 'x',
    'h': 'h',
    'l': 'l',
    'r': 'r',
    'ř': 'R',
    'j': 'j',
    'p': 'p',
    'b': 'b',
    't': 't',
    'd': 'd',
    'ť': 'T',
    'ď': 'D',
    'k': 'k',
    'g': 'g',

    # specialities
    'q': 'kv',
    'w': 'v',

    # nasals
    'm': 'm',
    'n': 'n',
    'ň': 'J',

    # affricates
    'c': 'c',
    'č': 'C',
    'dz': 'w',
    'dž': 'W',


    # interpunction
    '. ': '|$|',
    '.': '|$|',
    '; ': '|$|',
    ';': '|$|',
    ':': '|$|',
    ': ': '|$|',

    ',': '|#',
    ', ': '|#',

    # whitespace
    ' ': '|',

    # glottal stops (if word starts with vocal, we add glottal stop (= !))
    '|a': '|!a',
    '|e': '|!e',
    '|i': '|!i',
    '|o': '|!o',
    '|u': '|!u',

    '|A': '|!A',
    '|E': '|!E',
    '|I': '|!I',
    '|O': '|!O',
    '|U': '|!U',

    # alophone 'ch' in the end of word
    'x|': 'G|',
}

# 'b', 'd', 'ď', 'g', 'v', 'z', 'ž', 'h', 'dz', 'dž', 'ř'
VOICED_CONSONANTS_PAIR = ['b', 'd', 'D', 'g', 'v', 'z', 'Z', 'h', 'w', 'W', 'R']

# 'p', 't', 'ť', 'k', 'f', 's', 'š', 'ch', 'c', 'č', 'ř'
VOICELESS_CONSONANTS_PAIR = ['p', 't', 'T', 'k', 'f', 's', 'S', 'x', 'c', 'C', 'Q']

# 'm', 'n', 'ň', 'l', 'r', 'j'
VOICED_CONSONANTS = ['m', 'n', 'J', 'l', 'r', 'j']

CONSONANTS_ALL = VOICED_CONSONANTS + VOICELESS_CONSONANTS_PAIR + VOICED_CONSONANTS_PAIR

VOWELS = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']

# Conversion VOICED_CONSONANTS_PAIR to VOICELESS_CONSONANTS_PAIR
VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR = {
    'b': 'p',
    'd': 't',
    'D': 'T',
    'g': 'k',
    'v': 'f',
    'z': 's',
    'Z': 'S',
    'h': 'x',
    'w': 'c',
    'W': 'C',
    'R': 'Q',
}

# Conversion VOICELESS_CONSONANTS_PAIR to VOICED_CONSONANTS_PAIR
VOICELESS_CONSONANTS_PAIR_to_VOICED_CONSONANTS_PAIR = {
    'p': 'b',
    't': 'd',
    'T': 'D',
    'k': 'g',
    'f': 'v',
    's': 'z',
    'S': 'Z',
    'x': 'h',
    'c': 'w',
    'C': 'W',
    'Q': 'R',
}