import rules


def read_input_file(filename: str):
    sentences_list = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.rstrip()
            sentences_list.append(sentence)
    file.close()

    return sentences_list


def save_output_file(sentences, filename: str):
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
        for phoneme in basic_rules:
            char_transcript = basic_rules[phoneme]
            sentence = sentence.replace(phoneme, char_transcript)

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
                word = change_phoneme(word, 'n', next_phonemes=['k', 'g'], replacement='N')
            if 'm' in word:
                word = change_phoneme(word, 'm', next_phonemes=['v', 'f'], replacement='M')
            # if 'm' in word:
            #     word = change_char_between_consonants(word, 'm', consonants_all, replacement='H')
            if 'r' in word:
                word = change_phoneme_between_consonants(word, 'r', consonants_all, replacement='P')
            if 'l' in word:
                word = change_phoneme_between_consonants(word, 'l', consonants_all, replacement='L')
            if 'R' in word:
                word = change_phoneme_between_consonants_2(word, 'R', consonants_voiceless, replacement='Q')

            words_temp.append(word)

        sentence = '|'.join(words_temp)
        res.append(sentence)

    return res


def change_phoneme_between_consonants_2(word, phoneme, consonants, replacement):
    phoneme_idx = word.index(phoneme)
    if phoneme_idx == len(word) - 1:
        word_list = list(word)
        word_list[phoneme_idx] = replacement
        word = "".join(word_list)

        return word

    if phoneme_idx > 0 and word[phoneme_idx - 1] in consonants:
        word_list = list(word)
        word_list[phoneme_idx] = replacement
        word = "".join(word_list)

        return word

    return word


def change_phoneme_between_consonants(word, phoneme, consonants, replacement):
    phoneme_idx = word.index(phoneme)
    if phoneme_idx == len(word) - 1 and word[phoneme_idx - 1] in consonants:
        word_list = list(word)
        word_list[phoneme_idx] = replacement
        word = "".join(word_list)

        return word

    if phoneme_idx > 0 and word[phoneme_idx - 1] in consonants and word[phoneme_idx + 1] in consonants:
        word_list = list(word)
        word_list[phoneme_idx] = replacement
        word = "".join(word_list)

        return word

    return word


def change_phoneme(word, phoneme, next_phonemes, replacement):
    phoneme_idx = word.index(phoneme)
    if phoneme_idx < len(word) - 2:
        next_phoneme = word[phoneme_idx + 1]
        if next_phoneme == next_phonemes[0] or next_phoneme == next_phonemes[1]:
            word_list = list(word)
            word_list[phoneme_idx] = replacement
            word = "".join(word_list)

    return word


def apply_chain_rules(sentences_list: list):
    res = []
    special_chars = ['#', '!', '$']
    for sentence in sentences_list:
        for i in range(len(sentence)-2, 1, -1):  # reversed for cycle (from the end to the beginning of the sentence)
            current_char = sentence[i]
            prev_char = sentence[i + 1]

            sentence = chain_rule_voiced_consonants(current_char, i, prev_char, sentence, special_chars)
            sentence = chain_rule_voiceless_consonants(current_char, i, prev_char, sentence)

        res.append(sentence)

    return res


def chain_rule_voiceless_consonants(current_char, i, prev_char, sentence):
    if current_char in rules.VOICELESS_CONSONANTS_PAIR and (
            prev_char in rules.VOICED_CONSONANTS_PAIR or prev_char == '|'):
        if prev_char == '|' and i > 0:
            char_after_vertical_bar = sentence[i + 2]
            if char_after_vertical_bar in rules.VOICED_CONSONANTS_PAIR:
                current_char_idx = i
                new_char = rules.VOICELESS_CONSONANTS_PAIR_to_VOICED_CONSONANTS_PAIR[current_char]
                sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
        elif prev_char != 'v':
            current_char_idx = i
            new_char = rules.VOICELESS_CONSONANTS_PAIR_to_VOICED_CONSONANTS_PAIR[current_char]
            sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
    return sentence


def chain_rule_voiced_consonants(current_char, i, prev_char, sentence, special_chars):
    if current_char in rules.VOICED_CONSONANTS_PAIR and (
            prev_char in rules.VOICELESS_CONSONANTS_PAIR or prev_char == '|'):
        if prev_char == '|' and i > 0:
            char_after_vertical_bar = sentence[i + 2]
            if (char_after_vertical_bar in rules.VOWELS or char_after_vertical_bar in rules.VOICELESS_CONSONANTS_PAIR or
                    char_after_vertical_bar in special_chars or char_after_vertical_bar in rules.VOICED_CONSONANTS):
                current_char_idx = i
                new_char = rules.VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR[current_char]
                sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
        else:
            current_char_idx = i
            new_char = rules.VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR[current_char]
            sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
    return sentence
