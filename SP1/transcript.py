from pathlib import Path
import os

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
        sentence.append('\n')
        sentence_str = ''.join(sentence)
        f.write(sentence_str)

    f.close()

def create_start_end_pauses(sentences_list):
    pass

def apply_basic_rules(sentences_list: list, basic_rules: dict):
    res = []
    for sentence in sentences_list:
        sentence_transcript = ['|$|']
        words_list = sentence.split(" ")
        for word in words_list:
            word = word.lower()
            word_list = list(word)
            for i in range(len(word_list)):
                char = word[i]
                char_EPA = basic_rules[char]
                word_list[i] = char_EPA

            word_str = ''.join(word_list)

            sentence_transcript.append(word_str + "|")

        res.append(sentence_transcript)

    return res

if __name__ == "__main__":
    #input_filename = "vety_HDS.ortho.txt"
    input_filename = "ukazka_HDS.ortho.txt"
    output_filename = "vety_HDS_transcript.txt"

    sentences_list_orig = read_input_file(input_filename)
    basic_rules = rules.BASIC_RULES
    res = apply_basic_rules(sentences_list_orig.copy(), basic_rules)

    save_output_file(res, output_filename)
    print()


