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
            if 'm' in word:
                word = change_char_between_consonants(word, 'm', consonants_all, replacement='H')
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


def apply_chain_rule():
    pass

if __name__ == "__main__":
    #input_filename = "vety_HDS.ortho.txt"
    input_filename = "ukazka_HDS.ortho.txt"
    # input_filename = "test.txt"
    output_filename = "vety_HDS_transcript.txt"

    sentences_list_orig = read_input_file(input_filename)
    basic_rules = rules.BASIC_RULES
    res = apply_basic_rules(sentences_list_orig.copy(), basic_rules)
    res = apply_alophones(res)

    save_output_file(res, output_filename)
    print()


