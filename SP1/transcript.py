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

def change_char_between_consonants_2(word, char, consonants, replacement):
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


def change_char_between_consonants(word, char, consonants, replacement):
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


def change_char(word, char, next_chars, replacement):
    char_idx = word.index(char)
    if char_idx < len(word) - 2:
        next_char = word[char_idx + 1]
        if next_char == next_chars[0] or next_char == next_chars[1]:
            word_list = list(word)
            word_list[char_idx] = replacement
            word = "".join(word_list)

    return word


def apply_chain_rule(sentences_list: list):
    res = []
    special_chars = ['#', '!', '$']
    for sentence in sentences_list:
        for i in range(len(sentence)-2, 1, -1): # reversed for cycle
            current_char = sentence[i]
            prev_char = sentence[i + 1]

            if current_char in rules.VOICED_CONSONANTS_PAIR and (prev_char in rules.VOICELESS_CONSONANTS_PAIR or prev_char == '|'):
                if prev_char == '|' and i > 0:
                    char_after_vertical_bar = sentence[i + 2]
                    if char_after_vertical_bar in rules.VOWELS or char_after_vertical_bar in rules.VOICELESS_CONSONANTS_PAIR or char_after_vertical_bar in special_chars or char_after_vertical_bar in rules.VOICED_CONSONANTS:
                        current_char_idx = i
                        new_char = rules.VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR[current_char]
                        sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]
                else:
                    current_char_idx = i
                    new_char = rules.VOICED_CONSONANTS_PAIR_to_VOICELESS_CONSONANTS_PAIR[current_char]
                    sentence = sentence[:current_char_idx] + new_char + sentence[current_char_idx + 1:]

            if current_char in rules.VOICELESS_CONSONANTS_PAIR and (prev_char in rules.VOICED_CONSONANTS_PAIR or prev_char == '|'):
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

        res.append(sentence)

    return res

if __name__ == "__main__":
    #input_filename = "vety_HDS.ortho.txt"
    input_filename = "ukazka_HDS.ortho.txt"
    # input_filename = "test.txt"
    output_filename = "vety_HDS_transcript.txt"

    sentences_list_orig = read_input_file(input_filename)
    basic_rules = rules.BASIC_RULES
    res = apply_basic_rules(sentences_list_orig.copy(), basic_rules)
    res = apply_alophones(res)
    res = apply_chain_rule(res)

    save_output_file(res, output_filename)
    print()


