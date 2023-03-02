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
}