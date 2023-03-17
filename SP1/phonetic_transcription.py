import rules
from pathlib import Path


def read_input_file(filename: Path):
    sentences_list = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.rstrip()
            sentences_list.append(sentence)
    file.close()

    return sentences_list


def save_output_file(sentences: list, filename: str):
    f = open(filename, 'w', encoding='utf-8')

    for sentence in sentences:
        sentence = sentence + '\n'
        f.write(sentence)

    f.close()


def apply_basic_rules(sentences_list: list, basic_rules: dict):
    res = []
    for sentence in sentences_list:
        pause = '|$|'
        sentence = pause + sentence.lower()
        for char in basic_rules:
            char_transcript = basic_rules[char]
            sentence = sentence.replace(char, char_transcript)

        res.append(sentence)

    return res


def apply_alophones(sentences_list: list):
    # alophones = ['n', 'm', 'R', 'r', 'l']
    consonants_all = rules.CONSONANTS_ALL
    consonants_voiceless = rules.VOICELESS_CONSONANTS_PAIR
    res = []

    for sentence in sentences_list:
        words = sentence.split('|')
        words_temp = []
        for word in words:
            if 'n' in word:
                word = change_char(word, 'n', next_chars=['k', 'g'], replacement='N')
            if 'm' in word:
                word = change_char(word, 'm', next_chars=['v', 'f'], replacement='M')
            # if 'm' in word:
            #     word = change_char_between_consonants(word, 'm', consonants_all, replacement='H')
            if 'r' in word:
                word = change_char_between_consonants(word, 'r', consonants_all, replacement='P')
            if 'l' in word:
                word = change_char_between_consonants(word, 'l', consonants_all, replacement='L')
            if 'R' in word:
                word = change_char_between_consonants_2(word, 'R', consonants_voiceless, replacement='Q')

            words_temp.append(word)

        sentence = '|'.join(words_temp)
        res.append(sentence)

    return res


def change_char_between_consonants_2(word: str, char: str, consonants: list, replacement: str):
    char_idx = word.index(char)
    if char_idx == len(word) - 1:
        word_list = list(word)
        word_list[char_idx] = replacement
        word = "".join(word_list)

        return word

    if char_idx > 0 and word[char_idx - 1] in consonants:
        word_list = list(word)
        word_list[char_idx] = replacement
        word = "".join(word_list)

        return word

    return word


def change_char_between_consonants(word: str, char: str, consonants: list, replacement: str):
    char_idx = word.index(char)
    if char_idx == len(word) - 1 and word[char_idx - 1] in consonants:
        word_list = list(word)
        word_list[char_idx] = replacement
        word = "".join(word_list)

        return word

    if char_idx > 0 and word[char_idx - 1] in consonants and word[char_idx + 1] in consonants:
        word_list = list(word)
        word_list[char_idx] = replacement
        word = "".join(word_list)

        return word

    return word


def change_char(word: str, char: str, next_chars: list, replacement: str):
    char_idx = word.index(char)
    if char_idx < len(word) - 2:
        next_phoneme = word[char_idx + 1]
        if next_phoneme in next_chars:
            word_list = list(word)
            word_list[char_idx] = replacement
            word = "".join(word_list)

    return word


def apply_assimilation(sentences_list: list):
    res = []
    special_chars = ['#', '!', '$']
    for sentence in sentences_list:
        words = sentence.split('|')

        for i in range(len(sentence)-2, 1, -1):  # reversed for cycle (from the end to the beginning of the sentence)
            current_char = sentence[i]
            prev_char = sentence[i + 1]

            sentence = assimilation_voiced_consonants(current_char, i, prev_char, sentence, special_chars)
            sentence = assimilation_voiceless_consonants(current_char, i, prev_char, sentence)

        res.append(sentence)

    return res


def assimilation_voiceless_consonants(current_char: str, i: int, prev_char: str, sentence: str):  # assimilation - voiceless consonants
    if current_char in rules.VOICELESS_CONSONANTS_PAIR and (
            prev_char in rules.VOICED_CONSONANTS_PAIR or prev_char == '|'):
        if prev_char == '|' and i > 0:
            char_after_vertical_bar = sentence[i + 2]
            if (char_after_vertical_bar in rules.VOICED_CONSONANTS_PAIR) and char_after_vertical_bar != 'v':
                current_char_idx = i
                new_char = rules.VOICELESS_CONSONANTS_PAIR_to_VOICED_CONSONANTS_PAIR[current_char]
                sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
        elif prev_char != 'v':  # special case
            current_char_idx = i
            new_char = rules.VOICELESS_CONSONANTS_PAIR_to_VOICED_CONSONANTS_PAIR[current_char]
            sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]

    return sentence


def assimilation_voiced_consonants(current_char: str, i: int, prev_char: str, sentence: str, special_chars: list):  # assimilation - voiced consonants
    char_after_vertical_bar = ''
    if current_char in rules.VOICED_CONSONANTS_PAIR and (
            prev_char in rules.VOICELESS_CONSONANTS_PAIR or prev_char == '|'):
        if prev_char == '|' and i > 0:
            char_after_vertical_bar = sentence[i + 2]
            if (char_after_vertical_bar in rules.VOWELS or char_after_vertical_bar in rules.VOICELESS_CONSONANTS_PAIR or
                    char_after_vertical_bar in special_chars or char_after_vertical_bar in rules.UNIQUE_CONSONANTS or char_after_vertical_bar == 'v'):
                current_char_idx = i
                new_char = rules.VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR[current_char]
                sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
        elif char_after_vertical_bar != 'v':
            current_char_idx = i
            new_char = rules.VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR[current_char]
            sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]

    return sentence


def check_prepositions(sentences_list: list):
    res = []
    # 'bez', 'nad', 'ob', 'od', 'pod', 'pQed' monosyllabic prepositions (end with voiced pair consonants)
    # 'k', 's', 'v', 'z' disyllabic prepositions
    prepositions_bad = ['bes', 'nat', '!op', '!ot', 'pot', 'pQet', 'g', 'f', 's']
    dict_prepositions = {
        'bes': 'bez',
        'nat': 'nad',
        '!op': '!ob',
        '!ot': '!od',
        'pot': 'pod',
        'pQet': 'pQed',
        'g': 'k',
        'f': 'v',
        's': 'z',
    }

    for sentence in sentences_list:
        words = sentence.split('|')
        for preposition_bad in prepositions_bad:
            if preposition_bad in words:
                preposition_idx = words.index(preposition_bad)
                if preposition_idx < len(words)-1:
                    word_after_preposition = words[preposition_idx + 1]
                    first_char = word_after_preposition[0]
                    if first_char in rules.UNIQUE_CONSONANTS or first_char == 'v':
                        words[preposition_idx] = dict_prepositions[preposition_bad]

        sentence = '|'.join(words)
        res.append(sentence)

    res = check_s_preposition_personal_pronouns(res)

    return res

def check_s_preposition_personal_pronouns(sentences_list: list):
    res = []
    personal_pronouns = rules.PERSONAL_PRONOUNS
    bad_preposition = 'z'

    for sentence in sentences_list:
        words = sentence.split('|')
        if bad_preposition in words:
            preposition_idx = words.index(bad_preposition)
            if preposition_idx < len(words) - 1:
                word_after_preposition = words[preposition_idx + 1]
                if word_after_preposition in personal_pronouns:
                    words[preposition_idx] = 's'

        sentence = '|'.join(words)
        res.append(sentence)

    return res